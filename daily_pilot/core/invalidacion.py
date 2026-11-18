#!/usr/bin/env python3
"""Invalidacion — C08 (aprobado por Francisco, 2026-11-18).

Definicion de Francisco:
  > "La invalidacion es cuando **esperamos que un cambio de tendencia suceda y no sucede**.
  >  **Se cierra la posicion** hasta tener en claro un nuevo escenario."

O sea: la invalidacion NO es perder un nivel de precio.
Es la **no ocurrencia del cambio de tendencia que se esperaba** -> el escenario muere,
se cierra la posicion y se **espera** hasta que haya un escenario nuevo claro.

Corpus (vocabulario del canal): "si pierde este nivel..." (42 claims),
"no se ha invalidado el escenario" (6), "caceria de stops" (_Lxz34x7eGg 00:02:31).
El canal nombra la invalidacion como **escenario/proyeccion que deja de valer**, no como stop.

PAPER_ONLY: describe, no ejecuta. PAPER_ONLY=true.
"""
from __future__ import annotations

PAPER_ONLY = True

VIGENTE = 'VIGENTE'
INVALIDADO = 'INVALIDADO'
SIN_CAMBIO_ESPERADO = 'SIN_CAMBIO_ESPERADO'


def evaluar(cambio_de_tendencia_esperado: bool,
            cambio_ocurrido: bool = False,
            escenario_nuevo_claro: bool = False) -> dict:
    """C08: se invalidaba si se esperaba un cambio de tendencia y no ocurrio."""
    if not cambio_de_tendencia_esperado:
        return {'estado': SIN_CAMBIO_ESPERADO, 'accion': 'NADA',
                'motivo': 'no se esperaba cambio de tendencia; no aplica la regla'}
    if cambio_ocurrido:
        return {'estado': VIGENTE, 'accion': 'MANTENER',
                'motivo': 'el cambio de tendencia esperado ocurrio: escenario vigente'}
    return {
        'estado': INVALIDADO,
        'accion': 'CERRAR POSICION',
        'motivo': 'se esperaba un cambio de tendencia y no ocurrio',
        'esperar_nuevo_escenario': not escenario_nuevo_claro,
        'paper_only': PAPER_ONLY,
    }


if __name__ == '__main__':
    print(evaluar(True, False, False))
    print(evaluar(True, True, False))
    print(evaluar(False, False, False))
