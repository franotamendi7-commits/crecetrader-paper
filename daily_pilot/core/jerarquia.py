#!/usr/bin/env python3
"""C01 — Jerarquia de tendencia: **W > D > 4H** (Francisco).

La tendencia la determina el **semanal**. El diario y las 4h la **confirman**
(o la corrigen). Sin esa jerarquia, un 4H en contra puede dar unasenal
equivocada.

    W alcista  + D alcista  + 4h alcista  -> LONG a favor de los 3
    W alcista  + D correccion               -> CORRECCION (short temporal)
    W alcista  + D bajista                  -> CORRECCION FUERTE
    W bajista  + D bajista  + 4h bajista   -> SHORT a favor de los 3
    W bajista  + D correccion               -> CORRECCION (long temporal)
    cualquier rango / no determinado        -> NO OPERAR
    4H en contra de W (decisión Francisco 2026-11-23) -> NO OPERAR

PAPER_ONLY: describe, no ejecuta.
"""
from __future__ import annotations

PAPER_ONLY = True

ALCISTA = 'alcista'
BAJISTA = 'bajista'
CORRECCION = 'correccion'
RANGO = 'rango'
NO_DETERMINADO = 'no_determinado'

LONG = 'long'
SHORT = 'short'
NO_OPERAR = 'no_operar'


def determinar(regimen_semanal: str, regimen_diario: str | None = None,
               regimen_4h: str | None = None) -> dict:
    """Direccion segun la jerarquia W > D > 4H.

    Los regimenes pueden ser 'alcista' | 'bajista' | 'correccion' | 'rango'.
    """
    def _n(x):
        s = (x or NO_DETERMINADO).lower()
        return s.replace('tendencia_', '')
    w, d, h = _n(regimen_semanal), _n(regimen_diario), _n(regimen_4h)

    if w in (RANGO, NO_DETERMINADO, ''):
        return {'direccion': NO_OPERAR, 'motivo': f'semanal {w}: no hay tendencia macro',
                'confianza': 0.0}

    # 4H en contra del semanal -> no operar (decision Francisco, 2026-11-23)
    if (w == ALCISTA and h == BAJISTA) or (w == BAJISTA and h == ALCISTA):
        return {'direccion': NO_OPERAR,
                'motivo': f'{w} en W pero {h} en 4H: 4H en contra, no operar',
                'confianza': 0.0}

    correccion_d = d == CORRECCION
    correccion_h = h == CORRECCION

    if w == ALCISTA:
        if d == BAJISTA:
            return {'direccion': CORRECCION, 'motivo': 'W alcista pero D bajista: correccion fuerte',
                    'confianza': 0.25}
        if correccion_d or correccion_h:
            return {'direccion': CORRECCION, 'motivo': 'W alcista con correccion en D/4H',
                    'confianza': 0.5}
        if d in (RANGO, NO_DETERMINADO) or h in (RANGO, NO_DETERMINADO):
            return {'direccion': LONG, 'motivo': 'W alcista; D/4H sin confirmar del todo',
                    'confianza': 0.6}
        return {'direccion': LONG, 'motivo': 'W, D y 4H alcistas: a favor de los 3',
                'confianza': 0.85}

    if w == BAJISTA:
        if d == ALCISTA:
            return {'direccion': CORRECCION, 'motivo': 'W bajista pero D alcista: correccion fuerte',
                    'confianza': 0.25}
        if correccion_d or correccion_h:
            return {'direccion': CORRECCION, 'motivo': 'W bajista con correccion en D/4H',
                    'confianza': 0.5}
        if d in (RANGO, NO_DETERMINADO) or h in (RANGO, NO_DETERMINADO):
            return {'direccion': SHORT, 'motivo': 'W bajista; D/4H sin confirmar del todo',
                    'confianza': 0.6}
        return {'direccion': SHORT, 'motivo': 'W, D y 4H bajistas: a favor de los 3',
                'confianza': 0.85}

    return {'direccion': NO_OPERAR, 'motivo': f'semanal {w}: no operable',
            'confianza': 0.0}


if __name__ == '__main__':
    casos = [
        (ALCISTA, ALCISTA, ALCISTA, LONG),
        (ALCISTA, CORRECCION, ALCISTA, CORRECCION),
        (ALCISTA, BAJISTA, ALCISTA, CORRECCION),
        (BAJISTA, BAJISTA, BAJISTA, SHORT),
        (RANGO, ALCISTA, ALCISTA, NO_OPERAR),
    ]
    for w, d, h, esperado in casos:
        r = determinar(w, d, h)
        ok = 'OK ' if r['direccion'] == esperado else 'FALLO'
        print(f"{ok} W={w:<10} D={d:<10} 4h={h:<10} -> {r['direccion']}")


def sin_semanal(regimen_diario: str = None, regimen_4h: str = None) -> dict:
    """REFERENCIA: la misma jerarquia pero SOLO con diario y 4h.

    No es la regla (C01 manda el semanal). Sirve para ver que pasaria si el
    semanal no estuviera en rango. Se marca como referencia.
    """
    # normalizar: 'TENDENCIA_BAJISTA' -> 'bajista'
    def _n(x):
        s = (x or NO_DETERMINADO).lower()
        return s.replace('tendencia_', '')
    d = _n(regimen_diario)
    h = _n(regimen_4h)
    if d in (RANGO, NO_DETERMINADO, ''):
        return {'direccion': NO_OPERAR, 'confianza': 0.0,
                'motivo': f'D {d}: sin tendencia en diario'}
    if (d == ALCISTA and h == BAJISTA) or (d == BAJISTA and h == ALCISTA):
        return {'direccion': NO_OPERAR, 'confianza': 0.0,
                'motivo': f'D {d} pero 4H {h}: 4H en contra, no operar'}
    correccion = h == CORRECCION
    if d == ALCISTA:
        if correccion:
            return {'direccion': CORRECCION, 'confianza': 0.5, 'motivo': 'D alcista, 4H corrige'}
        if h in (RANGO, NO_DETERMINADO):
            return {'direccion': LONG, 'confianza': 0.6, 'motivo': 'D alcista; 4H sin confirmar'}
        return {'direccion': LONG, 'confianza': 0.85, 'motivo': 'D y 4H alcistas'}
    if d == BAJISTA:
        if correccion:
            return {'direccion': CORRECCION, 'confianza': 0.5, 'motivo': 'D bajista, 4H corrige'}
        if h in (RANGO, NO_DETERMINADO):
            return {'direccion': SHORT, 'confianza': 0.6, 'motivo': 'D bajista; 4H sin confirmar'}
        return {'direccion': SHORT, 'confianza': 0.85, 'motivo': 'D y 4H bajistas'}
    return {'direccion': NO_OPERAR, 'confianza': 0.0, 'motivo': f'D {d}: no operable'}
