#!/usr/bin/env python3
"""Verificador de integridad de E1 — READ-ONLY (PAPER_ONLY).

P0-3 FIX: la cadena de integridad anterior no cerraba (hashes calculados
antes de escribir). Este script es la fuente de verdad canónica:

    hash canonico = hashes_store.post  debe ser igual a  sha256(store.db)

Falla (exit 1) si no coincide. No escribe nada.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import store as S

PAPER_ONLY = True


def sha(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main() -> int:
    real = sha(S.STORE_PATH)
    manif = S.KNOWLEDGE_DIR / 'integrity_manifest.json'
    problemas = []

    if not manif.exists():
        problemas.append('integrity_manifest.json no existe')
        m = {}
    else:
        m = json.loads(manif.read_text(encoding='utf-8'))

    hs = (m.get('hashes_store') or {})
    post = hs.get('post')
    pre = hs.get('pre')
    print(f'store.db sha256 real      : {real}')
    print(f'hashes_store.pre         : {pre}')
    print(f'hashes_store.post (canon): {post}')
    print(f'hash_post_store (legado) : {m.get("hash_post_store")}')
    ctl = S.KNOWLEDGE_DIR / '.control.json'
    if ctl.exists():
        c = json.loads(ctl.read_text(encoding='utf-8'))
        print(f'.control.json store_sha256: {c.get("store_sha256")}')

    if not post:
        problemas.append('hashes_store.post ausente')
    elif post != real:
        problemas.append(f'hashes_store.post NO coincide con store.db ({post} != {real})')
    if pre == post and pre is not None:
        problemas.append('hashes_store.pre == post: el hash "post" se calculó antes de escribir')

    conn = sqlite3.connect(f'file:{S.STORE_PATH}?mode=ro', uri=True)
    try:
        integ = conn.execute('PRAGMA integrity_check').fetchone()[0]
        nv = conn.execute('SELECT COUNT(*) FROM videos').fetchone()[0]
        nc = conn.execute('SELECT COUNT(*) FROM cues').fetchone()[0]
        ncl = conn.execute('SELECT COUNT(*) FROM claims').fetchone()[0]
        meta_man = conn.execute("SELECT value FROM meta WHERE key='integrity_manifest_sha256'").fetchone()
    finally:
        conn.close()
    if meta_man:
        real_man = hashlib.sha256(manif.read_bytes()).hexdigest()
        print(f'meta.integrity_manifest_sha256: {meta_man[0][:16]} (legado, no canonico)')
    ctl2 = S.KNOWLEDGE_DIR / '.control.json'
    if ctl2.exists():
        c2 = json.loads(ctl2.read_text(encoding='utf-8'))
        a, b = c2.get('store_sha256'), c2.get('manifest_sha256')
        real_man = hashlib.sha256(manif.read_bytes()).hexdigest()
        print(f'.control store_sha256 : {str(a)[:16]}')
        print(f'.control manifest_sha256: {str(b)[:16]} · real {real_man[:16]}')
        if a != real:
            problemas.append(f'.control.store_sha256 NO coincide con store.db ({a} != {real})')
        if b != real_man:
            problemas.append('.control.manifest_sha256 NO coincide con el manifiesto real')
    else:
        problemas.append('.control.json ausente')
    print(f'integrity_check          : {integ}')
    print(f'videos/cues/claims       : {nv}/{nc}/{ncl}')
    if integ != 'ok':
        problemas.append(f'integrity_check = {integ}')

    decl = m.get('videos_post')
    if decl is not None and decl != nv:
        problemas.append(f'manifiesto videos_post={decl} != real {nv}')
    tests20 = (m.get('pruebas') or {}).get('conteo_videos_20')
    if tests20 and nv != 20:
        problemas.append(f'manifiesto declara conteo_videos_20=True con {nv} vídeos')

    print()
    if problemas:
        print('RESULTADO: FALLA — cadena de integridad rota')
        for p in problemas:
            print('  -', p)
        return 1
    print('RESULTADO: OK — hashes y conteos consistentes')
    return 0


if __name__ == '__main__':
    sys.exit(main())
