#!/usr/bin/env python3
"""Regimen — C07 (aprobado por Francisco, 2026-11-18).

Los 3 regimenes:
  1. **TENDENCIA_ALCISTA**  -> maximos crecientes y minimos crecientes
  2. **TENDENCIA_BAJISTA**  -> maximos decrecientes y minimos decrecientes
  3. **RANGO / REVERSION**   -> ni uno ni otro

La **correccion** es parte de la tendencia (no un regimen aparte).

Confirmacion: el canal dice **"supera y consolida"** (LzPTdClLo_w 00:05:42,
j06_M-fADjM 00:07:49). Sin esa confirmacion, el regimen no esta confirmado.

Corpus: "reversion" 105, "fase" 87, "alcista" 80, "bajista" 64, "correccion" 35,
"tendencia" 13, "rango" 13, "consolida" 14.
Vocabulario del experto (0 claims): "cambio de tendencia", "lateralidad".

PAPER_ONLY: describe, no ejecuta.
"""
from __future__ import annotations

PAPER_ONLY = True

TENDENCIA_ALCISTA = 'TENDENCIA_ALCISTA'
TENDENCIA_BAJISTA = 'TENDENCIA_BAJISTA'
RANGO = 'RANGO'
REVERSION = 'REVERSION'
NO_DETERMINADO = 'NO_DETERMINADO'


def _creciente(xs: list) -> bool:
    return all(b > a for a, b in zip(xs, xs[1:]))


def _decreciente(xs: list) -> bool:
    return all(b < a for a, b in zip(xs, xs[1:]))


def detectar(maximos: list, minimos: list) -> dict:
    """Regimen segun maximos y minimos (deber ser series ordenadas en el tiempo)."""
    if len(maximos) < 2 or len(minimos) < 2:
        return {'regimen': NO_DETERMINADO, 'motivo': 'faltan maximos/minimos'}
    mc, mnc = _creciente(maximos), _creciente(minimos)
    md, mnd = _decreciente(maximos), _decreciente(minimos)
    if mc and mnc:
        r, motivo = TENDENCIA_ALCISTA, 'maximos y minimos crecientes'
    elif md and mnd:
        r, motivo = TENDENCIA_BAJISTA, 'maximos y minimos decrecientes'
    else:
        r, motivo = RANGO, 'ni maximos ni minimos confirman tendencia'
    return {'regimen': r, 'motivo': motivo, 'paper_only': PAPER_ONLY}


def es_cambio(regimen_previo: str, regimen_actual: str) -> bool:
    """Una reversión es el cambio de un regimen de tendencia al otro."""
    par = {TENDENCIA_ALCISTA, TENDENCIA_BAJISTA}
    return regimen_previo in par and regimen_actual in par and regimen_previo != regimen_actual


def supera_y_consolida(precio: float, nivel: float, tolerancia: float = 0.0) -> bool:
    """El canal confirma con 'supera y consolida' el nivel."""
    return precio > nivel + tolerancia


if __name__ == '__main__':
    print(detectar([10, 20, 30], [5, 15, 25]))
    print(detectar([30, 20, 10], [25, 15, 5]))
    print(detectar([10, 30, 20], [5, 25, 15]))
    print(es_cambio('TENDENCIA_ALCISTA', 'TENDENCIA_BAJISTA'))
    print(supera_y_consolida(79.0, 78.746, 0.01))
