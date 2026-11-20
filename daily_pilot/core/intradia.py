#!/usr/bin/env python3
"""Niveles intradia (C04, Francisco, 2026-11-18; unidad resuelta 2026-11-20).

Modelo de Francisco (NO del corpus — el canal nunca dice "fibonacci"):
  - Cada dia a las **21:00** (00 UTC, cierre diario) se fija el **PUNTO CERO**:
    el precio de cierre del dia. A las 21:00 la vela nueva abre en el mismo precio.
  - Desde ese cero se despliegan niveles **para arriba y para abajo** con
    **proporciones de Fibonacci**: 0,236 / 0,382 / 0,618 (y extensiones 0,929 / 1,238).
  - El **ancho es FIJO**: 1.000 puntos por unidad. No depende de velas, ATR ni
    del precio.  (Verificado con la captura de BTC del 2026-11-20:
     cierre 61.910 -> +619 / +383 / +237 y -236 / -383 / -619.)
  - **Se resetea cada dia** al nuevo cierre de las 21:00.
  - **Es para SCALPING**, NO para confirmacion de 4H ni de daily.

PAPER_ONLY: describe, no ejecuta.
"""
from __future__ import annotations

PAPER_ONLY = True

HORA_ANCLA = 21          # 21:00 Argentina = 00:00 UTC = cierre diario
HORA_ANCLA_UTC = 0
ANCHO_UNIDAD = 1000.0    # ancho FIJO por unidad (verificado 2026-11-20)
NIVELES = (0.236, 0.382, 0.618, 0.929, 1.238)   # Fibonacci real
N_DEFAULT = len(NIVELES)                        # 5 a cada lado


def abanico(precio_cierre: float, ancho: float = ANCHO_UNIDAD,
            niveles: tuple = NIVELES) -> dict:
    """Niveles intradia alrededor del **cierre del dia** (punto cero).

    Ancho fijo (1000 puntos por unidad), no depende de velas ni del precio.
    """
    precios = {round(precio_cierre, 2)}
    for n in niveles:
        precios.add(round(precio_cierre + ancho * n, 2))
        precios.add(round(precio_cierre - ancho * n, 2))
    precios = sorted(precios)
    return {
        'punto_cero': round(precio_cierre, 2),
        'hora_ancla': HORA_ANCLA,
        'ancho_unidad': ancho,
        'unidad': 'puntos fijos (1000 por unidad), no porcentaje',
        'proporciones': list(niveles),
        'niveles': precios,
        'n_niveles': len(precios),
        'tipo': 'scalping',
        'confirmacion_4h_o_diario': False,
        'se_resetea': 'cada dia al cierre de las 21:00',
        'paper_only': PAPER_ONLY,
    }


def resetear(nuevo_cierre: float, **kw) -> dict:
    """Nuevo dia: nuevo punto cero."""
    return abanico(nuevo_cierre, **kw)


if __name__ == '__main__':
    r = abanico(61910.0)
    print('punto cero:', r['punto_cero'], '| ancho:', r['ancho_unidad'])
    for p in r['niveles']:
        print(f'  {p:>9,.0f}  ({p - 61910:+,.0f})')
