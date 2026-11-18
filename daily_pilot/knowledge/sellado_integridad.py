#!/usr/bin/env python3
"""Sella la integridad de E1 en el ORDEN correcto (PAPER_ONLY, read-only sobre el store).

Ciclo P0-3: el hash del store debe medirse ANTES de cualquier write posterior
(p.ej. meta o .control). Este script fija el orden canonico:

    1. sha256(store.db)            -> .control.store_sha256
    2. manifiesto con ese hash     -> integrity_manifest.json
    3. sha256(manifiesto)          -> .control.manifest_sha256

El store NO se escribe. Verificar con verify_integrity.py.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import store as S

PAPER_ONLY = True


def main() -> int:
    store_sha = S.sha256_file(S.STORE_PATH)
    man_path = S.KNOWLEDGE_DIR / 'integrity_manifest.json'
    m = json.loads(man_path.read_text(encoding='utf-8')) if man_path.exists() else {}
    m['hashes_store'] = {'pre': m.get('hashes_store', {}).get('pre'), 'post': store_sha,
                         'nota': 'post = sha256(store.db) medido antes de tocar .control/Manifiesto'}
    m['hash_post_store'] = store_sha
    man_path.write_text(json.dumps(m, ensure_ascii=False, indent=2))

    man_sha = S.sha256_file(man_path)
    ctl_path = S.KNOWLEDGE_DIR / '.control.json'
    c = json.loads(ctl_path.read_text(encoding='utf-8')) if ctl_path.exists() else {}
    c['store_sha256'] = store_sha
    c['manifest_sha256'] = man_sha
    c['hashes_store'] = {'pre': m['hashes_store']['pre'], 'post': store_sha}
    c['sellado'] = 'orden canonico: store -> manifiesto -> .control'
    ctl_path.write_text(json.dumps(c, ensure_ascii=False, indent=2))

    print(f'store.db        : {store_sha[:16]}')
    print(f'manifiesto      : {man_sha[:16]}')
    print(f'.control.json   : store={c["store_sha256"][:16]} manifest={man_sha[:16]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
