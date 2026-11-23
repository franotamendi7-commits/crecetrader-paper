#!/usr/bin/env python3
"""AGENTE DE TICKET — «analizá este par en esta temporalidad».

Uso:
    python3 daily_pilot/scripts/agente_ticket.py BTCUSDT --tf 4h
    python3 daily_pilot/scripts/agente_ticket.py AVAXUSDT          # 1D por defecto

Devuelve el analisis completo en el formato del metodo:
    regimen W/D/4H (C07) -> direccion (C01) -> confianza (C10)
    tramo del ciclo (C05-B) -> retrocesos y extensiones (C05)
    niveles concordantes (confluencia temporal)

PAPER_ONLY: analiza, no opera. Sin ordenes.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / 'daily_pilot' / 'core'))

TFs = ('1w', '1d', '4h')
TF_ALIAS = {'1m': '1m', '5m': '5m', '15m': '15m', '1h': '1h', '4h': '4h',
            '1d': '1d', '1w': '1w'}


def _tf_par(tf: str) -> str:
    return {'1w': 'largo', '1d': 'media', '4h': 'corto'}.get(tf, 'media')


def analizar(par: str, tf: str = '1d', n: int = 12, ventana: int = 60,
             plano: bool = False) -> dict:
    """El ticket de un par."""
    from velas import velas
    from tramos import tramo_ciclo, regimen_de
    from jerarquia import determinar, sin_semanal
    from zonas import zonas

    out = {'par': par, 'tf': tf, 'paper_only': True, 'fuente': {}, 'regimen': {}}
    velas_por_tf = {}
    for t in TFs:
        r = velas(par, t, limite=500)
        if 'error' in r:
            out['fuente'][t] = r['error']
            continue
        velas_por_tf[t] = r['velas']
        out['fuente'][t] = r['fuente']
        out['regimen'][t] = regimen_de(r['velas'])['regimen']

    w, d, h = out['regimen'].get('1w'), out['regimen'].get('1d'), out['regimen'].get('4h')
    j = determinar(w, d, h)
    ref = sin_semanal(d, h)
    out['direccion'] = j['direccion']
    out['motivo'] = j['motivo']
    out['confianza'] = j['confianza']
    out['ref_direccion'] = ref['direccion']
    out['ref_confianza'] = ref['confianza']

    # tramo del ciclo del TF pedido
    v = velas_por_tf.get(tf)
    if not v:
        out['error'] = f'sin velas para {tf}'
        return out
    t = tramo_ciclo(v, 3, ventana)
    if 'error' in t:
        out['error'] = t['error']
        return out
    z = zonas(t['minimo'], t['maximo'], plazo=_tf_par(tf))
    out['tramo'] = {'min': round(t['minimo'], 4), 'max': round(t['maximo'], 4)}
    out['retrocesos'] = {k: round(x, 4) for k, x in z['zonas_compra'].items()}
    out['extensiones'] = {k: round(x, 4) for k, x in z['extensiones'].items()}
    # adonde esta el precio ahora dentro del tramo
    precio = v[-1]['close']
    rg = t['maximo'] - t['minimo']
    out['precio_actual'] = round(precio, 4)
    out['posicion_en_tramo_pct'] = round((precio - t['minimo']) / rg * 100, 1) if rg else None
    # proximo nivel clave
    prox = min([x for x in list(out['retrocesos'].values()) + list(out['extensiones'].values())
                if x > precio], default=None)
    out['proximo_nivel'] = round(prox, 4) if prox else None
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('par')
    ap.add_argument('--tf', default='1d')
    ap.add_argument('--n', type=int, default=12)
    ap.add_argument('--ventana', type=int, default=60)
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()

    r = analizar(a.par.upper(), a.tf, a.n, a.ventana)
    if a.json:
        print(json.dumps(r, indent=1, ensure_ascii=False))
        return 0
    print(f"TICKET {r['par']} · {r['tf']}")
    print(f"  regimen W={r['regimen'].get('1w')} D={r['regimen'].get('1d')} 4H={r['regimen'].get('4h')}")
    print(f"  C01 -> {r['direccion']} (confianza {r['confianza']:.0%})  |  {r['motivo']}")
    print(f"  referencia sin semanal: {r['ref_direccion']} ({r['ref_confianza']:.0%})")
    if 'error' in r:
        print('  ERROR:', r['error'])
        return 1
    print(f"  tramo {r['tramo']['min']} -> {r['tramo']['max']} | precio {r['precio_actual']}"
          f" ({r['posicion_en_tramo_pct']}% del tramo)")
    print("  retrocesos:", {k: r['retrocesos'][k] for k in sorted(r['retrocesos'], key=float)})
    print("  extensiones:", {k: r['extensiones'][k] for k in sorted(r['extensiones'], key=float)})
    if r.get('proximo_nivel'):
        print(f"  proximo nivel por encima: {r['proximo_nivel']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
