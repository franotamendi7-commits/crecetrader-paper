#!/usr/bin/env python3
"""TRACKER PAPER — seguimiento de la estrategia validada (4 pares, 4h).

Registra en daily_pilot/datos/tracker_paper.json cada señal de la regla
validada:

  · entrada: pullback a EMA13 con retorno de 30 velas positivo
  · stop: swing LOW fijo posterior al cambio de tendencia
  · salida: 50% en 1R -> stop a Break-Even -> resto al target Fib 1.5
  · max_bars: 120 velas 4h

Dos origenes, siempre marcados:
  · replay  : señales de las ultimas 1000 velas 4h al crear el tracker
  · forward : señales nuevas detectadas despues del alta

El estado se recalcula desde las velas en cada corrida: es idempotente y no
duplica operaciones (clave par + timestamp de la señal).

PAPER_ONLY: registra, NUNCA manda ordenes.

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
sys.path.insert(0, str(PILOT / 'core'))
sys.path.insert(0, str(PILOT / 'scripts'))

from velas import velas  # noqa: E402
import estrategia_bull as Z  # noqa: E402
import estrategias_frecuencia as E  # noqa: E402

JOURNAL = PILOT / 'datos' / 'tracker_paper.json'
ESTRATEGIAS = PILOT / 'datos' / 'estrategias_validadas.json'

TF = '4h'
LIMITE = 1000
SALIDA = 'half'
MAX_BARS = 120
CAPITAL = 300.0
RIESGO_PCT = 0.35
RIESGO_USD = round(CAPITAL * RIESGO_PCT / 100.0, 2)      # 1,05 USD

CONFIG = dict(ema_fast=13, ema_trend=200, swing_n=5, regimen='ret_pos',
              fibo_ext=1.5, be_at=1.0, max_bars=MAX_BARS)


# ------------------------------------------------------------------ helpers
def _ms_ahora() -> int:
    return int(datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000)


def _ahora_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def _fecha(ts) -> str:
    if not ts:
        return ''
    return datetime.datetime.fromtimestamp(int(ts) / 1000, datetime.timezone.utc
                                          ).strftime('%Y-%m-%d %H:%M')


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
    """Últimas LIMITE velas 4h cerradas. Devuelve (velas, fuente, error)."""
    r = velas(par, TF, limite=LIMITE)
    if 'error' in r or not r.get('velas'):
        return [], None, r.get('error', 'sin velas')
    v = r['velas']
    # la ultima vela de Binance puede estar abierta: fuera del tracker
    if v[-1]['ts'] + 4 * 3600 * 1000 > _ms_ahora():
        v = v[:-1]
    # ventana de replay: solo las ultimas LIMITE velas cerradas, aunque la
    # cache local tenga el historico completo (el backtest largo vive aparte).
    v = v[-LIMITE:]
    minimo = CONFIG['ema_trend'] + CONFIG['swing_n'] + 120 + 5
    if len(v) < minimo:
        return [], r.get('fuente'), f'velas insuficientes ({len(v)} < {minimo})'
    return v, r.get('fuente', '?'), None


def _replay(v: list, s: dict) -> dict:
    """Replica exacta de estrategia_bull.simular(salida='half'), con detalle.

    El objetivo es que el resultado del tracker sea el mismo que el backtest
    para la misma secuencia de velas. No inventa precios ni gestion nueva.
    """
    i, e, st0 = s['i'], s['entry'], s['stop']
    tg = s['target']
    risk = e - st0
    if risk <= 0:
        return {'estado': 'INVALIDA', 'resultado_R': 0.0, 'R_actual': 0.0,
                'parcial': False, 'be': False, 'stop_actual': st0, 'barras': 0,
                'cierre_ts': None, 'cierre_fecha': None}
    R = (tg - e) / risk
    be_at = s.get('be_at')
    be_trigger = e + be_at * risk if be_at else None
    st = st0
    be = parcial = False
    realized = 0.0
    estado = 'ABIERTA'
    cierre_ts = None
    barras = 0
    fin = min(i + s.get('max_bars', MAX_BARS), len(v))
    for j in range(i + 1, fin):
        barras = j - i
        hi, lo = v[j]['high'], v[j]['low']
        if be_trigger and not be and hi >= be_trigger:
            be = True
            st = e
        if SALIDA == 'half' and not parcial and hi >= e + risk:
            parcial = True
            realized += 0.5
        if lo <= st:
            if parcial:
                realized += 0.5 * (0.0 if st == e else -1.0)
            else:
                realized += (0.0 if st == e else -1.0)
            estado = 'CERRADA_BE' if st == e else 'CERRADA_STOP'
            cierre_ts = v[j]['ts']
            break
        if hi >= tg:
            if parcial:
                realized += 0.5 * R
            else:
                realized += R
            estado = 'CERRADA_TARGET'
            cierre_ts = v[j]['ts']
            break

    if estado == 'ABIERTA':
        if i + s.get('max_bars', MAX_BARS) <= len(v):
            # la simulacion se quedo sin velas: cierra a tiempo (igual que simular)
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

    return {'estado': estado,
            'resultado_R': round(realized, 4),
            'R_actual': round(R_actual, 4),
            'parcial': parcial, 'be': be,
            'stop_actual': round(st, 8),
            'barras': barras,
            'cierre_ts': cierre_ts,
            'cierre_fecha': _fecha(cierre_ts) if cierre_ts else None}


def metricas_ops(ops: list) -> dict:
    """Metricas sobre operaciones CERRADAS (el backtest hace lo mismo)."""
    cerradas = sorted([o for o in ops
                       if str(o.get('estado') or '').startswith('CERRADA')],
                      key=lambda o: o.get('cierre_ts') or 0)
    abiertas = [o for o in ops
                if not str(o.get('estado') or '').startswith('CERRADA')]
    out = [float(o.get('resultado_R') or 0.0) for o in cerradas]
    if out:
        eq = peak = 0.0
        dd = 0.0
        for o in out:
            eq += o
            peak = max(peak, eq)
            dd = min(dd, eq - peak)
        wins = [o for o in out if o > 0]
        losses = [o for o in out if o <= 0]
        sw, sl = sum(wins), abs(sum(losses))
        m = {'E': round(sum(out) / len(out), 3),
             'acierto': round(100.0 * len(wins) / len(out), 1),
             'total': round(eq, 1),
             'dd': round(dd, 1),
             'pf': round(sw / sl, 2) if sl else None}
    else:
        m = {'E': None, 'acierto': None, 'total': 0.0, 'dd': 0.0, 'pf': None}

    fwd = [o for o in ops if o.get('origen') == 'forward']
    fwd_cerradas = [o for o in fwd
                    if str(o.get('estado') or '').startswith('CERRADA')]
    fwd_out = [float(o.get('resultado_R') or 0.0) for o in fwd_cerradas]
    return {'n': len(ops), 'cerradas': len(cerradas), 'abiertas': len(abiertas),
            'E': m['E'], 'acierto': m['acierto'], 'total': m['total'],
            'dd': m['dd'], 'pf': m['pf'],
            'usd': round(m['total'] * RIESGO_USD, 2),
            'forward_n': len(fwd), 'forward_cerradas': len(fwd_cerradas),
            'forward_E': round(sum(fwd_out) / len(fwd_out), 3) if fwd_out else None}


# ------------------------------------------------------------------ tracker
def actualizar(verbose: bool = False) -> dict:
    """Escanea los 4 pares, registra/actualiza señales y guarda el journal."""
    est = _leer_json(ESTRATEGIAS) or {}
    meta = {p.get('par'): p for p in est.get('pares') or [] if p.get('par')}
    ahora = _ahora_iso()

    j = _leer_json(JOURNAL)
    if not isinstance(j, dict) or not isinstance(j.get('operaciones'), list):
        j = {'version': 1, 'paper_only': True, 'creado': ahora,
             'operaciones': []}

    # 1) leer velas y detectar señales
    datos, fuente, errores = {}, {}, []
    ultima_ts = 0
    for par in meta:
        try:
            v, f, err = _velas_cerradas(par)
        except Exception as e:                     # red/parseo: no romper el dash
            v, f, err = [], None, f'{type(e).__name__}: {e}'
        if err:
            errores.append({'par': par, 'error': err})
            continue
        fuente[par] = f
        sen = Z.detectar(v, incluir_ultima=True, **CONFIG)
        datos[par] = (v, sen)
        ultima_ts = max(ultima_ts, v[-1]['ts'])

    # 2) alta del tracker: el forward arranca despues de la ultima vela vista
    if not j.get('desde_ts'):
        j['desde_ts'] = ultima_ts or _ms_ahora()
        j['desde'] = _fecha(j['desde_ts'])
    desde_ts = int(j['desde_ts'])

    # 3) merge por (par, timestamp de la señal) — sin duplicados
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
                     'riesgo_pct': RIESGO_PCT, 'riesgo_usd': RIESGO_USD}
                ops.append(o)
                idx[(par, ts)] = o
                nuevas += 1

            risk = s['entry'] - s['stop']
            sz = E.size_position(RIESGO_USD, s['entry'], s['stop']) or {}
            o.update({
                'entrada': round(s['entry'], 8),
                'stop_inicial': round(s['stop'], 8),
                'target': round(s['target'], 8),
                'riesgo_unidad': round(risk, 8),
                'R_objetivo': round((s['target'] - s['entry']) / risk, 3)
                if risk > 0 else None,
                'be_trigger': round(s['entry'] + CONFIG['be_at'] * risk, 8)
                if CONFIG['be_at'] and risk > 0 else None,
                'unidades': sz.get('unidades'),
                'notional_usd': sz.get('notional'),
                'margen_20x_usd': sz.get('margen_20x'),
            })
            o.update(_replay(v, s))
            o['actualizado'] = ahora
            actualizadas += 1

    # 4) podar replay fuera de la ventana actual (forward se conserva siempre)
    ventanas = {par: v[0]['ts'] for par, (v, _sen) in datos.items()}
    antes = len(ops)
    ops[:] = [o for o in ops
              if not (o.get('origen') == 'replay'
                      and o.get('par') in ventanas
                      and int(o.get('senal_ts') or 0) < ventanas[o['par']])]
    podadas = antes - len(ops)

    ops.sort(key=lambda o: (o.get('senal_ts') or 0, o.get('par') or ''))

    j['generado'] = ahora
    j['estrategia'] = {
        'nombre': (est.get('regla') or {}).get('nombre'),
        'timeframe': TF, 'pares': list(meta),
        'entrada': (est.get('regla') or {}).get('entrada'),
        'stop': (est.get('regla') or {}).get('stop'),
        'salida': (est.get('regla') or {}).get('salida'),
        'parametros': dict(CONFIG, salida=SALIDA),
        'capital_referencia': CAPITAL, 'riesgo_pct': RIESGO_PCT,
        'riesgo_usd': RIESGO_USD,
    }
    j['fuente_velas'] = fuente
    j['errores'] = errores
    j['resumen'] = metricas_ops(ops)
    _escribir_json(JOURNAL, j)

    if verbose:
        _imprimir_resumen(j, nuevas, actualizadas, podadas)
    return j


def _imprimir_resumen(j: dict, nuevas: int = 0, actualizadas: int = 0,
                      podadas: int = 0) -> None:
    r = metricas_ops(j.get('operaciones') or [])
    print(f"TRACKER PAPER · {r['n']} operaciones ({r['cerradas']} cerradas, "
          f"{r['abiertas']} abiertas) · +{nuevas} nuevas / {actualizadas} "
          f"actualizadas / -{podadas} podadas")
    print(f"  E {r['E']}R · acierto {r['acierto']}% · PF {r['pf']} · "
          f"DD {r['dd']}R · total {r['total']}R (${r['usd']:+.2f} a 0,35%)")
    print(f"  forward: {r['forward_n']} ops · "
          f"E {r['forward_E'] if r['forward_E'] is not None else '—'} · "
          f"desde {j.get('desde') or '—'}")
    for par in j.get('estrategia', {}).get('pares') or []:
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
