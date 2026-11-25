#!/usr/bin/env python3
"""TRACKER PAPER — cartera mixta de 6 pares (PAPER_ONLY).

Registra en daily_pilot/datos/tracker_paper.json las señales de las DOS
estrategias validadas:

  · PULLBACK (BTC, THETA, HBAR, ETC): ema13/200, swing5, ret_pos,
    target Fib 1.5, 50% en 1R -> Break-Even.
  · REVERSION (ARB, XRP): caida 12% en 8 velas 4h, stop en el minimo,
    target 30% del retroceso.

Origenes marcados: replay (ventana inicial) / forward (nuevas despues del alta).
Idempotente: merge por (par, timestamp). Lee velas DIRECTO del historico,
nunca via velas() (bug de cache ya corregido).

Uso:
    python3 daily_pilot/scripts/tracker_paper.py
    python3 daily_pilot/scripts/tracker_paper.py --resumen
"""
from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
PILOT = BASE / 'daily_pilot'
sys.path.insert(0, str(PILOT / 'scripts'))

import estrategias_validadas as EV  # noqa: E402

JOURNAL = PILOT / 'datos' / 'tracker_paper.json'
CARTERA = PILOT / 'datos' / 'cartera_mixta.json'
TF = '4h'
LIMITE = 1000
CAPITAL = EV.CAPITAL
RIESGO_USD = round(CAPITAL * EV.RIESGO_PCT, 2)   # 1,05 USD


def _ms_ahora() -> int:
    return int(datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000)


def _ahora_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def _fecha(ts) -> str:
    if not ts:
        return ''
    return datetime.datetime.fromtimestamp(int(ts) / 1000,
                                           datetime.timezone.utc).strftime('%Y-%m-%d %H:%M')


def _leer_json(p: Path):
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except Exception:
        return None


