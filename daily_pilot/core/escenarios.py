#!/usr/bin/env python3
"""Escenarios por confianza — C10 (aprobado_en_conversacion, 2026-11-18 (pendiente firma)).

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


def riesgo_total(confianza: float) -> float:
    """C11 (H-07): **riesgo = confianza x 5%**, con tope 5%.
    Unica formula compartida con risk_manager.py."""
    return round(min(max(float(confianza), 0.0), 1.0) * RIESGO_MAX, 4)


def evaluar(marcos_confluentes: int,
            correccion_dentro_de_tendencia: bool = False,
            contradicho: bool = False) -> dict:
    """Devuelve escenario, confianza y riesgo sugerido."""
    conf = CONFIANZA_POR_MARCOS.get(marcos_confluentes, 0.0)
    if contradicho:
        conf *= 0.5            # 4H validado pero contradicho en W/D: confianza a la mitad
    if correccion_dentro_de_tendencia:
        conf *= 0.75           # correccion dentro de tendencia: mas cautela
    riesgo = riesgo_total(conf)
    if conf == 0.0:
        esc, extra = RECHAZADO, {}
    elif correccion_dentro_de_tendencia:
        esc, extra = CAUTELA, {'nota': 'correccion dentro de tendencia: menos riesgo'}
    elif contradicho:
        esc, extra = MENOR_FIABILIDAD, {'tradear_intradia': True, 'nota': 'baja el riesgo pero se puede tradear intradia'}
    else:
        esc, extra = VALIDADO, {}
    return {
        'escenario': esc,
        'confianza': round(conf, 4),
        'confianza_base': CONFIANZA_POR_MARCOS.get(marcos_confluentes, 0.0),
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
