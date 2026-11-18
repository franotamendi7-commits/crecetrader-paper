#!/usr/bin/env python3
"""Zonas calculadas — C05 (aprobado_en_conversacion, 2026-11-18 (pendiente firma)).

Modelo de Francisco:
  - Una **zona es un NIVEL CALCULADO**, no un soporte/resistencia, ni order block, ni FVG.
  - Se usa **Fibonacci normal**, pero diferenciando **largo / media / corto plazo**:
      * **largo plazo**  -> se detecta en **semanal**
      * **media**        -> se detecta en **diario**
      * **corto**        -> se detecta en **4H**
  - Se detecta una **tendencia** (maximos crecientes / minimos crecientes) y, **cuando cambia a
    minimos menores**, **ahi se tira Fibonacci**.
  - **De un minimo a un maximo** se tira fibo:
      * **Zonas de compra** = retrocesos **50%, 61%, 78%**  (0.50 / 0.618 / 0.786)
      * **Extensiones**     = en la **ruptura del maximo**: **50%, 100%, 150%, 200%**
        de ganancia.

Corpus (vocabulario del canal): "maximos y minimos decrecientes" (muchos claims),
"extension" (2), "si nos ofertan un 50%" (LFHkc5dUoLw), "minimo de julio".
Voces propias del experto: "retroceso" (0), "0.618" (0), "0.786" (0), "fibonacci" (0).

PAPER_ONLY: describe, no ejecuta.
"""
from __future__ import annotations

PAPER_ONLY = True

RETROCESOS = (0.50, 0.618, 0.786)          # 50%, 61%, 78%
EXTENSIONES = (0.50, 1.00, 1.50, 2.00)     # 50%, 100%, 150%, 200% de ganancia

# Marco temporal segun el plazo de la tendencia ( Francisco ).
TF_POR_PLAZO = {'largo': 'semanal', 'media': 'diario', 'corto': '4H'}


def tf_para(plazo: str) -> str:
    return TF_POR_PLAZO.get(plazo, '4H')


def zonas(minimo: float, maximo: float, plazo: str = 'corto',
          direccion: str = 'alcista') -> dict:
    """Zonas de compra (retrocesos) y extensiones (ruptura del maximo).

    En tendencia **bajista** se calcula **al reves**: de maximo a minimo
    (Francisco: "respuesta es si! a la inversa").
    """
    rango = maximo - minimo
    if rango <= 0:
        raise ValueError('maximo debe ser mayor que minimo')
    tf = tf_para(plazo)
    if direccion == 'alcista':
        zonas_compra = {f'{int(r*100)}%': round(maximo - rango * r, 2) for r in RETROCESOS}
        extensiones = {f'{int(e*100)}%': round(maximo + rango * e, 2) for e in EXTENSIONES}
    else:  # bajista: mismo rango, niveles hacia abajo
        zonas_compra = {f'{int(r*100)}%': round(minimo + rango * r, 2) for r in RETROCESOS}
        extensiones = {f'{int(e*100)}%': round(minimo - rango * e, 2) for e in EXTENSIONES}
    return {
        'marco': tf,
        'direccion': direccion,
        'minimo': minimo,
        'maximo': maximo,
        'zonas_compra': zonas_compra,
        'extensiones': extensiones,
        'tipo': 'nivel_calculado',
        'no_es': ['soporte', 'resistencia', 'order_block', 'FVG'],
        'paper_only': PAPER_ONLY,
    }


def cambio_tendencia(maximos_mayores: bool, minimos_menores: bool) -> bool:
    """El cambio de tendencia se detecta cuando pasa de maximos mayores a minimos menores."""
    return (not maximos_mayores) and minimos_menores


if __name__ == '__main__':
    print(zonas(56760.0, 75518.0, 'corto'))
    print(cambio_tendencia(True, False), cambio_tendencia(False, True))
