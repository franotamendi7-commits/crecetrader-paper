#!/usr/bin/env python3
"""E1 — Knowledge Store (SQLite + FTS5) para YouTubeTradingAgent.

Capa de memoria histórica. Aditiva: los archivos originales son de SOLO lectura.
No genera claims semanticos, no interpreta videos ni graficos.
"""
from __future__ import annotations

import hashlib
import os
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent   # YouTubeTradingAgent
KNOWLEDGE_DIR = Path(__file__).resolve().parent
STORE_PATH = KNOWLEDGE_DIR / 'store.db'

SCHEMA_VERSION = '1.0.0'
MIGRATION_VERSION = '1.0.0'

PROGRESS_PATH = BASE_DIR / 'experimental' / 'results' / 'historical_progress.json'
REGISTRO_PATH = BASE_DIR / 'daily_pilot' / 'registro' / 'registro.json'
ESCENARIOS_PATH = BASE_DIR / 'daily_pilot' / 'datos' / 'escenarios_s_GjovZxQqY.json'
DATA_HIST = BASE_DIR / 'data_hist'
HISTORICAL_RESULTS = BASE_DIR / 'experimental' / 'results' / 'historical'
FRAMES_HIST = BASE_DIR / 'frames_hist'

PLACEHOLDERS = {None, '', '<anónimo>'}

# Prioridad documentada por campo (fuente que gana cuando ambas tienen valor real).
PRIORITY = {
    'title': 'registro',
    'published': 'registro',
    'url': 'registro',
    'detected_at': 'progress',
    'status': 'progress',
}

DDL = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS videos(
  video_id TEXT PRIMARY KEY,
  title TEXT, published TEXT, url TEXT, detected_at TEXT, status TEXT,
  duration_seconds REAL,
  source_path TEXT, source_sha256 TEXT,
  transcript_path TEXT, transcript_sha256 TEXT,
  frames_dir TEXT, analysis_path TEXT, analysis_sha256 TEXT,
  source TEXT, content_hash TEXT, imported_at TEXT, updated_at TEXT
);

CREATE TABLE IF NOT EXISTS cues(
  video_id TEXT NOT NULL REFERENCES videos(video_id) ON DELETE CASCADE,
  seq INTEGER NOT NULL,
  start TEXT NOT NULL, end TEXT NOT NULL,
  start_ms INTEGER NOT NULL, end_ms INTEGER NOT NULL,
  text TEXT NOT NULL, source_ref TEXT,
  content_hash TEXT NOT NULL,
  presente_en_source INTEGER NOT NULL DEFAULT 1,
  PRIMARY KEY(video_id, seq)
);

CREATE TABLE IF NOT EXISTS cue_history(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  video_id TEXT, seq INTEGER, campo TEXT,
  valor_previo TEXT, valor_nuevo TEXT, detectado_en TEXT
);

CREATE VIRTUAL TABLE IF NOT EXISTS cues_fts
  USING fts5(text, content='cues', content_rowid='rowid');

CREATE TABLE IF NOT EXISTS manual_scenarios(
  escenario_id TEXT PRIMARY KEY,
  video_id TEXT, payload TEXT,
  origen TEXT NOT NULL, archivo_fuente TEXT,
  sha256 TEXT, imported_at TEXT
);

CREATE TABLE IF NOT EXISTS source_files(
  path TEXT PRIMARY KEY, sha256 TEXT NOT NULL, tipo TEXT, bytes INTEGER
);

CREATE TABLE IF NOT EXISTS metadata_conflicts(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  video_id TEXT, campo TEXT,
  valor_a TEXT, fuente_a TEXT, valor_b TEXT, fuente_b TEXT,
  resolucion TEXT, detectado_en TEXT
);

CREATE TABLE IF NOT EXISTS migration_log(
  id INTEGER PRIMARY KEY AUTOINCREMENT, run_at TEXT,
  videos INT, cues INT, inserted INT, updated INT, unchanged INT,
  missing INT, rechazados INT, manifest_sha256 TEXT
);

CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT);