def _escribir_json(p: Path, d: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def _velas_cerradas(par: str):
    """Ultimas LIMITE velas 4h cerradas, leidas del historico directo."""
    v = EV.cargar(par)
    if not v:
        return [], f'sin velas para {par}'
    if v[-1]['ts'] + 4 * 3600 * 1000 > _ms_ahora():
        v = v[:-1]              # ultima vela abierta: fuera
    v = v[-LIMITE:]
    if len(v) < 230:
        return [], f'velas insuficientes ({len(v)} < 230)'
    return v, None


def _replay(v: list, s: dict) -> dict:
    """Replica exacta de EV.simular(salida='half') con detalle de gestion."""
    i, e, st0, tg = s['i'], s['entry'], s['stop'], s['target']
    risk = e - st0
    if risk <= 0:
        return {'estado': 'INVALIDA', 'resultado_R': 0.0, 'R_actual': 0.0,
                'parcial': False, 'be': False, 'stop_actual': st0, 'barras': 0,
                'cierre_ts': None, 'cierre_fecha': None}
    R = (tg - e) / risk
    be_at = s.get('be_at')
    be_trigger = e + be_at * risk if be_at else None
    max_bars = s.get('max_bars', 120)
    st = st0
    be = parcial = False
    realized = 0.0
    estado = 'ABIERTA'
    cierre_ts = None
    barras = 0
    fin = min(i + max_bars, len(v))
    for j in range(i + 1, fin):
        barras = j - i
        hi, lo = v[j]['high'], v[j]['low']
        if be_trigger and not be and hi >= be_trigger:
            be = True
            st = e
        if not parcial and hi >= e + risk:
            parcial = True
            realized += 0.5
        if lo <= st:
            realized += (0.5 * (0.0 if st == e else -1.0) if parcial
                         else (0.0 if st == e else -1.0))
            estado = 'CERRADA_BE' if st == e else 'CERRADA_STOP'
            cierre_ts = v[j]['ts']
            break
        if hi >= tg:
            realized += 0.5 * R if parcial else R
            estado = 'CERRADA_TARGET'
            cierre_ts = v[j]['ts']
            break

    if estado == 'ABIERTA':
        if i + max_bars <= len(v):
            estado = 'CERRADA_TIEMPO'
            cierre_ts = v[fin - 1]['ts']
            R_actual = realized
        else:
            estado = 'EN_BE' if parcial else 'ABIERTA'
            ultimo = v[-1]['close'] if len(v) > i + 1 else e
            resto = 0.5 if parcial else 1.0
            R_actual = realized + resto * (ultimo - e) / risk
    else:
        R_actual = realized

    return {'estado': estado, 'resultado_R': round(realized, 4),
            'R_actual': round(R_actual, 4), 'parcial': parcial, 'be': be,
            'stop_actual': round(st, 8), 'barras': barras,
            'cierre_ts': cierre_ts,
            'cierre_fecha': _fecha(cierre_ts) if cierre_ts else None}


def metricas_ops(ops: list) -> dict:
    cerradas = sorted([o for o in ops
                       if str(o.get('estado') or '').startswith('CERRADA')],
                      key=lambda o: o.get('cierre_ts') or 0)
    abiertas = [o for o in ops
                if not str(o.get('estado') or '').startswith('CERRADA')]
    out = [float(o.get('resultado_R') or 0.0) for o in cerradas]
    if out:
        eq = peak = dd = 0.0
        for o in out:
            eq += o
            peak = max(peak, eq)
            dd = min(dd, eq - peak)
        wins = [o for o in out if o > 0]
        losses = [o for o in out if o <= 0]
        sw, sl = sum(wins), abs(sum(losses))
        m = {'E': round(sum(out) / len(out), 3),
             'acierto': round(100.0 * len(wins) / len(out), 1),
             'total': round(eq, 1), 'dd': round(dd, 1),
             'pf': round(sw / sl, 2) if sl else None}
    else:
        m = {'E': None, 'acierto': None, 'total': 0.0, 'dd': 0.0, 'pf': None}

    fwd = [o for o in ops if o.get('origen') == 'forward']
    fwd_out = [float(o.get('resultado_R') or 0.0) for o in fwd
               if str(o.get('estado') or '').startswith('CERRADA')]
    return {'n': len(ops), 'cerradas': len(cerradas), 'abiertas': len(abiertas),
            'E': m['E'], 'acierto': m['acierto'], 'total': m['total'],
            'dd': m['dd'], 'pf': m['pf'],
            'usd': round(m['total'] * RIESGO_USD, 2),
            'forward_n': len(fwd), 'forward_cerradas': len(fwd_out),
            'forward_E': round(sum(fwd_out) / len(fwd_out), 3) if fwd_out else None}


def actualizar(verbose: bool = False) -> dict:
    """Escanea los 6 pares, registra/actualiza señales y guarda el journal."""
    cartera = _leer_json(CARTERA) or {}
    pares = {p['par']: p for p in cartera.get('pares') or [] if p.get('par')}
    ahora = _ahora_iso()

    j = _leer_json(JOURNAL)
    if not isinstance(j, dict) or not isinstance(j.get('operaciones'), list):
        j = {'version': 2, 'paper_only': True, 'creado': ahora, 'operaciones': []}

    datos, errores = {}, []
    ultima_ts = 0
    for par in pares:
        v, err = _velas_cerradas(par)
        if err:
            errores.append({'par': par, 'error': err})
            continue
        if par in EV.PULLBACK:
            sen = EV.senales_pullback(v, EV.PULLBACK[par])
        elif par in EV.REVERSION:
            sen = EV.senales_reversion(v, EV.REVERSION[par])
        else:
            continue
        datos[par] = (v, sen)
        ultima_ts = max(ultima_ts, v[-1]['ts'])

    if not j.get('desde_ts'):
        j['desde_ts'] = ultima_ts or _ms_ahora()
        j['desde'] = _fecha(j['desde_ts'])
    desde_ts = int(j['desde_ts'])

    ops = j['operaciones']
    idx = {(o.get('par'), int(o.get('senal_ts') or 0)): o for o in ops}
    nuevas = actualizadas = 0
    for par, (v, sen) in datos.items():
        for s in sen:
            ts = v[s['i']]['ts']
            o = idx.get((par, ts))
            if o is None:
                o = {'id': f'{par}-{ts}', 'par': par, 'senal_ts': ts,
                     'senal_fecha': _fecha(ts),
                     'origen': 'forward' if ts > desde_ts else 'replay',
                     'capital_referencia': CAPITAL,
                     'riesgo_pct': round(EV.RIESGO_PCT * 100, 2),
                     'riesgo_usd': RIESGO_USD}
                ops.append(o)
                idx[(par, ts)] = o
                nuevas += 1

            tipo = 'reversion' if par in EV.REVERSION else 'pullback'
            risk = s['entry'] - s['stop']
            sz = EV.size_position(s['entry'], s['stop']) or {}
            o.update({
                'estrategia': tipo,
                'entrada': round(s['entry'], 8),
                'stop_inicial': round(s['stop'], 8),
                'target': round(s['target'], 8),
                'riesgo_unidad': round(risk, 8),
                'R_objetivo': round((s['target'] - s['entry']) / risk, 3)
                if risk > 0 else None,
                'be_trigger': round(s['entry'] + s['be_at'] * risk, 8)
                if s.get('be_at') and risk > 0 else None,
                'unidades': sz.get('unidades'),
                'notional_usd': sz.get('notional'),
                'margen_20x_usd': sz.get('margen_20x'),
            })
            o.update(_replay(v, s))
            o['actualizado'] = ahora
            actualizadas += 1

    ventanas = {par: v[0]['ts'] for par, (v, _sen) in datos.items()}
    antes = len(ops)
    ops[:] = [o for o in ops
              if not (o.get('origen') == 'replay'
                      and o.get('par') in ventanas
                      and int(o.get('senal_ts') or 0) < ventanas[o['par']])]
    podadas = antes - len(ops)
    ops.sort(key=lambda o: (o.get('senal_ts') or 0, o.get('par') or ''))

    j['version'] = 2
    j['generado'] = ahora
    j['estrategia'] = {
        'nombre': (cartera.get('cartera') or {}).get('nombre') or 'cartera mixta',
        'timeframe': TF, 'pares': list(pares),
        'estrategias': cartera.get('estrategias'),
        'capital_referencia': CAPITAL,
        'riesgo_pct': round(EV.RIESGO_PCT * 100, 2), 'riesgo_usd': RIESGO_USD,
    }
    j['fuente_velas'] = list(pares)
    j['errores'] = errores
    j['resumen'] = metricas_ops(ops)
    _escribir_json(JOURNAL, j)

    if verbose:
        _imprimir_resumen(j, nuevas, actualizadas, podadas)
    return j


def _imprimir_resumen(j: dict, nuevas: int = 0, actualizadas: int = 0,
                      podadas: int = 0) -> None:
    r = metricas_ops(j.get('operaciones') or [])
    print(f"TRACKER PAPER · 6 PARES · {r['n']} operaciones "
          f"({r['cerradas']} cerradas, {r['abiertas']} abiertas) · "
          f"+{nuevas} nuevas / {actualizadas} actualizadas / -{podadas} podadas")
    print(f"  E {r['E']}R · acierto {r['acierto']}% · PF {r['pf']} · "
          f"DD {r['dd']}R · total {r['total']}R (${r['usd']:+.2f} a 0,35%)")
    print(f"  forward: {r['forward_n']} ops · "
          f"E {r['forward_E'] if r['forward_E'] is not None else '—'} · "
          f"desde {j.get('desde') or '—'}")
    for par in (j.get('estrategia') or {}).get('pares') or []:
        m = metricas_ops([o for o in j.get('operaciones') or []
                          if o.get('par') == par])
        print(f"  {par:10s} n={m['n']:3d} cerradas={m['cerradas']:3d} "
              f"E={m['E']} win={m['acierto']} PF={m['pf']} DD={m['dd']}")
    for e in j.get('errores') or []:
        print(f"  ERROR {e.get('par')}: {e.get('error')}")
    abiertas = [o for o in j.get('operaciones') or []
                if not str(o.get('estado') or '').startswith('CERRADA')]
    for o in abiertas:
        print(f"  ABIERTA {o['par']} @ {o['entrada']} stop {o['stop_actual']} "
              f"target {o['target']} R_actual {o['R_actual']} ({o['estado']})")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--resumen', action='store_true', help='solo muestra el journal')
    a = ap.parse_args()
    if a.resumen:
        j = _leer_json(JOURNAL)
        if not j:
            print('sin journal: corré primero sin --resumen')
            return 1
        _imprimir_resumen(j)
        return 0
    actualizar(verbose=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
