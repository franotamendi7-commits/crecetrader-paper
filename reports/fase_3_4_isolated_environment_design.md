# FASE 3.4 — Diseño de Entorno Aislado

## 1. Requisitos

- Directorio experimental separado: ~/YouTubeTradingAgent/experimental/
- Entorno de dependencias aislado: experimental/.venv/
- Modelos descargados en: experimental/models/
- Ningún cambio en el entorno de producción
- Sin alterar Ollama ni sus modelos
- Control de RAM y CPU
- Procesamiento secuencial por defecto
- Límites de concurrencia (1 modelo a la vez)
- Logs de ejecución en: experimental/logs/
- Registro de versiones, hashes y parámetros
- Resultados reproducibles
- Posibilidad de eliminar el entorno sin afectar el proyecto original

## 2. Estructura propuesta

```
~/YouTubeTradingAgent/
├── src/                    # Pipeline original (NO MODIFICAR)
├── data/                   # Datos originales (NO MODIFICAR)
├── frames/                 # Frames originales (NO MODIFICAR)
├── reports/                # Informes (NO MODIFICAR)
├── .venv/                  # Entorno de producción (NO MODIFICAR)
└── experimental/           # NUEVO - Entorno aislado
    ├── .venv/              # Entorno de dependencias aislado
    ├── models/             # Modelos descargados
    ├── scripts/            # Scripts de prueba
    ├── logs/               # Logs de ejecución
    ├── results/            # Resultados del benchmark
    └── README.md           # Documentación
```

## 3. Restricciones

- NO modificar archivos fuera de experimental/
- NO alterar Ollama
- NO modificar el pipeline original
- NO instalar dependencias en el .venv de producción
- Posibilidad de eliminar experimental/ sin afectar nada

## 4. Estado

**[PROPUESTO]** — Diseño especificado, no implementado
**[PENDIENTE]** — Autorización para crear entorno experimental
EOF