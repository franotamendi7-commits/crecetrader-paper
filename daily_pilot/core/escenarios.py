#!/usr/bin/env python3
"""Escenarios por confianza — C10 (aprobado por Francisco, 2026-11-18).

Modelo de Francisco:
  - Los escenarios se ordenan por **CONFIANZA EN PORCENTAJE**.
  - **Zona de compra en SEMANAL + DIARIO + 4H** (fibos y precios calculados) -> escenario
    **VALIDADO**, se compra.
  - **4H validado pero CONTRADICHO en semanal y diario** -> **fiabilidad menor**: baja el riesgo,
    pero **se puede tradear intradia**.
  - **Correccion dentro de una tendencia alcista** -> escenario de **CAUTELA**: estamos en
    correccion, pero sabemos que el precio va a ir a buscar esos numeros -> **menos riesgo**.
  - **Si no llega, se protege con stop y luego BV** (break even).
  - **El profit esta donde esta la zona de compra** para seguir subiendo.
  - **A la inversa** en tendencia bajista.

Corpus: "escenario" 332, "plan" 172, "en caso de" 145, "si el precio" 61.
Vocabulario del experto (0 claims): "condicional", "activacion".

PAPER_ONLY: describe, no ejecuta.
"""
from __future__ import annotations

PAPER_ONLY = True

VALIDADO = 'VALIDADO'
MENOR_FIABILIDAD = 'MENOR_FIABILIDAD'
CAUTELA = 'CAUTELA'
RECHAZADO = 'RECHAZADO'

# Confianza segun en cuantos marcos confluye la zona (C10).
CONFIANZA_POR_MARCOS = {3: 1.00, 2: 0.75, 1: 0.50}
RIESGO_MAX = 0.05          # C11: tope 5%


def evaluar(marcos_confluentes: int,
            correccion_dentro_de_tendencia: bool = False,
            contradicho: bool = False) -> dict:
    """Devuelve escenario, confianza y riesgo sugerido."""
    conf = CONFIANZA_POR_MARCOS.get(marcos_confluentes, 0.0)
    if conf == 0.0:
        esc, riesgo, extra = RECHAZADO, 0.0, {}
    elif correccion_dentro_de_tendencia:
        esc, riesgo, extra = CAUTELA, round(RIESGO_MAX * conf, 4), {'nota': 'correccion dentro de tendencia: menos riesgo'}
    elif contradicho:
        esc = MENOR_FIABILIDAD
        riesgo = round(RIESGO_MAX * conf * 0.5, 4)
        extra = {'tradear_intradia': True, 'nota': 'baja el riesgo pero se puede tradear intradia'}
    else:
        esc, riesgo, extra = VALIDADO, round(RIESGO_MAX * conf, 4), {}
    return {
        'escenario': esc,
        'confianza': conf,
        'riesgo_sugerido': riesgo,
        'marcos_confluentes': marcos_confluentes,
        'stop': 'si no llega: stop y luego break even',
        'profit': 'donde esta la zona de compra para seguir subiendo',
        'paper_only': PAPER_ONLY,
        **extra,
    }


if __name__ == '__main__':
    print(evaluar(3))
    print(evaluar(1, contradicho=True))
    print(evaluar(2, correccion_dentro_de_tendencia=True))
    print(evaluar(0))
