#!/usr/bin/env python3
"""Confluencia — C03 (aprobado por Francisco, 2026-11-18).

Modelo:
  1. La **fase 3** del canal es la **fase de correccion**.
  2. Para que sea alcista: en **4H** el precio se **recupera** y empieza a hacer
     maximos crecientes (= cambio de estructura).
  3. **Con cambio de fase en 4H + niveles calculados alcanzados** -> se empiezan a
     tomar decisiones de entrada.
  4. **Si el diario lo confirma -> LONG** (se juntan precios calculados y zonas de compra).

PAPER_ONLY: describe, no ejecuta.
"""
from __future__ import annotations

PAPER_ONLY = True

SENALES = ('SIN_SENAL', 'DECISION_ENTRADA', 'LONG')

# C03 (Francisco): secuencia exacta del giro alcista en 4H.
#   1. minimos decrecientes  -> correccion
#   2. rango (consolidacion)
#   3. ruptura del rango con vela verde por ENCIMA de la vela roja
#   4. CAMBIO DE TENDENCIA NO CONFIRMADO (una vela verde)
#   5. dos velas mas -> DOS MAXIMOS CRECIENTES -> CONFIRMADO
ESTADOS = ('CORRECCION', 'RANGO', 'RUPTURA', 'CAMBIO_NO_CONFIRMADO', 'CONFIRMADO')


def secuencia(minimos_decrecientes: bool = False,
              rango: bool = False,
              ruptura: bool = False,
              vela_verde_sobre_roja: bool = False,
              maximos_crecientes: int = 0) -> str:
    """Estado de la secuencia de giro en 4H (C03)."""
    if maximos_crecientes >= 2:
        return 'CONFIRMADO'
    if vela_verde_sobre_roja:
        return 'CAMBIO_NO_CONFIRMADO'
    if ruptura:
        return 'RUPTURA'
    if rango:
        return 'RANGO'
    if minimos_decrecientes:
        return 'CORRECCION'
    return 'SIN_ESTRUCTURA'


def evaluar(cambio_fase_4h: bool = False,
            niveles_calculados_alcanzados: bool = False,
            confirmacion_diaria: bool = False,
            zona_de_compra: bool = False) -> dict:
    """Devuelve la senal y los componentes que la sostienen (trazabilidad)."""
    comp = []
    if cambio_fase_4h:
        comp.append('cambio de fase en 4H')
    if niveles_calculados_alcanzados:
        comp.append('niveles calculados alcanzados')
    if confirmacion_diaria:
        comp.append('confirmacion en diario')
    if zona_de_compra:
        comp.append('zona de compra')

    if cambio_fase_4h and niveles_calculados_alcanzados and confirmacion_diaria and zona_de_compra:
        senal, motivo = 'LONG', '4H cambio de fase + niveles calculados + diario confirma + zona de compra'
    elif cambio_fase_4h and niveles_calculados_alcanzados and confirmacion_diaria:
        senal, motivo = 'DECISION_ENTRADA', 'falta la zona de compra (C10: se juntan precios calculados y zonas)'
    elif cambio_fase_4h and niveles_calculados_alcanzados:
        senal, motivo = 'DECISION_ENTRADA', '4H cambia de fase + niveles calculados (falta confirmacion diaria)'
    else:
        senal, motivo = 'SIN_SENAL', 'no hay cambio de fase en 4H con niveles calculados'
    return {'senal': senal, 'motivo': motivo, 'componentes': comp,
            'paper_only': PAPER_ONLY, 'regla': 'C03 (Francisco)'}


if __name__ == '__main__':
    print(evaluar(True, True, True, True))
    print(evaluar(True, True, False, False))
    print(evaluar(False, False, False, True))
