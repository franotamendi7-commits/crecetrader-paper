#!/usr/bin/env python3
"""Niveles intradia (C04, Francisco, 2026-11-18).

Modelo de Francisco (NO del corpus — el canal nunca dice "fibonacci"):
  - CreceTrader marca unos **9 niveles** donde el precio puede negociar durante el dia.
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
            hora_ancla: int = HORA_ANCLA, rango: float | None = None) -> dict:
    """Niveles intradia alrededor del **precio de cierre del dia** (punto cero).

    `rango` es la amplitud del abanico: con `rango=None` el abanico es en **unidades**
    (0, +/-0.25 ... +/-1.00) alrededor del cierre; con `rango` expresado en el mismo
    tipo de precio, el abanico es +/- `rango` (p.ej. rango=1% -> +/-1% de abanico).

    **PREGUNTA ABIERTA (H-08)**: la **unidad** de "0.25 / 1.00" no esta definida por
    Francisco. No se inventa: hasta que la defina, el abanico se expresa en unidades.
    """
    base = {'precio_base': round(precio_base, 4), 'hora_ancla': hora_ancla, 'paso': paso,
            'rango': rango, 'unidad': 'unidades (definir: %, $, ATR...)', 'paper_only': PAPER_ONLY}
    if rango is None:
        base['niveles'] = [round(precio_base + paso * i, 4) for i in range(-n, n + 1)]
    else:
        base['niveles'] = [round(precio_base * (1 + paso * i * rango), 4) for i in range(-n, n + 1)]
    base['n_niveles'] = len(base['niveles'])
    base['tipo'] = 'scalping'
    base['confirmacion_4h_o_diario'] = False
    base['se_resetea'] = 'cada dia al precio de la hora ancla'
    return base


def resetear(nuevo_precio: float, **kw) -> dict:
    """Nuevo dia: el punto cero pasa al precio de la hora ancla."""
    return abanico(nuevo_precio, **kw)


if __name__ == '__main__':
    a = abanico(64000.0)
    print(a)
    print('niveles:', len(a['niveles']))
