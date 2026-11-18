# Tu anotación — ground truth del sensor visual

**Para qué**: es la única forma de saber si el VLM **lee bien** los gráficos. Sin esto, el VLM es
un oráculo que no validaste.

**Dónde**: `daily_pilot/vision_mission/TU_ANOTACION.csv` (ya tiene 5 filas del video `LFHkc5dUoLw`,
puedés ampliarla a 19).

**Cómo**: mirás el frame y anotás **lo que VOS ves**. No hace falta que sea perfecto: es tu referencia.

| columna | qué ponés |
|---|---|
| `instrumento` | BTCUSD · ETHUSD · SPX · QQQ · XAUUSD |
| `tf` | 4H · diario · semanal · 1H |
| `estructura` | maximos_crecientes · minimos_decrecientes · rango · ruptura |
| `niveles_que_se_ven` | separados por `;` → ej: `69000; 71509; 72554` |
| `vela` | verde · roja · indecision |
| `vos_que_harias` | **tu lectura** en una frase (esto es lo más valioso) |

**Frames**: `frames/scene_*.jpg` (abrires con Preview/Doble clic).

**Importante**: si algo no se ve, dejálo vacío. **No inventes** — el VLM tampoco debería.

---

## Con qué se compara

```bash
python3 daily_pilot/scripts/comparar_vision.py \
    --humano daily_pilot/vision_mission/TU_ANOTACION.csv \
    --vlm /tmp/vision_19.json
```

Te da: acuerdo por campo y cuántos de **tus** niveles aparecieron en la lectura del VLM.

## El criterio para decidir

- Si el VLM acierta **estructura e instrumento** en la mayoría → **sensor usable**.
- Si los **niveles** no coinciden con los tuyos → el VLM **no** puede proponer; solo puede
  **ayudarte a mirar**.
- **Nunca** lo usamos para decidir: solo para **mostrarte** lo que hay.

> Con 19 frames es una **muestra**, no una métrica final. Para una métrica seria harían falta
> cientos — pero para decidir «¿el VLM sirve o no?», 19 bien anotados alcanzan.
