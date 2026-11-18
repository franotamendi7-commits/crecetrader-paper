#!/usr/bin/env python3
"""P0-4 — Reconciliacion de linaje (READ-ONLY, PAPER_ONLY).

Compara cuatro universos y reporta diferencias. NO escribe nada.
  DB        : daily_pilot/knowledge/store.db (tabla videos)
  registro  : daily_pilot/registro/registro.json
  nocturno  : daily_pilot/nocturno_2026-11-17/<id>/
  data_hist : data_hist/<id>/
"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

BASE = Path('/Users/franciscootamendi/YouTubeTradingAgent')
PILOT = BASE / 'daily_pilot'
PAPER_ONLY = True


def universos() -> dict:
    conn = sqlite3.connect(f"file:{PILOT / 'knowledge' / 'store.db'}?mode=ro", uri=True)
    db = {r[0] for r in conn.execute('SELECT video_id FROM videos')}
    pub = {r[0]: r[1] for r in conn.execute('SELECT video_id, published FROM videos')}
    conn.close()
    reg = set(json.loads((PILOT / 'registro' / 'registro.json').read_text(encoding='utf-8'))['videos'])
    noc = {d.name for d in (PILOT / 'nocturno_2026-11-17').iterdir() if d.is_dir()} \
        if (PILOT / 'nocturno_2026-11-17').exists() else set()
    dh = {d.name for d in (BASE / 'data_hist').iterdir() if d.is_dir()}
    return {'DB': db, 'registro': reg, 'nocturno': noc, 'data_hist': dh, '_pub': pub}


def main() -> int:
    u = universos()
    pub = u.pop('_pub')
    print('=== UNIVERSOS ===')
    for k, v in u.items():
        print(f'  {k}: {len(v)}')

    print('\n=== DIFERENCIAS ===')
    db, reg, noc, dh = u['DB'], u['registro'], u['nocturno'], u['data_hist']
    def show(titulo, s):
        s = sorted(s)
        print(f'  {titulo}: {len(s)}' + (f' -> {s[:8]}' if s else ''))
    show('en DB y no en registro', db - reg)
    show('en registro y no en DB', reg - db)
    show('nocturno fuera de DB', noc - db)
    show('nocturno fuera de registro', noc - reg)
    show('nocturno con transcripcion en data_hist', noc & dh)
    show('en DB sin transcripcion en data_hist', db - dh)
    show('en data_hist sin entrada en DB', dh - db)

    print('\n=== FECHAS INCONSISTENTES (solo published entre fuentes) ===')
    regd = json.loads((PILOT / 'registro' / 'registro.json').read_text(encoding='utf-8'))['videos']
    n = 0
    for vid in sorted(db & reg):
        p_db = pub.get(vid)
        p_reg = (regd.get(vid) or {}).get('published')
        if p_db and p_reg and str(p_db)[:19] != str(p_reg)[:19]:
            n += 1
            print(f'  {vid}: DB.published={p_db} | registro.published={p_reg}')
        elif p_db is None and p_reg:
            n += 1
            print(f'  {vid}: DB.published=NULL | registro.published={p_reg}  (falta en DB)')
    print(f'  total published inconsistente: {n}')

    out = PILOT / 'investigacion' / 'linaje.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({'paper_only': PAPER_ONLY, 'universos': {k: sorted(v) for k, v in u.items()},
                                'resumen': {'DB': len(db), 'registro': len(reg), 'nocturno': len(noc),
                                            'data_hist': len(dh)},
                                'nocturno_fuera_de_db': len(noc - db),
                                'db_sin_registro': len(db - reg)},
                               ensure_ascii=False, indent=2))
    print(f'\nreporte: {out}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
