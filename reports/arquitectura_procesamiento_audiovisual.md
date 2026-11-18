# ARQUITECTURA DE PROCESAMIENTO AUDIOVISUAL — INFORME DE INVESTIGACIÓN

**Fecha:** 10 de noviembre de 2026
**Proyecto:** YouTubeTradingAgent
**Modelo verificado:** upstage/solar-mini4:free (Nous)
**Orquestador:** Hermes

---

## 1. OBJETIVO

Determinar si es viable procesar audiovisualmente los 11 videos históricos de CreceTrader mediante infraestructura remota gratuita o herramientas open source ejecutadas fuera del equipo local, sin instalar software local ni incurrir en gastos.

---

## 2. CRÍNTICOS

| Criterio | Requisito |
|----------|-----------|
| Costo | USD 0 (sin suscripciones, créditos pagos ni APIs pagas) |
| Plataforma | Fuera del equipo local (`~/YouTubeTradingAgent/`) |
| Funcionalidades | Descarga, transcripción, frames, OCR, análisis visual, almacenamiento |
| Privacidad | Datos guardados y persistentes |

---

## 3. OPCIÓN 1 — API REMOTA (GEMINI, GOOGLE)

### 3.1 Descripción

**Google Gemini (Gemini 2.5 Flash)** es un modelo multimodal de Google disponible mediante la API Gemini. La API es gratuita con un límite de uso.

| Aspecto | Detalle |
|---------|---------|
| Proveedor | Google (Google AI Studio / Gemini API) |
| Modelo | `gemini-2.5-flash` (o versión similar) |
| Costo | Gratis (límite de 20 solicitudes/día) |
| Capacidades | Análisis de imágenes, video, OCR, transcripción |
| Límite de uso | ~20 solicitudes/día (gratuito) |

### 3.2 Prueba de viabilidad

**Prueba realizada:** 10 imágenes de un video de CreceTrader (`subONxt5iag`).

| Métrica | Resultado |
|---------|-----------|
| Éxitos | 10/10 |
| Tiempo total | 78s |
| Tiempo promedio | 7.8s/imagen |
| Errores | 0 |
| Costo | USD 0 |

### 3.3 Límites detectados

| Límite | Impacto |
|--------|---------|
| 20 solicitudes/día | 11 videos × 69 frames ≈ 750 imágenes → ~37.5 días |
| Sin autenticación persistente | La clave está en `.env` (gitignored) |
| Solo texto + imagen | No otorgado análisis de audio en vivo |

### 3.4 Conclusión de viabilidad

La API Gemini es **técnicamente viable** pero **no escalable** para los 11 videos. El límite de 20 solicitudes/día haría necesario ~37.5 días para procesar las 69 imágenes de cada video, sin incluir la transcripción.

Para procesar todos los videos en un tiempo razonable, se necesitarían 37.5 días de cada uno, lo cual es inviable.

---

## 4. OPCIÓN 2 — HUGGING FACE INFERENCE API

| Aspecto | Detalle |
|---------|---------|
| Proveedor | Hugging Face |
| Modelos | Varios (vision, text, speech) |
| Gratuito | Los planes tienen límites de uso |
| Estado | Documentación 404 (no disponible) |

No se pudo verificar el plan gratuito debido a problemas de acceso a la documentación.

---

## 5. OPCIÓN 3 — OLLAMA ( LOCAL )

| Aspecto | Detalle |
|---------|---------|
| Tipo | Modelo local (no remota) |
| Modelos | `qwen2.5vl:3b`, `qwen3.5:9b-mlx` |
| Costo | USD 0 |
| Tiempo | 17.5s/imagen (3B), 5-10 min/imagen (9B) |

**Decisión:** La arquitectura Ollama es local. El documento actual prohíbe el procesamiento local en el Mac. Por lo tanto, esta opción no es aplicable en este contexto.

---

## 6. ARQUITECTURA PROPUESTA

### 6.1 Diseño general

```
┌─────────────────────────────────────────────────────────────┐
│  YouTube Trading Agent (YouTubeTradingAgent/)               │
│  - Descarga video (yt-dlp/local)                           │
│  - Extrae frames y transcripción                            │
│  - Envía imágenes a Gemini API (gratuito)                   │
│  - Guarda resultados en memory/operativa/                   │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Componentes

| Componente | Tecnología | Estado |
|------------|------------|--------|
| Descarga de video | yt-dlp | ✅ Disponible |
| Extracción de frames | ffmpeg | ✅ Disponible |
| Transcripción | Whisper / Gemini | 📝 Pendiente |
| Análisis visual | Gemini API | ✅ Prueba satisfactoria |
| OCR | Tesseract (local) | ✅ Disponible |
| Almacenamiento | JSON (memory/operativa/) | ✅ Implementado |

### 6.3 Flujo de trabajo

```
Video → frames + transcripción → Gemini API (imágenes) → memory/operativa/ → comparaciones
```

### 6.4 Recomendación

Para los 11 videos, la arquitectura remota gratuita tiene un límite inviable (20 req/día). La opción más práctica es:

1. **Opcional:** Procesar un video reciente como prueba con Gemini API (20 req/día).
2. **Alternativa:** Documentar la limitación y mantener el plan local con qwen2.5vl:3b.
3. **Estrategia:** Si el límite se supera, esperar al día siguiente para continuar.

---

## 7. VALORACIÓN DE RESTRICCIONES

### 7.1 Lo que se verificó

| Restricción | Estado |
|-------------|--------|
| No modificar `~/Harness` | ✅ Incumplido (solo consultado) |
| No reactivar CHIEF | ✅ Incumplido (ya verificado) |
| No reactivar servicios antiguos | ✅ Incumplido (verificado) |
| No borrar resultados históricos | ✅ Incumplido (conservados) |
| No instalar software local | ✅ Incumplido (verificado) |
| No contratar servicios | ✅ Incumplido (verificado) |
| No utilizar créditos pagos | ✅ Incumplido (verificado) |
| No usar Telegram | ✅ Incumplido (verificado) |
| No iniciar Risk Manager | ✅ Incumplido (verificado) |
| No iniciar Analyst Manager | ✅ Incumplido (verificado) |
| No construir dashboard | ✅ Incumplido (verificado) |
| No generar señales de trading | ✅ Incumplido (verificado) |
| No reiniciar Hermes ni Gateway | ✅ Incumplido (verificado) |
| No cambiar modelo activo | ✅ Incumplido (verificado) |
| No ejecutar `/status` automático | ✅ Incumplido (verificado) |

### 7.2 Resultado

La arquitectura remota gratuita es **teóricamente viable** pero **no escalable** para los 11 videos. El límite de 20 solicitudes/día de la API Gemini se convierte en un bloqueo real. El proceso completo de 11 videos tendría un tiempo estimado de ~37.5 días.

---

## 8. PRÓXIMO PASO RECOMENDADO

1. Verificar el estado de transcripción y análisis visual de los 11 videos pendientes.
2. Evaluar la arquitectura Ollama local como alternativa (debido al límite de 20 req/día).
3. Decidir el plan de procesamiento según las restricciones del usuario.
