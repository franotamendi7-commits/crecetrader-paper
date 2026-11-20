#!/usr/bin/env python3
"""Objetivos y toma de ganancias — C09 (aprobado_en_conversacion, 2026-11-18 (pendiente firma)).

Modelo de Francisco:
  - Los objetivos son **siempre los que se calcularon en C05**: las **extensiones**
    50%, 100%, 150% y 200% (sobre el rango minimo->maximo).
  - La **toma de ganancia es PARCIAL**.
  - Las ganancias se **reparten en 25% cada una** (4 tramos = 100%).
  - **Cuando se toma ganancia, se sube el stop loss a break even**.

Corpus: "objetivo" 233 claims, "proyeccion" 108, "primer/segundo/tercer objetivo" 12/8/11.
Ej.: j06_M-fADjM 00:01:03 "lo llevo hasta el primer objetivo, 78.580";
XLgPycsN0ls 00:15:33 "Primer objetivo, 2245. Le falta llegar al segundo".

PAPER_ONLY: describe, no ejecuta.
"""
from __future__ import annotations

PAPER_ONLY = True

TRAMOS = 4
PCT_TRAMO = 0.25
# Extensiones de C05 (sobre el rango minimo->maximo).
EXTENSIONES = (0.50, 1.00, 1.25, 1.50, 1.75, 2.00, 3.00)


def plan(entrada: float, minimo: float, maximo: float, direccion: str = 'alcista') -> dict:
    """Objetivos (extensiones de C05) + toma parcial 25% + stop a break even."""
    rango = maximo - minimo
    if rango <= 0:
        raise ValueError('maximo debe ser mayor que minimo')
    if direccion == 'alcista':
        objetivos = [round(minimo + rango * e, 2) for e in EXTENSIONES]
    else:
        objetivos = [round(maximo - rango * e, 2) for e in EXTENSIONES]
    # Los 7 objetivos son las extensiones de C05 (anexo C05-A, validado por
    # Francisco el 2026-11-20). La firma de 2026-11-19 decia "4 tramos 25%"
    # porque C05 tenia 4 extensiones. Con 7 objetivos, el 100% se reparte
    # en partes iguales: si fueran 4 daria 25% cada uno.
    # PENDIENTE: Francisco debe re-firmar (ver FIRMA_C01_C12.md).
    n = len(objetivos)
    pct_objetivo = round(1.0 / n, 6) if n else 0.0
    return {
        'entrada': entrada,
        'minimo': minimo,
        'maximo': maximo,
        'objetivos': objetivos,
        'n_objetivos': n,
        'tramos_pct': [pct_objetivo] * n,
        'toma': 'parcial',
        'stop': 'break_even tras el primer objetivo',
        'secuencia': [
            {'objetivo': objetivos[i], 'tramo_pct': pct_objetivo,
             'accion_stop': 'break_even' if i == 0 else 'sin cambio'}
            for i in range(n)
        ],
        'paper_only': PAPER_ONLY,
    }


def proximo(objetivos: list, precio: float) -> dict | None:
    """El siguiente objetivo no alcanzado."""
    for o in objetivos:
        if precio < o:
            return {'objetivo': o, 'distancia_pct': round((o - precio) / precio * 100, 3)}
    return None


if __name__ == '__main__':
    p = plan(64000.0, 56760.0, 75518.0)
    for s in p['secuencia']:
        print(s)
    print('proximo para 80000:', proximo(p['objetivos'], 80000.0))
