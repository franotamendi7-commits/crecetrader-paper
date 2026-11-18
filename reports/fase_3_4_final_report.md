# FASE 3.4 — Informe Final

## 1. Dictamen técnico

**[APTO CON LIMITACIONES — REQUIERE CORRECCIONES]**

La fase diseñó un protocolo experimental completo para validar modelos de visión. No se instaló ni se probó ningún modelo. Todas las mejoras son propuestas.

## 2. Modelo recomendado para la prueba

**Moondream 2** (1.86B, int4, ~2.0 GB RAM)
- Menor consumo de recursos
- Apple Silicon nativo (MLX/Photon)
- Apache 2.0 (uso comercial libre)
- Velocidad ~0.7s por imagen
- OCR integrado
- Instalación simple (pip install moondream)
- Sin dependencias pesadas

**Alternativa:** Qwen2.5-VL-3B (mayor capacidad, requiere torch/transformers)

## 3. Justificación

Moondream 2 es el mejor balance entre calidad de interpretación y consumo de recursos para el hardware disponible (M4, 24GB RAM, ~15GB disponible). Qwen2.5-VL-7B requiere 5-7GB RAM y puede comprometer la estabilidad.

## 4. Coste y consumo estimados

| Recurso | Moondream 2 (int4) | Qwen2.5-VL-3B (int4) |
|---------|-------------------|----------------------|
| RAM | ~2.0 GB | ~2-3 GB |
| Disco | ~2.0 GB | ~2-3 GB |
| Velocidad | ~0.7s/img | ~1-2s/img |
| Coste | $0 | $0 |

**[VERIFICADO]** — Hardware: M4, 24GB RAM
**[PROPUESTO]** — Consumo de RAM (estimado, no medido)
**[PROPUESTO]** — Velocidad (estimada de benchmarks de terceros)

## 5. Riesgos y limitaciones

1. Moondream 2 no ha sido probado en este hardware
2. La velocidad real puede diferir de las estimaciones
3. El modelo puede no reconocer gráficos financieros específicos
4. Sin ground truth independiente, no se puede medir precisión real
5. Solo 1 video disponible para validación

## 6. Plan exacto de implementación experimental

1. Crear directorio experimental/ aislado
2. Crear .venv experimental
3. Instalar moondream (pip install moondream)
4. Crear script de prueba (experimental/scripts/test_moondream.py)
5. Probar con 5 frames representativos
6. Evaluar resultados
7. Si satisfactorio, implementar muestreo adaptativo
8. Ejecutar benchmark completo
9. Comparar con sistema anterior
10. Documentar resultados

## 7. Cambios que requieren autorización

- Instalación de moondream (pip install)
- Creación de directorio experimental/
- Descarga de pesos del modelo (~2GB)
- Modificación de código (solo en experimental/)

## 8. Recomendación

**[APTO CON LIMITACIONES — REQUIERE CORRECCIONES]**

El protocolo está diseñado pero no ejecutado. Se recomienda:
1. Autorizar instalación de Moondream 2 en entorno aislado
2. Ejecutar prueba con 5 frames
3. Evaluar resultados antes de avanzar

**La decisión de autorizar corresponde exclusivamente a Francisco.**

---

**PRINCIPIO DE AUDITORÍA: NO CREER. PROBAR.**
EOF