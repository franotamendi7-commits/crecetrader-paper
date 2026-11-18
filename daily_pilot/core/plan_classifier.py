#!/usr/bin/env python3
"""Clasificador de PLANES DE TRABAJO (modelo CreceTrader, 8 tipos).

No exige orden explicita de compra/venta. Reconoce planes por su contenido.
"""
from __future__ import annotations

import re

CLASIFICACIONES = ('NIVEL_REFERENCIADO', 'ZONA_DE_INTERES', 'ESCENARIO_CONDICIONAL',
                   'PLAN_OPERATIVO_INCOMPLETO', 'PLAN_OPERATIVO_COMPLETO',
                   'OPORTUNIDAD_VALIDABLE', 'NO_OPERABLE', 'DESCARTADO', 'INDETERMINADO')

_NEG = re.compile(r'no (es|era|fue|sería|seria) (una )?(señal|compra|venta|operacion)|'
                 r'no compro|sin (señal|operacion)|no hay confirmacion', re.I)
_COND = re.compile(r'\b(si|en caso de|siempre que|cuando|podr\w*|escenario|hipotet\w*)\b', re.I)
_ZONA = re.compile(r'zona|vigilar|vigil|objetivo|soporte|resistencia|liquidez|horquilla', re.I)
_ENTRADA = re.compile(r'\b(compr\w*|vend\w*|entr\w*|abrir posicion)\b', re.I)
_STOP = re.compile(r'\b(stop|invalidaci\w*|pérdida|perdida|stop loss)\b', re.I)
_OBJETIVO = re.compile(r'\b(objetivo|blanco|meta|proyecci\w*|buscar\w*)\b', re.I)


def clasificar_escenario(e) -> dict:
    """e: Escenario o dict. Devuelve clasificacion + info_faltante."""
    def g(k):
        v = e.get(k) if isinstance(e, dict) else getattr(e, k, None)
        return v or {}
    def gv(k):
        return g(k).get('valor')

    texto = ' '.join([e.get('justificacion', '') if isinstance(e, dict) else e.justificacion or '',
                      ' '.join(e.get('evidencia', []) if isinstance(e, dict) else e.evidencia or [])])
    cond = gv('condicion_activacion')
    entrada = gv('entrada')
    stop = gv('stop')
    objetivos = e.get('objetivos', []) if isinstance(e, dict) else e.objetivos
    nivel = gv('nivel')

    faltante = []
    if _NEG.search(texto):
        return {'clasificacion': 'NIVEL_REFERENCIADO', 'info_faltante': ['el analista lo nego expresamente']}
    if not (nivel or cond or entrada or objetivos):
        return {'clasificacion': 'INDETERMINADO', 'info_faltante': ['sin datos operativos']}

    if cond and entrada is not None and stop is not None and objetivos:
        return {'clasificacion': 'PLAN_OPERATIVO_COMPLETO', 'info_faltante': []}
    if cond and entrada is not None and objetivos:
        return {'clasificacion': 'PLAN_OPERATIVO_INCOMPLETO',
                'info_faltante': ['invalidacion no declarada']}
    if cond and entrada is not None:
        return {'clasificacion': 'PLAN_OPERATIVO_INCOMPLETO',
                'info_faltante': ['objetivos no declarados', 'invalidacion no declarada']}
    if cond:
        return {'clasificacion': 'ESCENARIO_CONDICIONAL',
                'info_faltante': ['entrada no declarada', 'invalidacion no declarada',
                                  'objetivos no declarados']}
    if nivel and _ZONA.search(texto):
        return {'clasificacion': 'ZONA_DE_INTERES', 'info_faltante': ['sin condicion de activacion']}
    if nivel:
        return {'clasificacion': 'NIVEL_REFERENCIADO', 'info_faltante': ['sin informacion operativa']}
    return {'clasificacion': 'INDETERMINADO', 'info_faltante': ['informacion ambigua']}
