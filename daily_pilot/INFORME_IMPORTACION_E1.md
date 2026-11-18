# INFORME — FASE 0 + IMPORTACIÓN DEL NOCTURNO A E1

Fecha: 2026-11-18 · Autorización: «si analiza el video nuevo! y importa E1!» · `PAPER_ONLY=true`
Backups: `daily_pilot/.backups_fase0_20261118T111917Z/` · `store.db.bak-pre-nocturno-*` · `store.db.bak-20261118T113227Z-*`

## 1. Video nuevo analizado
`cH2KY5vnsVQ` → `daily_pilot/analisis/cH2KY5vnsVQ_analisis.json`
- **646 cues**, 75 niveles, instrumentos BTC/NQ/ETH/XAUUSD.
- Estado resultante: **`VIDEO NUEVO ANALIZADO`**.

## 2. Nocturno importado a E1
`daily_pilot/scripts/importar_nocturno.py` (nuevo, idempotente):
- Copió los `.es.vtt` a `data_hist/<id>/` y generó `_transcript.json` (sin red).
- Registró los vídeos en `registro.json` con `fuente: nocturno_2026-11-17`.

`migrate.py --force`:
- fuentes: **42** transcripciones, 44 vtt, 17 análisis.
- **inserted=16.599** · updated=0 · unchanged=17.462 · rechazados=0.
- integrity `ok` · fk=0 · timestamps_nulos=0 · metadata_conflicts=116.

Cadena posterior: `extraer_claims.py` → `reclasificar_claims.py` → `anadir_temporalidad.py`.

## 3. Estado resultante

| | Antes | Después |
|---|---|---|
| vídeos | 21 | **42** |
| cues | 17.462 | **34.061** |
| claims | 3.802 | **6.831** |
| registro.json | 16 | **42** |
| data_hist | 22 | **42** |

**Linaje: DB 42 = registro 42 = data_hist 42 · 0 diferencias.**

Claims por tipo: `ESCENARIO_CONDICIONAL` 3.459 · `NIVEL_MENCIONADO` 2.757 · `ZONA_DE_INTERES` 260 · `NO_DETERMINABLE` 208 · `SENAL_EXPLICITA` 123 · `SIN_OPERACION` 24.
Temporalidad: semanal 199 · diario 67 · 4h 110 · intradía 48 · neutro 6.407.

## 4. Verificación
| Comprobación | Resultado |
|---|---|
| `run_all.py` | **5/5 suites OK · FUENTES INTACTAS** |
| Tests | 18 core · 10 métricas · 19 RM · 8 dashboard · 14 C2C3E6 |
| `verify_integrity.py` | **OK** · 42/34.061/6.831 |
| Dashboard | 60.113 B · `file://` limpio · `VIDEO NUEVO ANALIZADO` |
| Relaciones | 7 niveles repetidos · 4.034 descartados por plausibilidad |
| Escenarios | 60 versiones · 25 vigentes |

## 5. Corrección de un hallazgo mío
El informe previo decía **21 vídeos** en el nocturno: eran **20** — el vigésimo primero era `__pycache__` (caché de Python). La auditoría DeepSeek tenía razón.

## 6. Pendiente
1. `metadata_conflicts=116` en la migración: difieren `published`/`detectado` entre fuentes (no es corrupción; hay que elegir una regla de prioridad).
2. Los 5 vídeos que estaban en DB ya fueron registrados (linaje cerrado).
3. Ruta de dependencias externa: `tvdatafeed`/`ccxt` siguen sin usarse; el siguiente paso natural es la **Fase 1 (capa de datos de mercado)**.
