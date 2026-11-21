#!/usr/bin/env python3
"""Liquidez institucional — C06 (aprobado_en_conversacion, 2026-11-18 (pendiente firma)).

Modelo de Francisco:
  - **La liquidez es el lugar donde tienen las ordenes los institucionales.**
  - El calculo se hace con la **combinacion de varias cosas**:
      1. **Zonas de fibo** (C05: retrocesos 50/61/78 y extensiones)
      2. **Precios de comienzo de ano** (1 de enero)
      3. **Pools de volumen** (como order block)
  - **Nueva York es mas para el diario**, pero **dentro de la sesion de NY** es donde se
    pueden ir a buscar los **niveles de volumen grande**, donde esta la **liquidez institucional**.

Corpus verificado: "institucional" 52 claims, "Nueva York" 54, "1 de enero" 4
(subONxt5iag 00:09:58 "se preparan desde el 1 de enero"), "dinero institucional"
(0prmrS6nnRk 00:07:25 "si el dinero institucional empieza a entrar ahi").
Vocabulario del experto (0 claims): "pool", "order block".

IMPORTANTE: el "order block" aqui es un **ingrediente del calculo de liquidez**,
NO una zona de trading (C05 lo excluye explicitamente).

PAPER_ONLY: describe, no ejecuta.
"""
from __future__ import annotations

PAPER_ONLY = True

SESION = 'Nueva York'
SESION_APERTURA = '15:30 / 14:30 horario de Londres'   # LFHkc5dUoLw 00:09:36

# Ingredientes del calculo de liquidez ( Francisco ).
COMPONENTES = ('zonas_fibo_c05', 'precios_comienzo_ano', 'pools_volumen_order_block')


def calcular(zonas_fibo: dict | None = None,
             precios_comienzo_ano: list | None = None,
             pools_volumen: list | None = None,
             timeframe: str = None) -> dict:
    """Devuelve los puntos de liquidez institucional y los ingredientes usados.

    C12: el OB / FVG / BOS-CHoCH es **por timeframe** (4H/1H). Sin el TF no se
    puede distinguir la liquidez de 4H de la de 1H.
    """
    usadas = []
    if zonas_fibo:
        usadas.append('zonas_fibo_c05')
    if precios_comienzo_ano:
        usadas.append('precios_comienzo_ano')
    if pools_volumen:
        usadas.append('pools_volumen_order_block')
    candidatos = []
    if zonas_fibo:
        candidatos += list(zonas_fibo.get('zonas_compra', {}).values())
    if precios_comienzo_ano:
        candidatos += list(precios_comienzo_ano)
    if pools_volumen:
        candidatos += list(pools_volumen)
    return {
        'liquidez_institucional': sorted(set(round(float(x), 2) for x in candidatos)),
        'componentes_usados': usadas,
        'n_componentes': len(usadas),
        'timeframe': timeframe,
        'sesion': SESION,
        'nota_sesion': f'dentro de la sesion de {SESION} se buscan los niveles de volumen grande',
        'paper_only': PAPER_ONLY,
    }


def busca_liq(_liquidez: dict, precio: float, tolerancia: float = 0.0) -> list:
    """Niveles de liquidez cercanos a un precio (dentro de la sesion de NY)."""
    return [n for n in _liquidez['liquidez_institucional'] if abs(n - precio) <= tolerancia]


if __name__ == '__main__':
    print(calcular({'zonas_compra': {'50%': 66139.0, '61%': 63925.56}},
                   [60000.0], [69000.0, 71509.0]))
