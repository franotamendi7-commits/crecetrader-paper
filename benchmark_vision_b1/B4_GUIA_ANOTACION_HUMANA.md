# B4 — Guía de anotación humana

Para dos anotadores independientes. Video `LFHkc5dUoLw`, 20 frames (`frame_3994`–`frame_4013`).

## 1. Cómo completar una ficha

1. Abrí la ficha `B4_fichas_anotacion/ficha_frame_XXXX.jpg.md`.
2. Mirá **solo** la imagen original indicada (o la copia verificada en `entregas_a74/LFHkc5dUoLw/`).
3. Completá cada campo de la tabla con lo que veas. Si no se lee, dejá `NO LEGIBLE` / `NO PRESENTE`.
4. En la lista de precios, transcribí **exactamente** los valores que tienen etiqueta visible.
5. Al final, volcá tus respuestas a tu CSV personal (`anotador1.csv` / `anotador2.csv`) usando la estructura de `B4_referencia_humana_template_v2.csv` (la vigente) y las reglas de `B4_ESQUEMA_ANOTACION.md`.
6. **No** consultes al otro anotador ni sus respuestas.

## 2. Cómo identificar un precio visible

Un precio es **visible** solo si aparece **escrito** en la imagen:
- En el eje de precios (ej. `87.496`).
- En una etiqueta/cuadro sobre una línea (ej. `78746`).
- En una herramienta dibujada (Fibonacci, pivot, etc.).

Si solo **infiero** un nivel por dónde pasa una línea, pero no está escrito, **no** lo anotes como precio visible. Anotalo en `horizontal_levels` como línea sin etiqueta.

Si un dígito es dudoso → `NO LEGIBLE` para ese nivel.

## 3. Línea horizontal vs directriz

- **Línea horizontal**: no tiene pendiente; marca un nivel de precio (soporte/resistencia/zona). Viven en `horizontal_levels`.
- **Directriz (trendline)**: tiene pendiente (ascendente o descendente); une máximos o mínimos. Viven en `trendlines`.
- Si una línea podría ser ambas cosas o no está claro su rol → describila y marcá `role: UNKNOWN`. **No** le asignes una función arbitraria.

## 4. Clasificar la legibilidad

| Código | Significado |
|---|---|
| 1 | Claramente legible |
| 2 | Parcialmente legible (se entiende con duda razonable) |
| 3 | No legible |
| 4 | No presente en la imagen |

Aplicá el código **por campo**, no por frame.

## 5. Cuándo usar `NO LEGIBLE`

- El texto existe pero no se alcanza a leer (tamaño, compresión, obstrucción).
- Un dígito es dudoso.
- El gráfico está tapado por la ventana del presentador o por la franja publicitaria.

## 6. Cuándo usar `NO PRESENTE`

- El elemento **no existe** en la imagen (ej. no hay panel de volumen, no hay Fibonacci, no hay zonas de liquidez dibujadas).

No confundas `NO LEGIBLE` (existe, no se lee) con `NO PRESENTE` (no existe).

## 7. Cómo registrar dudas

- Usá la columna de confianza (1-5) para expresar **certeza**, nunca para habilitar un valor inventado.
- Si existe texto pero **no podés determinar el valor exacto con seguridad**, anotá `NO LEGIBLE`. No escribas el valor "más probable".
- Dejá constancia de la duda en `notes` o en `abstentions`.
- La confianza alta exige un valor claramente visible; la confianza baja implica `NO LEGIBLE` o abstención.

**Criterio definitivo (coherente con el protocolo de evaluación):**

| Situación | Registro |
|---|---|
| Valor claramente visible | Transcribir el valor exacto |
| Existe texto pero el valor exacto no es determinable con seguridad | `NO LEGIBLE` |
| El elemento no existe en la imagen | `NO PRESENTE` |
| No sabés / no se ve | `NO LEGIBLE` |

Queda **prohibido** completar dígitos por intuición o usar conocimiento de trading para reconstruir precios. La confianza no habilita a inventar ni completar información.

## 8. Por qué no deducir precios ni niveles

- Una deducción es una **hipótesis**, no un dato. Si se usa como referencia, el benchmark mide si el modelo **adivina como el anotador**, no si lee el gráfico.
- El objetivo es medir **lectura real**. Solo cuenta lo escrito en la imagen.
- Los niveles que no tienen etiqueta **no** son precios visibles.

## 9. Por qué los dos anotadores deben trabajar independientes

- El acuerdo entre dos personas es la única forma de distinguir un dato objetivo de una interpretación personal.
- Si se consultan, el acuerdo se infla artificialmente y el benchmark pierde validez.
- Los desacuerdos **no son un problema**: son información. Se resuelven por adjudicación de un tercero.

## 10. Distribución propuesta de las 20 fichas

**Opción recomendada (doble ciego completo):** los dos anotadores reciben **las mismas 20 fichas** y las completan por separado. Coste: 20 fichas × 2 personas.

**Opción alternativa (si el tiempo es limitado):**
- **10 fichas comunes** (5 por video/tramo) → miden el acuerdo.
- **5 exclusivas** para el anotador 1 y **5 exclusivas** para el anotador 2 → amplían cobertura.
- En el acuerdo solo entran las 10 comunes.

**Reglas:**
- Mismas imágenes, mismo enunciado, mismo orden.
- Sin comunicación entre anotadores hasta entregar.
- Cada uno entrega su CSV con su nombre.
- No se combinan resultados antes de la adjudicación.

## 11. Prohibido

- Completar campos por intuición o conocimiento de trading.
- Usar las respuestas del modelo.
- Copiar de el otro anotador.
- Modificar las imágenes.
