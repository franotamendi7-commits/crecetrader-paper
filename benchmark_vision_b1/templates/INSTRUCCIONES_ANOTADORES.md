# Instrucciones para anotadores — Benchmark de visión A.7.4

Propósito: construir una **referencia humana independiente** de lo que realmente muestra cada frame, para evaluar la fiabilidad del modelo `qwen2.5vl:3b`.

## Principios obligatorios

1. **NO CREER. PROBAR.** Anotá solo lo que veás en la imagen.
2. **No uses las respuestas del modelo** como referencia. Si ya viste una respuesta automática, ignorala.
3. **No deduzcas** nada por contexto (ni por el título del video, ni por lo que se dice en el audio, ni por tu conocimiento de trading).
4. Si un campo **no se lee con claridad**, anotá `NO LEGIBLE`. No completes con lo que "debería" ser.
5. Los números se transcriben **exactamente como aparecen**. Si un dígito es dudoso, anotá `NO LEGIBLE` para ese nivel.

## Campos

| Campo | Valores |
|---|---|
| `frame_id` | ID único (ya viene relleno) |
| `video_id` | ID del video (ya viene relleno) |
| `idx` / `pts_time` | Índice y segundo del frame (ya vienen rellenos) |
| `instrument` | Uno de: `BTCUSD`, `ETHUSD`, `ES`, `NQ`, `XAUUSD`, `AMD`, `MDT`, `SPX`, `SP500`, `NDX`, `OTHER` (escribí cuál), `NO LEGIBLE` |
| `timeframe` | `Weekly`, `Daily`, `4H`, `1H`, `15m`, `5m`, `NO LEGIBLE` |
| `price_levels` | Lista de **niveles con etiqueta visible** en el gráfico, separados por `;`. Solo los que tienen etiqueta escrita. Máximo 12. Si no se ven, `NO LEGIBLE` |
| `indicators` | Separados por `;` de: `MA` (medias móviles), `Fibonacci`, `Volume`, `none`. Si no se ven, `none` |
| `structure` | `trend`, `range`, `support`, `resistance`, `NO LEGIBLE` |
| `legible_*` | `si` / `no` por cada campo |
| `abstencion` | Qué campo o dato **no pudiste leer** (o `ninguno`) |
| `certainty_1_5` | 1 = duda mucho, 5 = totalmente seguro |
| `timestamp_source` | `pts_time verificado` (por defecto) o `NO VERIFICABLE` |
| `notes` | Observaciones breves (opcional) |

## Procedimiento

1. Abrí el **contact sheet** del video (o el frame individual).
2. Para cada frame, mirá el gráfico y anotá los campos.
3. **Precios**: si el eje muestra "87.496" y el gráfico tiene una línea etiquetada "87496", anotá `87496`. Si hay varias etiquetas, anotá todas. Si el número está borroso, `NO LEGIBLE`.
4. **Instrumento**: usá la marca de agua / título del gráfico (ej. "BTCUSD, 1D"). Si el exchange o el par no es legible, `NO LEGIBLE`.
5. **Temporalidad**: usá el indicador de período (1D, 4H, etc.). Si no aparece, `NO LEGIBLE`.
6. Guardá tu CSV **con tu nombre** (ej. `anotador1.csv`).

## Prohibido

- Rellenar por intuición.
- Usar las predicciones del modelo.
- Copiar de otro anotador.
- Modificar los frames o los archivos de production.

## Doble anotado y desacuerdos

Cada frame será anotado por **dos personas de forma independiente**. Luego se compararán los CSV:
- Si coinciden → `adjudicado = acuerdo`.
- Si difieren → un **tercero** revisa y decide; se registra el desacuerdo y la resolución.

Ver `ADJUDICACION.md`.
