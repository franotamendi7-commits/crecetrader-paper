#!/usr/bin/env python3
"""E1 — Migracion idempotenta de las fuentes historicas al Knowledge Store.

Solo lectura sobre los originales. Aditiva: nunca modifica ni borra fuentes.
Uso:
    python3 migrate.py            # aborta si store.db ya existe
    python3 migrate.py --force    # reimporta (idempotente) sobre un store existente
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

import store as S


def log(msg: str) -> None:
    print(msg, flush=True)


def fuentes() -> dict:
    trans = sorted(S.DATA_HIST.glob('*/*_transcript.json'))
    vtt = sorted(S.DATA_HIST.glob('*/*.vtt'))
    analisis = sorted(S.HISTORICAL_RESULTS.glob('*_analysis.json'))
    return {'transcripciones': trans, 'vtt': vtt, 'analisis': analisis}


def registrar_source_files(conn: sqlite3.Connection, fs: dict) -> None:
    archivos = list(fs['transcripciones']) + list(fs['vtt']) + list(fs['analisis'])
    archivos += [S.PROGRESS_PATH, S.REGISTRO_PATH, S.ESCENARIOS_PATH]
    for p in archivos:
        p = Path(p)
        if not p.exists():
            continue
        conn.execute(
            'INSERT OR IGNORE INTO source_files(path, sha256, tipo, bytes) VALUES(?,?,?,?)',
            (str(p), S.sha256_file(p),
             'transcripcion' if p in fs['transcripciones'] else
             'vtt' if p in fs['vtt'] else
             'analsis' if p in fs['analisis'] else 'estado', p.stat().st_size))


def importar_videos(conn: sqlite3.Connection, fs: dict) -> tuple[int, dict]:
    """Fusiona historical_progress + registro con la regla de prioridad documentada."""
    prog = json.loads(S.PROGRESS_PATH.read_text(encoding='utf-8')).get('videos', {})
    reg = json.loads(S.REGISTRO_PATH.read_text(encoding='utf-8')).get('videos', {})
    conflictos = 0
    for vid in sorted(set(prog) | set(reg)):
        a, b = prog.get(vid, {}), reg.get(vid, {})
        vals = {}
        for campo, prio in S.PRIORITY.items():
            va, vb = a.get(campo), b.get(campo)
            if va == vb:
                vals[campo] = va
                continue
            # registrar la divergencia (sin sobrescritura silenciosa)
            if va not in S.PLACEHOLDERS and vb not in S.PLACEHOLDERS:
                resolucion = f'prioridad:{prio}'
                vals[campo] = vb if prio == 'registro' else va
            elif va in S.PLACEHOLDERS and vb in S.PLACEHOLDERS:
                vals[campo] = None
                continue
            else:
                resolucion = 'fusion: placeholder tratado como ausente'
                vals[campo] = vb if va in S.PLACEHOLDERS else va
            conflictos += 1
            conn.execute(
                'INSERT OR IGNORE INTO metadata_conflicts(video_id,campo,valor_a,valor_b,fuente_a,fuente_b,resolucion,detectado_en)'
                ' VALUES(?,?,?,?,?,?,?,?)',
                (vid, campo, str(va), str(vb), 'progress', 'registro', resolucion, S.now_iso()))
        # artefactos y rutas (solo progress las declara)
        art = a.get('artifacts') or {}
        transcript = None
        for p in fs['transcripciones']:
            if p.parent.name == vid:
                transcript = p
                break
        source = '+'.join([n for n, d in (('progress', a), ('registro', b)) if d])
        payload = {
            'title': vals.get('title'), 'published': vals.get('published'),
            'url': vals.get('url'), 'detected_at': vals.get('detected_at'),
            'status': vals.get('status'),
            'duration_seconds': None,
            'transcript_path': str(transcript) if transcript else None,
            'transcript_sha256': S.sha256_file(transcript) if transcript else None,
            'frames_dir': art.get('frames_dir'),
            'analysis_path': art.get('analysis_file'),
            'analysis_sha256': (S.sha256_file(art.get('analysis_file'))
                                if art.get('analysis_file') and Path(art['analysis_file']).exists() else None),
            'source': source,
            'content_hash': None,
        }
        if transcript is not None:
            d = json.loads(transcript.read_text(encoding='utf-8'))
            payload['duration_seconds'] = d.get('duration_seconds')
            payload['content_hash'] = S.sha256_str(json.dumps(
                {'n': len(d.get('segments', [])), 'tsha': payload['transcript_sha256']},
                sort_keys=True))
        cur = conn.execute('SELECT content_hash FROM videos WHERE video_id=?', (vid,)).fetchone()
        if cur is None:
            conn.execute(
                'INSERT INTO videos(video_id,title,published,url,detected_at,status,duration_seconds,'
                'source_path,source_sha256,transcript_path,transcript_sha256,frames_dir,analysis_path,'
                'analysis_sha256,source,content_hash,imported_at,updated_at) '
                'VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                (vid, payload['title'], payload['published'], payload['url'], payload['detected_at'],
                 payload['status'], payload['duration_seconds'], str(transcript) if transcript else None,
                 payload['transcript_sha256'], payload['transcript_path'], payload['transcript_sha256'],
                 payload['frames_dir'], payload['analysis_path'], payload['analysis_sha256'],
                 payload['source'], payload['content_hash'], S.now_iso(), S.now_iso()))
        elif cur[0] != payload['content_hash']:
            conn.execute(
                'UPDATE videos SET transcript_sha256=?,content_hash=?,updated_at=? WHERE video_id=?',
                (payload['transcript_sha256'], payload['content_hash'], S.now_iso(), vid))
        else:
            # P0: si la metadata real llego despues, rellenar huecos sin tocar el hash
            ant = conn.execute('SELECT title,published FROM videos WHERE video_id=?', (vid,)).fetchone()
            nue = (payload.get('title') or '', payload.get('published') or '')
            if ant and (ant[0] in (None, '') and nue[0]) or (ant and ant[1] in (None, '') and nue[1]):
                conn.execute('UPDATE videos SET title=COALESCE(NULLIF(title,\'\'),?),'
                             'published=COALESCE(NULLIF(published,\'\'),?),updated_at=? WHERE video_id=?',
                             (nue[0], nue[1], S.now_iso(), vid))
    return len(set(prog) | set(reg)), {'metadata_conflicts': conflictos}


def importar_cues(conn: sqlite3.Connection, fs: dict) -> tuple[int, int, int, int, int]:
    ins = upd = unch = rech = 0
    for p in fs['transcripciones']:
        vid = p.parent.name
        d = json.loads(p.read_text(encoding='utf-8'))
        for i, s in enumerate(d['segments'], start=1):
            try:
                st_ms, en_ms = S.to_ms(s['start']), S.to_ms(s['end'])
            except (KeyError, ValueError):
                rech += 1
                continue
            ch = S.sha256_str(f"{s['start']}|{s['end']}|{s['text']}")
            row = conn.execute('SELECT content_hash FROM cues WHERE video_id=? AND seq=?',
                               (vid, i)).fetchone()
            if row is None:
                conn.execute(
                    'INSERT INTO cues(video_id,seq,start,end,start_ms,end_ms,text,source_ref,content_hash) '
                    'VALUES(?,?,?,?,?,?,?,?,?)',
                    (vid, i, s['start'], s['end'], st_ms, en_ms, s['text'],
                     s.get('source'), ch))
                ins += 1
            elif row[0] != ch:
                viejo = conn.execute('SELECT text FROM cues WHERE video_id=? AND seq=?',
                                     (vid, i)).fetchone()[0]
                conn.execute('SAVEPOINT cue_upd')
                conn.execute(
                    'INSERT INTO cue_history(video_id,seq,campo,valor_previo,valor_nuevo,detectado_en) '
                    'VALUES(?,?,?,?,?,?)', (vid, i, 'texto', viejo, s['text'], S.now_iso()))
                conn.execute(
                    'UPDATE cues SET start=?,end=?,start_ms=?,end_ms=?,text=?,content_hash=? '
                    'WHERE video_id=? AND seq=?',
                    (s['start'], s['end'], st_ms, en_ms, s['text'], ch, vid, i))
                conn.execute('RELEASE SAVEPOINT cue_upd')
                upd += 1
            else:
                unch += 1
    conn.execute("INSERT INTO cues_fts(cues_fts) VALUES('rebuild')")
    return ins, upd, unch, rech, 0


def importar_escenarios(conn: sqlite3.Connection) -> int:
    d = json.loads(S.ESCENARIOS_PATH.read_text(encoding='utf-8'))
    n = 0
    for e in d.get('escenarios', []):
        esc = e.get('escenario', e)
        eid = esc.get('id')
        payload = json.dumps(e, ensure_ascii=False, sort_keys=True)
        conn.execute(
            'INSERT OR IGNORE INTO manual_scenarios(escenario_id,video_id,payload,origen,archivo_fuente,sha256,imported_at)'
            ' VALUES(?,?,?,?,?,?,?)',
            (eid, esc.get('video_id'), payload, 'manual', str(S.ESCENARIOS_PATH),
             S.sha256_str(payload), S.now_iso()))
        n += 1
    return n


def marcar_faltantes(conn: sqlite3.Connection, fs: dict) -> int:
    """Cues en BD que ya no estan en la fuente: se marcan, nunca se borran."""
    missing = 0
    for p in fs['transcripciones']:
        vid = p.parent.name
        d = json.loads(p.read_text(encoding='utf-8'))
        actuales = set(range(1, len(d['segments']) + 1))
        filas = conn.execute('SELECT seq FROM cues WHERE video_id=? AND presente_en_source=1',
                             (vid,)).fetchall()
        for (seq,) in filas:
            if seq not in actuales:
                conn.execute('UPDATE cues SET presente_en_source=0 WHERE video_id=? AND seq=?',
                             (vid, seq))
                missing += 1
    return missing


def backup_store(etiqueta: str) -> Path | None:
    """Backup consistente (WAL) con conexion de solo lectura; NUNCA con TX abierta."""
    if not S.STORE_PATH.exists() or S.STORE_PATH.stat().st_size == 0:
        return None
    bak = S.KNOWLEDGE_DIR / f"store.db.bak-{etiqueta}-{os.getpid()}"
    if bak.exists():
        return None
    src = sqlite3.connect(f'file:{S.STORE_PATH}?mode=ro', uri=True)
    dst = sqlite3.connect(str(bak))
    src.backup(dst)
    dst.close()
    src.close()
    return bak


def verificar_backup(bak: Path | None) -> dict:
    if bak is None:
        return {'backup': None, 'integrity': None, 'cues': None}
    b = sqlite3.connect(str(bak))
    integ = b.execute('PRAGMA integrity_check').fetchone()[0]
    n = b.execute('SELECT COUNT(*) FROM cues').fetchone()[0]
    b.close()
    return {'backup': str(bak), 'integrity': integ, 'cues': n}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--force', action='store_true',
                    help='permite reimportar sobre un store existente (idempotente)')
    args = ap.parse_args()

    fs = fuentes()
    log(f"fuentes: {len(fs['transcripciones'])} transcripciones, {len(fs['vtt'])} vtt, "
        f"{len(fs['analisis'])} analisis")

    errores = S.verificar_esquema_fuente(fs['transcripciones'])
    if errores:
        log('PREFLIGHT FALLIDO (no se escribio nada):')
        for e in errores:
            log('  - ' + e)
        return 2

    if S.STORE_PATH.exists() and not args.force:
        log(f"ABORTADO: {S.STORE_PATH} ya existe. Usa --force para reimportar (idempotente).")
        return 3

    pre_hash = S.sha256_file(S.STORE_PATH) if S.STORE_PATH.exists() else None
    etq = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    bak = backup_store(etq)          # ANTES de escribir (sin TX abiertas)

    conn = S.conectar()
    S.crear_esquema(conn)
    registrar_source_files(conn, fs)

    ins = upd = unch = rech = missing = nesc = 0
    conn.execute('BEGIN')
    try:
        nv, meta_v = importar_videos(conn, fs)
        ins, upd, unch, rech, _ = importar_cues(conn, fs)
        missing = marcar_faltantes(conn, fs)
        nesc = importar_escenarios(conn)
        conn.execute("INSERT INTO cues_fts(cues_fts) VALUES('rebuild')")
        conn.execute('COMMIT')
    except BaseException:
        conn.execute('ROLLBACK')
        raise

    # Verificaciones
    integridad = conn.execute('PRAGMA integrity_check').fetchone()[0]
    fk = conn.execute('PRAGMA foreign_key_check').fetchall()
    total_cues = conn.execute('SELECT COUNT(*) FROM cues').fetchone()[0]
    total_videos = conn.execute('SELECT COUNT(*) FROM videos').fetchone()[0]
    malts = conn.execute('SELECT COUNT(*) FROM cues WHERE start_ms IS NULL OR end_ms IS NULL').fetchone()[0]
    n_conf = conn.execute('SELECT COUNT(*) FROM metadata_conflicts').fetchone()[0]
    n_hist = conn.execute('SELECT COUNT(*) FROM cue_history').fetchone()[0]

    manif = {
        'schema_version': S.SCHEMA_VERSION,
        'migration_version': S.MIGRATION_VERSION,
        'run_at': S.now_iso(),
        'store_path': str(S.STORE_PATH),
        'store_sha256_pre': pre_hash,
        'fuentes': {
            'transcripciones': len(fs['transcripciones']),
            'vtt': len(fs['vtt']),
            'analisis': len(fs['analisis']),
            'progress': str(S.PROGRESS_PATH),
            'registro': str(S.REGISTRO_PATH),
            'escenarios': str(S.ESCENARIOS_PATH),
        },
        'importacion': {
            'videos': total_videos, 'cues': total_cues, 'escenarios_manuales': nesc,
            'inserted': ins, 'updated': upd, 'unchanged': unch,
            'missing': missing, 'rechazados': rech,
        },
        'verificacion': {
            'integrity_check': integridad, 'foreign_key_check': len(fk),
            'timestamps_nulos': malts, 'metadata_conflicts': n_conf, 'cue_history': n_hist,
        },
        'hashes_store': {'pre': pre_hash, 'post': S.sha256_file(S.STORE_PATH)},
        'pruebas': {
            'conteo_cues_17462': total_cues == 17462,
            'conteo_videos_20': total_videos == 20,
            'integridad_ok': integridad == 'ok',
            'fk_limpias': not fk,
        },
        'backup': verificar_backup(bak),
    }
    (S.KNOWLEDGE_DIR / 'integrity_manifest.json').write_text(
        json.dumps(manif, ensure_ascii=False, indent=2), encoding='utf-8')
    conn.execute('INSERT OR REPLACE INTO meta(key,value) VALUES(?,?)',
                 ('integrity_manifest_sha256', S.sha256_file(S.KNOWLEDGE_DIR / 'integrity_manifest.json')))
    conn.execute(
        'INSERT INTO migration_log(run_at,videos,cues,inserted,updated,unchanged,missing,rechazados,manifest_sha256)'
        ' VALUES(?,?,?,?,?,?,?,?,?)',
        (S.now_iso(), total_videos, total_cues, ins, upd, unch, missing, rech,
         manif['verificacion']['integrity_check']))
    conn.execute('INSERT OR REPLACE INTO meta(key,value) VALUES(?,?)', ('base_dir', str(S.BASE_DIR)))
    conn.execute('INSERT OR REPLACE INTO meta(key,value) VALUES(?,?)', ('schema_version', S.SCHEMA_VERSION))
    conn.commit()

    # Control sidecar
    control = {
        'run_at': S.now_iso(),
        'cues': total_cues, 'videos': total_videos,
        'escenarios_manuales': nesc,
        'source_files': conn.execute('SELECT COUNT(*) FROM source_files').fetchone()[0],
        'hashes_post': {str(p): S.sha256_file(p) for p in fs['transcripciones']},
        'store_sha256': S.sha256_file(S.STORE_PATH),
    }
    (S.KNOWLEDGE_DIR / '.control.json').write_text(
        json.dumps(control, ensure_ascii=False, indent=2), encoding='utf-8')

    log(f'importacion: videos={total_videos} cues={total_cues} escenarios={nesc}')
    log(f'inserted={ins} updated={upd} unchanged={unch} missing={missing} rechazados={rech}')
    log(f'integrity={integridad} fk={len(fk)} timestamps_nulos={malts} '
        f'metadata_conflicts={n_conf} cue_history={n_hist}')
    log(f'backup={manif["backup"]["backup"]} (integrity={manif["backup"]["integrity"]}, '
        f'cues={manif["backup"]["cues"]})')
    conn.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
