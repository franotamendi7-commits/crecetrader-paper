#!/usr/bin/env python3
"""TRACKER BOS — break of structure 4h + confirmación 1h (PAPER_ONLY).

Pares validados con 20 seeds (doble verificación, semillas distintas):
  INJ, DOGE, DOT
"""
from __future__ import annotations
import argparse, datetime, json, sys
from pathlib import Path
B = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(B / 'daily_pilot' / 'scripts'))
import test_bos as T  # noqa: E402

D = B / 'daily_pilot' / 'datos'
J = D / 'tracker_bos.json'
PARES = ['INJUSDT', 'DOGEUSDT', 'DOTUSDT', 'USDBRL']


def iso():
    return datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')


def fecha(ts):
    return datetime.datetime.utcfromtimestamp(ts / 1000).strftime('%Y-%m-%d %H:%M')


def actualizar(verbose=False):
    j = json.loads(J.read_text()) if J.exists() else {
        'version': 1, 'paper_only': True, 'creado': iso(), 'operaciones': []}
    ops = j['operaciones']
    idx = {(o['par'], o['senal_ts']): o for o in ops}
    nuevas = 0
    for par in PARES:
        v4, v1 = T.cargar(par, '4h'), T.cargar(par, '1h')
        if not v4 or not v1:
            continue
        for s in T.detectar(v4, v1, 'long'):
            ts = int(v4[s['i4']]['ts'])
            key = (par, ts)
            if key not in idx:
                rec = {'id': f'{par}-{ts}', 'par': par, 'senal_ts': ts,
                       'senal_fecha': fecha(ts),
                       'origen': 'replay' if not j.get('desde_ts') or ts <= j['desde_ts'] else 'forward'}
                ops.append(rec); idx[key] = rec; nuevas += 1
            rr = T.simular(v4, [s])[0]
            idx[key].update({
                'estrategia': 'bos_long', 'entrada': round(s['entry'], 4),
                'stop': round(s['stop'], 4), 'target': round(s['target'], 4),
                'resultado_R': round(rr, 3), 'estado': 'CERRADA_BOS',
                'cierre_fecha': fecha(ts), 'actualizado': iso()})
    if not j.get('desde_ts'):
        j['desde_ts'] = max([o['senal_ts'] for o in ops], default=0)
    ops.sort(key=lambda o: (o['senal_ts'], o['par']))
    r = [float(o.get('resultado_R') or 0) for o in ops]
    eq = peak = dd = 0.0
    for x in r:
        eq += x; peak = max(peak, eq); dd = min(dd, eq - peak)
    j['generado'] = iso()
    j['resumen'] = {'n': len(r), 'win': round(100*sum(1 for x in r if x>0)/len(r),1) if r else 0,
                    'total_R': round(eq,2), 'dd_R': round(dd,2),
                    'forward_n': sum(1 for o in ops if o.get('origen')=='forward')}
    j['config'] = {'estrategia':'BOS 4h+1h long','pares':PARES,'seeds':20}
    J.write_text(json.dumps(j, indent=2, ensure_ascii=False)+'\n')
    if verbose:
        s=j['resumen']
        print(f"BOS · {s['n']} ops · {s['win']}% · {s['total_R']:+.2f}R · "
              f"DD {s['dd_R']:.2f}R · +{nuevas} nuevas · forward {s['forward_n']}")
    return j


if __name__ == '__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--resumen',action='store_true')
    a=ap.parse_args()
    if a.resumen:
        print(json.dumps((json.loads(J.read_text()) if J.exists() else {}).get('resumen',{}),indent=2))
    else:
        actualizar(verbose=True)
