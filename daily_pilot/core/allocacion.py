#!/usr/bin/env python3
"""Asignacion de capital — C02 (aprobado por Francisco, 2026-11-18).

Modelo:
  - Zona de OFERTA (descuento): se compra el 30% del tramo de capital.
  - Zona de CONFIRMACION (cambio de tendencia): se completa el 70% restante,
    en 2 tramos iguales del 35% cada uno.

Restricciones:
  - Solo los 5 pares del proyecto se compran en OFERTA.
  - Cualquier otro activo: solo en tendencia.
  - SPX: se compra en TENDENCIA (no en oferta), tope 10% de la cartera.
  - BTC: tope 30-45% de la cartera.

PAPER_ONLY: no ejecuta ordenes.
"""
from __future__ import annotations

PAPER_ONLY = True

# Solo estos instrumentos admiten compra en oferta/descuento (C02, Francisco).
OFERTA_UNIVERSE = {'BTCUSD', 'ETHUSD', 'SPX', 'QQQ', 'XAUUSD'}
# Corrección de Francisco (2026-11-18): LAS CINCO se compran en oferta. El resto, no.
OFERTA_EXCLUIDOS = set()

GASTO_OFERTA_PCT = 0.30
GASTO_CONFIRMACION_PCT = 0.70
TRAMOS_CONFIRMACION = 2

# Asignacion maxima por activo (fraccion de la cartera total): (en oferta, en tendencia).
ALLOCATION_MAX = {
    'BTCUSD': (0.30, 0.45),
    'SPX': (0.10, 0.10),
    'ETHUSD': (0.10, 0.20),
    'QQQ': (0.05, 0.10),
    'XAUUSD': (0.05, 0.10),
}


def oferta_permitida(instrumento: str) -> bool:
    return instrumento in OFERTA_UNIVERSE and instrumento not in OFERTA_EXCLUIDOS


def allocacion_maxima(instrumento: str, en_tendencia: bool = True) -> float:
    """Tope de asignacion segun el tipo de operacion."""
    rango = ALLOCATION_MAX.get(instrumento)
    if not rango:
        return 0.0          # activo fuera del universo: no se compra
    return rango[1] if en_tendencia else rango[0]


def distribuir(capital: float, tipo: str = 'mixto') -> list:
    """Reparte el capital segun el modelo 30/35/35."""
    out = []
    if tipo in ('mixto', 'oferta'):
        out.append({'tramo': 1, 'zona': 'oferta', 'porcentaje': GASTO_OFERTA_PCT,
                    'monto': round(capital * GASTO_OFERTA_PCT, 2)})
    if tipo in ('mixto', 'confirmacion'):
        p = round(GASTO_CONFIRMACION_PCT / TRAMOS_CONFIRMACION, 4)
        for i in range(TRAMOS_CONFIRMACION):
            out.append({'tramo': i + 1, 'zona': 'confirmacion', 'porcentaje': p,
                        'monto': round(capital * p, 2)})
    return out


def plan(instrumento: str, capital: float, en_oferta: bool = True) -> dict:
    """Plan de asignacion para un instrumento y un capital dado."""
    permitido = oferta_permitida(instrumento)
    tipo = 'mixto' if (en_oferta and permitido) else 'confirmacion'
    # En mixto/confirmacion el tope es el de tendencia (45% BTC); en oferta pura, 30%.
    maximo = allocacion_maxima(instrumento, en_tendencia=(tipo != 'oferta'))
    tramos = distribuir(min(capital, capital), tipo)
    return {
        'instrumento': instrumento, 'tipo': tipo, 'oferta_permitida': permitido,
        'allocacion_maxima': maximo, 'allocacion_maxima_monto': round(capital * maximo, 2),
        'tramos': tramos, 'paper_only': PAPER_ONLY,
    }


if __name__ == '__main__':
    for inst in ('BTCUSD', 'SPX', 'ADA'):
        print(inst, plan(inst, 1000.0))
