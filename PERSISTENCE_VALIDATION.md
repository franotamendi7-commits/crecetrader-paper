# PERSISTENCE VALIDATION — FASE 1

## Fecha: 2026-11-09

## 1. DISEÑO DE PERSISTENCIA

### Base de datos: SQLite + FTS5

Ubicación: `~/YouTubeTradingAgent/data/agent.db` (a crear en Fase 1)

### Tablas principales

```sql
-- Videos detectados y procesados
CREATE TABLE videos (
    video_id TEXT PRIMARY KEY,
    title TEXT,
    channel TEXT,
    published_at TEXT,
    detected_at TEXT,
    status TEXT DEFAULT 'PENDING',  -- PENDING, PROCESSING, COMPLETED, FAILED, SKIPPED
    priority INTEGER DEFAULT 0,
    retry_count INTEGER DEFAULT 0,
    last_error TEXT,
    completed_at TEXT
);

-- Transcripciones
CREATE TABLE transcripts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id TEXT REFERENCES videos(video_id),
    text TEXT,
    segments_json TEXT,  -- JSON con timestamps
    language TEXT,
    created_at TEXT
);

-- Frames extraídos
CREATE TABLE frames (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id TEXT REFERENCES videos(video_id),
    frame_path TEXT,
    timestamp REAL,
    scene_number INTEGER,
    created_at TEXT
);

-- Análisis de charts (estructural + OCR + semántico)
CREATE TABLE chart_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id TEXT REFERENCES videos(video_id),
    frame_id INTEGER REFERENCES frames(id),
    structural_json TEXT,  -- chart-vision-mcp output
    ocr_text TEXT,         -- Tesseract output
    semantic_text TEXT,     -- Vision LLM output
    created_at TEXT
);

-- Metodología extraída
CREATE TABLE methodology (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id TEXT REFERENCES videos(video_id),
    instrument TEXT,
    timeframe TEXT,
    indicator TEXT,
    parameters TEXT,
    levels TEXT,
    scenario TEXT,
    confidence TEXT,  -- HIGH, MEDIUM, LOW
    classification TEXT,  -- [DICHO], [OBSERVADO], [INFERIDO]
    created_at TEXT
);

-- Informes
CREATE TABLE reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id TEXT REFERENCES videos(video_id),
    report_type TEXT,  -- individual, daily_summary
    content TEXT,
    created_at TEXT
);

-- FTS5 para búsqueda
CREATE VIRTUAL TABLE methodology_fts USING fts5(
    instrument, timeframe, indicator, scenario,
    content='methodology', content_rowid='id'
);
```

### Mecanismo de recuperación

1. **Checkpoint por paso:** Cada paso del pipeline actualiza el estado del video
2. **Reintentos:** Videos FAILED se reintentan hasta N veces
3. **Idempotencia:** Un video_id ya COMPLETED no se re-procesa
4. **Persistencia en disco:** SQLite en directorio del proyecto (no en memoria)
5. **Recuperación tras reinicio:** Al iniciar, cargar videos PENDING y FAILED

### Estados de la cola

```
PENDING → PROCESSING → COMPLETED
                    → FAILED → (retry) → PROCESSING
                    → SKIPPED (no relevante)
```

### Protección contra duplicados

- video_id es PRIMARY KEY (no se pueden insertar duplicados)
- Antes de procesar, verificar que video_id no está en COMPLETED
- Informes usan UNIQUE constraint en (video_id, report_type)

## 2. VERIFICACIÓN DE PERSISTENCIA

| Aspecto | Diseño | Estado |
|---|---|---|
| Base de datos en disco | SQLite en ~/YouTubeTradingAgent/data/ | [PROPUESTO] |
| Sobrevive reinicios | Si (archivo en disco) | [PROPUESTO] |
| No pierde videos pendientes | Cola persistente | [PROPUESTO] |
| No duplica informes | UNIQUE constraint | [PROPUESTO] |
| Checkpoints por paso | Estado actualizado por paso | [PROPUESTO] |
| Reintentos | retry_count + max_retries | [PROPUESTO] |
| Búsqueda por concepto | FTS5 | [PROPUESTO] |

## 3. RIESGOS

| Riesgo | Mitigación |
|---|---|
| Corrupción de SQLite | Backup periódico, integridad check |
| Pérdida de datos | Archivo en disco, no en memoria |
| Duplicados | PRIMARY KEY + idempotencia |
| Procesos interrumpidos | Checkpoint + recuperación |

## 4. CLASIFICACIÓN

- [VERIFICADO]: SQLite + FTS5 funciona (probado en Hermes Memory Vault)
- [PROPUESTO]: Esquema completo (requiere implementación en Fase 1)
- [PENDIENTE]: Pruebas de persistencia real
