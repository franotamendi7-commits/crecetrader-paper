# FASE 3.5 — Criterios de Aceptación

## 1. Condiciones para autorizar el benchmark

1. Ground truth independiente creado (doble anotación)
2. Protocolo de benchmark aprobado
3. Entorno aislado creado
4. Modelo seleccionado e instalado
5. Métricas y umbrales definidos
6. Hardware suficiente verificado

## 2. Condiciones para incorporar otro modelo

1. Modelo open source/open weights
2. Compatible con Apple Silicon M4
3. Consumo de RAM < 8 GB (int4)
4. Coste recurrente USD 0
5. Licencia permisiva (Apache 2.0 o MIT)

## 3. Condiciones de seguridad e integridad

1. No modificar archivos fuera de experimental/
2. No alterar Ollama
3. No modificar el pipeline original
4. Procesamiento secuencial por defecto
5. Límite de 1 modelo simultáneo
6. Logs de ejecución obligatorios
7. Posibilidad de eliminar experimental/ sin afectar nada

## 4. Estado

**[VERIFICADO]** — Criterios definidos
**[PENDIENTE]** — Autorización para ejecutar benchmark
EOF