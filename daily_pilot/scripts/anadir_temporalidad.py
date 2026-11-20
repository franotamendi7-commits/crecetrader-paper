#!/usr/bin/env python3
"""E6 — Clasificacion de TEMPORALIDAD de cada claim (PAPER_ONLY).

Anade la columna 'temporalidad' a claims (ALTER TABLE idempotente) con:
  semanal | diario | 4h | intradia | neutro
Metodo declarado por regex sobre el texto del claim. No infiere B/C/D.
"""
from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path

# ruta relativa a ESTE archivo (antes era absoluta: hacia que la integracion
# corriendo desde una copia abriera el store VIVO)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'knowledge'))
import store as S

PATRONES = [
    ('semanal', re.compile(r'\b(semanal|semana|semanas|weekly)\b', re.I)),
    ('diario', re.compile(r'\b(diario|diaria|dia|dias|daily)\b', re.I)),
    ('4h', re.compile(r'\b4\s?h\b|\bcuatro horas\b|\b4 horas\b', re.I)),
    ('intradia', re.compile(r'\bintrad[ií]a\b|\bintrad[ií]o\b|\brango\b|\bplazo corto\b', re.I)),
]


def clasificar(texto: str) -> str:
    for nombre, pat in PATRONES:
        if pat.search(texto or ''):
            return nombre
    return 'neutro'


def asegurar_columna(conn: sqlite3.Connection) -> None:
    cols = {r[1] for r in conn.execute('PRAGMA table_info(claims)')}
    if 'temporalidad' not in cols:
        conn.execute("ALTER TABLE claims ADD COLUMN temporalidad TEXT")
        conn.commit()


def main() -> int:
    conn = S.conectar()
    asegurar_columna(conn)
    filas = conn.execute('SELECT id, texto, temporalidad FROM claims').fetchall()
    n = 0
    for cid, texto, actual in filas:
        t = clasificar(texto)
        if actual != t:
            conn.execute('UPDATE claims SET temporalidad=? WHERE id=?', (t, cid))
            n += 1
    conn.commit()
    print(f'actualizados {n} de {len(filas)} claims')
    for nombre, _ in PATRONES + [('neutro', None)]:
        c = conn.execute('SELECT COUNT(*) FROM claims WHERE temporalidad=?', (nombre,)).fetchone()[0]
        print(f'  {nombre}: {c}')
    conn.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
