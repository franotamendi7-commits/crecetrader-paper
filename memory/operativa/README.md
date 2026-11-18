# Memoria Operativa — YouTubeTradingAgent

**Directorio exclusivo:** `~/YouTubeTradingAgent/memory/operativa/`

Este directorio contiene la memoria operativa del nuevo proyecto
**YouTubeTradingAgent**. La memoria histórica del trabajo experimental se mantiene
separada en `experimental/memory/` e **no se carga automáticamente** en ninguna
sesión del nuevo proyecto.

---

## Estructura

```
memory/operativa/
├── memory.json          # Memoria principal (JSON)
├── README.md            # Este archivo
└── historial/           # Historial de cambios (si se necesita)
```

---

## Reglas de uso

1. **Memoria operativa** (esta carpeta): usada exclusivamente por YouTubeTradingAgent.
   - Se carga en las sesiones del nuevo proyecto.
   - Se actualiza con las decisiones y evidencias del nuevo proyecto.

2. **Memoria histórica** (`experimental/memory/`): trabajo experimental original.
   - Se conserva intacta.
   - No se carga automáticamente.
   - Consultable solo cuando haya una necesidad explícita.

3. **No mezclar decisiones antiguas con las nuevas.** Las reglas antiguas pueden consultarse, pero no condicionan las nuevas.

4. **No añadir datos no verificados** a la memoria operativa.

5. **Trazabilidad:** cada entrada debe tener video, fecha, timestamp, frame y evidencia.

---

## Estado actual

- `memory.json`: vacía (versión 1.0.0, creada 2026-11-10)
- `historial/`: vacío por ahora
- Memoria operativa: [CREADA] — pendiente de llenado por el nuevo proyecto

---

## Notas

- Este directorio no depende de `~/Harness` ni del sistema anterior CHIEF.
- El nuevo proyecto no carga automáticamente `experimental/memory/`.
- Una sesión nueva únicamente carga `~/YouTubeTradingAgent/memory/operativa/`.