CREATE INDEX IF NOT EXISTS idx_cues_startms ON cues(start_ms);
CREATE INDEX IF NOT EXISTS idx_cues_video ON cues(video_id, seq);
CREATE INDEX IF NOT EXISTS idx_videos_published ON videos(published);
CREATE UNIQUE INDEX IF NOT EXISTS uq_metadata_conflicts
  ON metadata_conflicts(video_id, campo, valor_a, valor_b, fuente_a, fuente_b);

CREATE TABLE IF NOT EXISTS claims(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  video_id TEXT NOT NULL REFERENCES videos(video_id) ON DELETE CASCADE,
  seq INTEGER NOT NULL,
  start TEXT,
  claim_hash TEXT NOT NULL,
  tipo TEXT,
  nivel TEXT,
  procedencia TEXT,
  confianza REAL,
  texto TEXT,
  motivo TEXT,
  extraido_en TEXT
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_claims_hash ON claims(video_id, claim_hash);
CREATE INDEX IF NOT EXISTS idx_claims_video ON claims(video_id, seq);
CREATE INDEX IF NOT EXISTS idx_claims_tipo ON claims(tipo);
"""

TS_RE = re.compile(r'^(\d+):(\d{2}):(\d{2})\.(\d{3})$')


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_str(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


def sha256_file(p: Path) -> str:
    return sha256_bytes(Path(p).read_bytes())


def to_ms(ts: str) -> int:
    """Convierte 'HH:MM:SS.mmm' a milisegundos. Falla si el formato difiere."""
    m = TS_RE.match(ts)
    if not m:
        raise ValueError(f'timestamp con formato inesperado: {ts!r}')
    h, mi, s, ms = (int(x) for x in m.groups())
    return ((h * 3600 + mi * 60 + s) * 1000) + ms


def ms_to_str(ms: int) -> str:
    h, r = divmod(ms, 3600000)
    mi, r = divmod(r, 60000)
    s, milli = divmod(r, 1000)
    return f'{h:02d}:{mi:02d}:{s:02d}.{milli:03d}'


def _validar_path(path: Path) -> Path:
    """Guard anti-huye: el store debe vivir DENTRO del arbol del piloto.

    Antes no habia guard y la integracion corriendo desde una copia abria el
    store VIVO (hallazgo P0-1 de la auditoria 2026-11-20).
    """
    p = Path(path).resolve()
    try:
        p.relative_to(KNOWLEDGE_DIR.resolve())
    except ValueError:
        raise SystemExit(
            f'GUARD: se intento abrir un store fuera del piloto: {p} '
            f'(esperado dentro de {KNOWLEDGE_DIR.resolve()})')
    return p


def conectar(path: Path | None = None) -> sqlite3.Connection:
    path = _validar_path(path or STORE_PATH)   # evaluado en tiempo de ejecucion
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), isolation_level=None)   # autocommit; TX explicitas
    conn.execute('PRAGMA foreign_keys=ON')
    conn.execute('PRAGMA synchronous=NORMAL')
    return conn


def crear_esquema(conn: sqlite3.Connection) -> None:
    conn.executescript(DDL)
    conn.commit()


def verificar_esquema_fuente(transcripciones: list[Path]) -> list[str]:
    """Preflight: valida la forma de cada transcripcion. Devuelve errores."""
    errores = []
    for p in transcripciones:
        try:
            import json
            d = json.loads(p.read_text(encoding='utf-8'))
        except Exception as exc:
            errores.append(f'{p}: no es JSON valido ({exc})')
            continue
        if 'video_id' not in d or 'segments' not in d:
            errores.append(f'{p}: sin video_id/segments')
            continue
        for i, s in enumerate(d['segments'], start=1):
            if not isinstance(s, dict) or 'text' not in s or 'start' not in s or 'end' not in s:
                errores.append(f'{p}: segmento {i} sin text/start/end')
                break
            try:
                to_ms(s['start'])
                to_ms(s['end'])
            except ValueError as exc:
                errores.append(f'{p}: segmento {i}: {exc}')
                break
    return errores
