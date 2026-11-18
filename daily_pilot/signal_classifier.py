#!/usr/bin/env python3
"""Clasificador obligatorio de niveles/escenarios del YouTube Analyst.

Impide que un nivel mencionado se convierta automaticamente en operacion.

Tipos:
  NIVEL_MENCIONADO      - numero nombrado sin contexto operativo
  ZONA_DE_INTERES       - zona a vigilar / posible area de operacion
  ESCENARIO_CONDICIONAL - operacion sujeta a una condicion explicita
  SENAL_EXPLICITA       - indicacion directa de entrada (unica candidata operativa)
  SIN_OPERACION         - el analista lo niega expresamente
  NO_DETERMINABLE       - falta informacion

Reglas:
  - La negacion explicita prevalece sobre cualquier otro criterio.
  - Sin condicion explicita no hay escenario condicional activable.
  - Solo SENAL_EXPLICITA puede ser candidata operativa.
"""
from __future__ import annotations

import re

TIPOS = ('NIVEL_MENCIONADO', 'ZONA_DE_INTERES', 'ESCENARIO_CONDICIONAL',
         'SENAL_EXPLICITA', 'SIN_OPERACION', 'NO_DETERMINABLE')

NEGACION = re.compile(r'no (es|era|fue|sería|seria) (una )?(señal|senal|compra|venta|operacion)|'
                      r'no (me )?compr|no compro|sin (señal|operacion)|'
                      r'tampoco (es|una) (señal|compra)|no hay (señal|confirmacion)|'
                      r'no es una señal|'
                      r'no (voy|vamos|pienso|quiero|considero|me planteo) a? ?(compr|vend)|'
                      r'no (me )?(importa|interesa) (compr|vend)|'
                      r'ni se me ocurre (compr|vend)|no me planteo (compr|vend)', re.I)
CONDICION = re.compile(r'\b(si|en caso de|siempre que|cuando|podr\w*|escenario|hipotet\w*)\b', re.I)
ZONA = re.compile(r'zona|vigilar|vigil|objetivo|soporte|resistencia|area|horquilla', re.I)
ENTRADA = re.compile(r'\b(compr(ar|o|amos|emos)|vend(er|o|amos|emos)|entr(ar|o|amos)|'
                     r'abr(ir|o) (posicion|compra|venta)|colocar (compra|venta)|'
                     r'orden de compra|orden de venta)\b', re.I)


def clasificar(item: dict) -> dict:
    texto = (item.get('texto') or '').strip()
    nivel = item.get('nivel')
    negacion = bool(item.get('negacion_explicita')) or bool(NEGACION.search(texto))
    condicion = item.get('condicion') or (texto if CONDICION.search(texto) else None)
    entrada = item.get('entrada') or bool(ENTRADA.search(texto))

    if negacion:
        tipo = 'SIN_OPERACION'
        motivo = 'negacion explicita del analista'
    elif entrada:
        tipo = 'SENAL_EXPLICITA'
        motivo = 'indicacion explicita de entrada'
    elif condicion:
        tipo = 'ESCENARIO_CONDICIONAL'
        motivo = f'condicion explicita: {condicion[:80]}'
    elif nivel and ZONA.search(texto or ''):
        tipo = 'ZONA_DE_INTERES'
        motivo = 'mencionado como zona/objetivo a vigilar'
    elif nivel:
        tipo = 'NIVEL_MENCIONADO'
        motivo = 'numero mencionado sin contexto operativo'
    elif texto:
        tipo = 'NO_DETERMINABLE'
        motivo = 'informacion insuficiente'
    else:
        tipo = 'NO_DETERMINABLE'
        motivo = 'sin datos'

    return {
        'nivel': nivel,
        'tipo': tipo,
        'motivo': motivo,
        'es_candidata_operativa': tipo == 'SENAL_EXPLICITA',
        'requiere_condicion': tipo in ('ESCENARIO_CONDICIONAL',),
        'texto': texto[:160],
    }


def clasificar_lista(items: list) -> list:
    return [clasificar(x) for x in items]


if __name__ == '__main__':
    import json
    import sys
    datos = json.load(open(sys.argv[1]))
    print(json.dumps(clasificar_lista(datos), ensure_ascii=False, indent=2))
