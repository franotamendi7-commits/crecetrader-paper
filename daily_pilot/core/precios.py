#!/usr/bin/env python3
"""Parser determinista de precios (C-shared).

Bug que resuelve: '78.580' se convertia en 78,58 y se descartaba (filtro >1000).
Regla: si el numero tiene UN punto y exactamente 3 digitos despues, es separador
de miles (78.580 = 78580). Si tiene coma, tambien miles. Si tiene decimales
reales (2 digitos), se respeta.

Uso: from core.precios import parsear_precio
PAPER_ONLY.
"""
from __future__ import annotations

import re

NUM = re.compile(r'(?<![\d.])(\d{1,3}(?:[.,]\d{3})+(?:[.,]\d+)?)(?![\d])')


def parsear_precio(s: str) -> float | None:
    """'78.580' -> 78580.0 · '65,520' -> 65520.0 · '2.286' -> 2286.0 · '1.780' -> 1780.0"""
    if s is None:
        return None
    t = str(s).strip().replace(' ', '')
    if not t:
        return None
    # miles con punto o coma
    if re.fullmatch(r'\d{1,3}(?:[.,]\d{3})+', t):
        return float(re.sub(r'[.,]', '', t))
    # decimal comun
    try:
        return float(t.replace(',', '.'))
    except ValueError:
        return None


def precios_de_texto(texto: str) -> list[float]:
    """Todos los precios > 1000 que aparecen en un texto."""
    out = []
    for m in NUM.finditer(texto or ''):
        v = parsear_precio(m.group(1))
        if v is not None and v > 1000:
            out.append(v)
    return out


if __name__ == '__main__':
    for s in ('78.580', '75.471', '65,520', '2,286', '1.780', '64.620', '123'):
        print(f'{s:>8} -> {parsear_precio(s)}')
