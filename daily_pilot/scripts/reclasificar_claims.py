#!/usr/bin/env python3
"""Reclasifica los claims existentes con el clasificador vigente (PAPER_ONLY).

P1-2 FIX: el clasificador se amplió (negaciones «no voy a comprar», «ni se me
ocurre comprar», etc.). Los claims ya guardados quedaron con la clasificación
vieja; este script los actualiza sin tocar el texto ni el nivel.
"""
from __future__ import annotations

import sys
from pathlib import Path

BASE = Path('/Users/franciscootamendi/YouTubeTradingAgent')
sys.path.insert(0, str(BASE / 'daily_pilot'))
sys.path.insert(0, str(BASE / 'daily_pilot' / 'knowledge'))
import store as S
from signal_classifier import clasificar


def main() -> int:
    conn = S.conectar()
    filas = conn.execute('SELECT id, nivel, texto, tipo FROM claims').fetchall()
    cambios = 0
    for cid, nivel, texto, tipo_prev in filas:
        r = clasificar({'nivel': nivel, 'texto': texto or ''})
        if r['tipo'] != tipo_prev:
            conn.execute('UPDATE claims SET tipo=?, motivo=? WHERE id=?',
                         (r['tipo'], r['motivo'], cid))
            cambios += 1
    conn.commit()
    print(f'reclasificados {cambios} de {len(filas)} claims')
    for t, n in conn.execute('SELECT tipo, COUNT(*) FROM claims GROUP BY tipo ORDER BY 2 DESC'):
        print(f'  {t}: {n}')
    conn.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
