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

# C10/C11 — DOS COSAS DISTINTAS (corregido con Francisco, 2026-11-19):
# 1) NIVELES DE ENTRADA: fibo del impulso (punto cero -> fin de tendencia).
#    De CreceTrader: 50% / 61.8% ('Evento 1') / 100% ('Evento 2') / 125% / 150%.
NIVELES_IMPULSO = (0.50, 0.618, 1.00, 1.25, 1.50)
# 2) RIESGO: decision de capital de Francisco (NO del canal).
#    'En tendencia pongo hasta un 5% de la cuenta.'
RIESGO_MAX_TENDENCIA = 0.05
RIESGO_MAX_CORRECCION = 0.02
# La confianza ya NO se deriva de marcos; la asigna el trader. Default conservador.
CONF_DEFECTO = 0.50


def riesgo_total(confianza: float, correccion: bool = False) -> float:
    """C11: **riesgo = confianza x tope**. Tope 5% tendencia / 2% correccion.
    El tope es de Francisco (su capital); la confianza la asigna el trader."""
    tope = RIESGO_MAX_CORRECCION if correccion else RIESGO_MAX_TENDENCIA
    return round(min(max(float(confianza), 0.0), 1.0) * tope, 4)


def evaluar(marcos_confluentes: int,
            correccion_dentro_de_tendencia: bool = False,
            contradicho: bool = False) -> dict:
    """Devuelve escenario, confianza y riesgo sugerido."""
    if marcos_confluentes <= 0:
        return {'escenario': RECHAZADO, 'confianza': 0.0, 'confianza_base': 0.0,
                'riesgo_sugerido': 0.0, 'marcos_confluentes': marcos_confluentes,
                'stop': 'nada', 'profit': 'nada', 'paper_only': PAPER_ONLY,
                'motivo': 'sin marcos confluentes'}
    conf = CONF_DEFECTO  # no se infiere de marcos; la asigna el trader
    es_corr = bool(correccion_dentro_de_tendencia)
    riesgo = riesgo_total(conf, correccion=es_corr)
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
        'confianza_base': conf,
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
