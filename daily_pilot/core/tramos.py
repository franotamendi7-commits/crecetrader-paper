#!/usr/bin/env python3
"""Tramo por timeframe + confluencia (C05, Francisco, 2026-11-20).

Metodo:
  - Cada TF tiene su **propia tendencia** -> su **propio tramo** (minimo -> maximo).
  - Sobre ese tramo: retrocesos 50/61/78 y extensiones 50/100/150/200.
  - Donde coinciden varios TF -> **confluencia** (zona de compra).

PAPER_ONLY: describe y calcula, no ejecuta.
"""
from __future__ import annotations

PAPER_ONLY = True
from zonas import zonas, RETROCESOS, EXTENSIONES, tf_para   # noqa: E402
from regimen import detectar, TENDENCIA_ALCISTA, TENDENCIA_BAJISTA, RANGO  # noqa: E402

PLAZOS = ('largo', 'media', 'corto')


def tramo(velas: list[dict]) -> dict:
    """Minimo y maximo de la tendencia, a partir de velas {high, low}.

    velas: lista ordenada en el tiempo (las mas viejas primero).
    """
    if not velas:
        return {'error': 'sin velas'}
    altos = [v['high'] for v in velas]
    bajos = [v['low'] for v in velas]
    return {'minimo': min(bajos), 'maximo': max(altos),
            'n_velas': len(velas), 'ultimo_cierre': velas[-1].get('close')}


def regimen_de(velas: list[dict]) -> dict:
    """Regimen (C07) a partir de maximos y minimos de los tramos (swing)."""
    if len(velas) < 4:
        return {'regimen': 'NO_DETERMINADO', 'motivo': 'faltan velas'}
    altos = [v['high'] for v in velas]
    bajos = [v['low'] for v in velas]
    # swing: ultimos 3 maximos y minimos relevantes
    maxs = sorted(altos, reverse=True)[:3]
    mins = sorted(bajos)[:3]
    return detectar(maxs, mins)


def calcular(velas: list[dict], plazo: str = 'corto') -> dict:
    """Fibos sobre el tramo de la tendencia en ese plazo."""
    t = tramo(velas)
    if 'error' in t:
        return t
    r = regimen_de(velas)
    z = zonas(t['minimo'], t['maximo'], plazo=plazo)
    return {'tramo': t, 'regimen': r, 'zonas': z, 'tf': tf_para(plazo)}


def confluencia(por_plazo: dict, tolerancia_pct: float = 0.005) -> list[dict]:
    """Niveles donde coinciden 2+ plazos (misma zona).

    tolerancia: 0.005 = 0,5% de tolerancia en el precio.
    """
    bolsas = []
    for plazo, res in (por_plazo or {}).items():
        z = (res or {}).get('zonas') or {}
        for lista in ('zonas_compra', 'extensiones'):
            for k, v in (z.get(lista) or {}).items():
                bolsas.append({'plazo': plazo, 'tipo': lista, 'nivel': k, 'precio': float(v)})
    out = []
    for b in bolsas:
        grupo = [o for o in bolsas
                 if abs(o['precio'] - b['precio']) <= max(1.0, abs(b['precio']) * tolerancia_pct)]
        plazos = sorted({g['plazo'] for g in grupo})
        if len(plazos) >= 2:
            out.append({'precio': round(b['precio'], 2), 'plazos': plazos,
                        'n_confluencias': len(plazos), 'detalle': grupo})
    # dedup por precio cercano
    out.sort(key=lambda x: -x['n_confluencias'])
    seen, limpia = [], []
    for o in out:
   	    if any(abs(o['precio'] - s) <= 1.0 for s in seen):
   	        continue
   	    seen.append(o['precio']); limpia.append(o)
    return limpia


if __name__ == '__main__':
    # validacion con las 3 capturas de BNB (2026-11-20)
    semanal = [{'high': 1371.90, 'low': 537.21, 'close': 533.82}] * 20
    diario = [{'high': 808.24, 'low': 537.81, 'close': 534.82}] * 20
    h4 = [{'high': 809.57, 'low': 530.54, 'close': 534.68}] * 20
    r = confluencia({'largo': calcular(semanal, 'largo'),
                     'media': calcular(diario, 'media'),
                     'corto': calcular(h4, 'corto')})
    print('confluencias BNB:', [(x['precio'], x['n_confluencias']) for x in r[:8]])
