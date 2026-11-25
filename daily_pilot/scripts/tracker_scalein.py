#!/usr/bin/env python3
"""TRACKER SCALE-IN — cartera de 5 pares validados (PAPER_ONLY).

Registra en daily_pilot/datos/tracker_scalein.json las operaciones del
scale-in Fibonacci con filtro R>=4%, riesgo 2% del capital.

Pares validados (null estricto p=0.00, 6 seeds):
  BTC, ETH, SOL, XRP, ADA

Idempotente: merge por (par, timestamp). Lee velas directo del historico.
"""
from __future__ import annotations
import argparse, datetime, json, sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
PILOT = BASE / 'daily_pilot'
sys.path.insert(0, str(PILOT / 'scripts'))
import scalein_fibo as S  # noqa: E402

JOURNAL = PILOT / 'datos' / 'tracker_scalein.json'
S.RIESGO_TOTAL = 0.02


def ahora_iso():
    return datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')


def fecha(ts):
    return datetime.datetime.utcfromtimestamp(ts / 1000).strftime('%Y-%m-%d %H:%M')


def leer(p):
    try:
        return json.loads(p.read_text()) if p.exists() else None
    except Exception:
        return None


def actualizar(verbose=False):
    j = leer(JOURNAL)
    if not isinstance(j, dict) or not isinstance(j.get('operaciones'), list):
        j = {'version': 1, 'paper_only': True, 'creado': ahora_iso(),
             'operaciones': []}

    ahora = ahora_iso()
    ops = j['operaciones']
    idx = {(o.get('par'), int(o.get('senal_ts') or 0)): o for o in ops}
    nuevas = 0
    for par in S.PARES_VALIDADOS:
        a = S.V / f'{par}_1h.json'
        b = S.V / f'{par}_4h.json'
        if not a.exists() or not b.exists():
            continue
        v1 = json.loads(a.read_text())['velas']
        v4 = json.loads(b.read_text())['velas']
        if v1[-1]['ts'] + 3600 * 1000 > int(datetime.datetime.utcnow().timestamp() * 1000):
            v1 = v1[:-1]
        for o in S.detectar_validados(v1, v4):
            ts = o['ts']
            key = (par, ts)
            if key not in idx:
                rec = {'id': f'{par}-{ts}', 'par': par, 'senal_ts': ts,
                       'senal_fecha': fecha(ts),
                       'origen': 'replay' if not j.get('desde_ts') or ts <= j['desde_ts'] else 'forward'}
                ops.append(rec)
                idx[key] = rec
                nuevas += 1
            rec = idx[key]
            rec.update({'estrategia': 'scalein_fibo', 'legs': o['legs'],
                        'stop': round(o['stop'], 2), 'target': round(o['target'], 2),
                        'R': round(o.get('R', 0), 4),
                        'resultado_usd': round(o['pnl'], 2),
                        'capital': S.CAPITAL, 'riesgo_pct': 2.0,
                        'riesgo_usd': round(S.CAPITAL * 0.02, 2),
                        'actualizado': ahora})

    if not j.get('desde_ts'):
        j['desde_ts'] = max([o['senal_ts'] for o in ops], default=0)
        j['desde'] = fecha(j['desde_ts']) if j['desde_ts'] else ''
    ops.sort(key=lambda o: (o['senal_ts'], o['par']))

    p = [float(o.get('resultado_usd') or 0) for o in ops]
    eq = peak = dd = 0.0
    for x in p:
        eq += x
        peak = max(peak, eq)
        dd = min(dd, eq - peak)
    w = [x for x in p if x > 0]
    j['generado'] = ahora
    j['resumen'] = {'n': len(p), 'win': round(100 * len(w) / len(p), 1) if p else 0,
                    'total_usd': round(eq, 2), 'dd_usd': round(dd, 2),
                    'forward_n': sum(1 for o in ops if o.get('origen') == 'forward')}
    j['config'] = {'filtro': 'R>=4%', 'riesgo_pct': 2.0,
                   'pares': S.PARES_VALIDADOS}
    JOURNAL.write_text(json.dumps(j, indent=2, ensure_ascii=False) + '\n')

    if verbose:
        r = j['resumen']
        print(f"TRACKER SCALE-IN · {r['n']} ops · {r['win']}% win · "
              f"${r['total_usd']:+.2f} · DD ${r['dd_usd']:.2f} · +{nuevas} nuevas · "
              f"forward {r['forward_n']}")
    return j


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--resumen', action='store_true')
    a = ap.parse_args()
    if a.resumen:
        j = leer(JOURNAL)
        print(json.dumps(j.get('resumen') if j else {}, indent=2))
    else:
        actualizar(verbose=True)
