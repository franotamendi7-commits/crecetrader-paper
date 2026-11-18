#!/usr/bin/env python3
"""Registro de SEGUIMIENTO de escenarios (PAPER_ONLY, E7 parte 2).

Estados canonicos de seguimiento (iguales a los del Dashboard):
  EN_OBSERVACION, ESPERANDO_ACTIVACION, ACTIVADO, EN_SEGUIMIENTO,
  OBJETIVO_ALCANZADO, INVALIDADO, EXPIRADO

NO marca estados solo: el control periodico registra lo que el usuario/analista
confirma. El que ejecuta ordenes no existe (PAPER_ONLY).
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

DIR = Path(__file__).resolve().parent
REG = DIR / 'estados.jsonl'

ESTADOS = ('EN_OBSERVACION', 'ESPERANDO_ACTIVACION', 'ACTIVADO', 'EN_SEGUIMIENTO',
           'OBJETIVO_ALCANZADO', 'INVALIDADO', 'EXPIRADO')
PAPER_ONLY = True


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def registrar(escenario_id: str, estado: str, nota: str = '', precio: float | None = None) -> dict:
    assert estado in ESTADOS, estado
    e = {'fecha': now_iso(), 'escenario_id': escenario_id, 'estado': estado,
         'nota': nota, 'precio': precio, 'paper_only': PAPER_ONLY}
    REG.parent.mkdir(parents=True, exist_ok=True)
    with REG.open('a', encoding='utf-8') as f:
        f.write(json.dumps(e, ensure_ascii=False) + '\n')
    return e


def leer() -> list:
    if not REG.exists():
        return []
    return [json.loads(l) for l in REG.read_text(encoding='utf-8').splitlines() if l.strip()]


def resumen() -> dict:
    reg = leer()
    ult = {}
    for e in reg:
        ult[e['escenario_id']] = e['estado']
    por = {s: 0 for s in ESTADOS}
    for s in ult.values():
        por[s] = por.get(s, 0) + 1
    return {'paper_only': PAPER_ONLY, 'n_registros': len(reg), 'n_escenarios': len(ult),
            'estado_actual': ult, 'por_estado': por, 'fuente': str(REG)}


if __name__ == '__main__':
    print(json.dumps(resumen(), ensure_ascii=False, indent=2))
