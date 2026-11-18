#!/usr/bin/env python3
"""Niveles intradia (C04, Francisco, 2026-11-18).

Modelo de Francisco (NO del corpus — el canal nunca dice "fibonacci"):
  - CreceTrader marca unos **7 niveles** donde el precio puede negociar durante el dia.
  - Se ancla al **punto cero** = el precio a la hora de inicio de la sesion
    (en el caso de Francisco: las **21:00**).
  - Tira un abanico de Fibonacci **distinto al clasico**: de **0 a +/-1**, con
    escala de **0.25**: 0, +/-0.25, +/-0.50, +/-0.75, +/-1.00 (**9 niveles**).
  - **Se resetea cada dia** al precio de la hora ancla.
  - **Es para SCALPING**, NO para confirmacion de 4H ni de daily:
    es una forma de ver donde puede estar el precio durante la sesion.

PAPER_ONLY: describe, no ejecuta.
"""
from __future__ import annotations

PAPER_ONLY = True

HORA_ANCLA = 21          # 21:00 Argentina = 00:00 UTC = cierre diario ( Francisco )
HORA_ANCLA_UTC = 0       # el punto cero es el cierre del dia (00 UTC)
PASO = 0.25
N_DEFAULT = 4            # n=4 -> 9 niveles (-1.00..+1.00); n=3 -> 7 (hasta +/-0.75)


def abanico(precio_base: float, paso: float = PASO, n: int = N_DEFAULT,
            hora_ancla: int = HORA_ANCLA) -> dict:
    """Devuelve los niveles intradia alrededor del precio base."""
    niveles = [round(precio_base + paso * i, 4) for i in range(-n, n + 1)]
    return {'precio_base': round(precio_base, 4), 'hora_ancla': hora_ancla, 'paso': paso,
            'niveles': niveles, 'n_niveles': len(niveles),
            'tipo': 'scalping', 'confirmacion_4h_o_diario': False,
            'se_resetea': 'cada dia al precio de la hora ancla', 'paper_only': PAPER_ONLY}


def resetear(nuevo_precio: float, **kw) -> dict:
    """Nuevo dia: el punto cero pasa al precio de la hora ancla."""
    return abanico(nuevo_precio, **kw)


if __name__ == '__main__':
    a = abanico(64000.0)
    print(a)
    print('niveles:', len(a['niveles']))
