# B4 — INFORME DE VALIDACIÓN VISUAL (TradingView, LFHkc5dUoLw)

Fecha: 2026-11-16
Estado global: **PREPARADO — NO EJECUTADO — PENDIENTE DE REFERENCIA HUMANA**

---

## 1. Identificación del modelo y configuración

| Ítem | Valor |
|---|---|
| Modelo | `qwen2.5vl:3b` (Ollama local `localhost:11434`) |
| Arquitectura | qwen25vl, 3,8B |
| Cuantización | Q4_K_M |
| Contexto | 128000 |
| Temperatura | 0,1 (igual que producción) |
| `top_p` / `num_predict` / `repeat_penalty` | **no configurados** → defaults del servidor (**NO VERIFICADOS**) |
| Prompt | experimental, en `B4_PROTOCOLO_EVALUACION.md` (no es el de producción) |
| Preprocesamiento | ninguno (frame original 640×352, base64) |

## 2. Identificación de los 20 frames

`frames_hist/LFHkc5dUoLw/frame_3994.jpg` … `frame_4013.jpg`. Copias verificadas: `entregas_a74/LFHkc5dUoLw/` (20/20 MD5 idénticos).
Son consecutivos y cubren **798,60–802,40 s** (últimos **3,80 s** del vídeo). Representan **una sola escena**.

## 3. Estado de las anotaciones humanas

**PENDIENTE.** No hay dos anotadores humanos independientes disponibles. No se fabricó ground truth ni se simuló una segunda opinión. Las 20 fichas están listas en `B4_fichas_anotacion/` y la plantilla normalizada en `B4_referencia_humana_template.csv`.

## 4. Resultados individuales por frame

**NO DISPONIBLE.** El script `scripts/b4_ejecutar_evaluacion.py` está preparado pero **bloqueado**: sin el flag `--ejecutar` no llama al modelo (verificado). No se ejecutó la evaluación.

## 5. Comparación contra referencia humana

**NO DISPONIBLE** (sin referencia humana).

## 6. Métricas agregadas

**NO DISPONIBLES.** No se calculó ninguna métrica de comprensión.

## 7. Ejemplos de aciertos

**NO DISPONIBLE** (B4 no ejecutado).

## 8. Ejemplos de errores

**NO DISPONIBLE** (B4 no ejecutado).

## 9. Ejemplos de alucinaciones

**NO DISPONIBLE en B4.** (Los detectados en la auditoría de A.7.4 corresponden al prompt de producción y **no** constituyen resultados de B4.)

## 10. Limitaciones de resolución y obstrucciones

Verificadas en la auditoría de capturas:
- Resolución **640×352**; etiquetas de precios pequeñas.
- **Obstrucciones**: ventana del presentador (arriba centro) y franja publicitaria morada (abajo) que **tapa el eje de fechas** y el posible panel de volumen.
- Ilegible de forma recurrente: esquina superior izquierda (símbolo/OHLC), panel superior derecho.

## 11. Conclusiones

- B4 está **preparado y aislado**: fichas, protocolo, script de evaluación y comparador listos.
- **No se evaluó el modelo** y **no se validó** ninguna capacidad en esta etapa.
- La muestra (20 frames de una sola escena de 3,8 s) **no permite** declarar aprobado el YouTube Analyst ni extrapolar al vídeo completo.
- Capacidades demostradas: ninguna por B4. Capacidades pendientes: todas.

## 12. Recomendaciones técnicas

1. Conseguir **dos anotadores humanos independientes** y completar las fichas; solo entonces ejecutar B4.
2. Adjudicar desacuerdos con un tercero antes de usar la referencia.
3. Ejecutar `b4_ejecutar_evaluacion.py --ejecutar` con la referencia validada.
4. Completar la evaluación en los 6 vídeos restantes (muestreo uniforme) antes de cualquier conclusión general.
5. No cambiar de modelo sin evidencia comparativa.

## Restricciones respetadas

Sin cambios en producción, prompts, modelos, skills ni configuración. Sin reprocesamiento de vídeo. Sin APIs pagas. Sin reentrenamiento. Sin conexión al pipeline. El experimento quedó aislado en `benchmark_vision_b1/`.

**Pendiente:** referencia humana independiente. No se declara B4 finalizado.
