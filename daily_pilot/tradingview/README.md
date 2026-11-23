# TradingView — indicador de niveles (C05)

`crecetrader_niveles.pine` — Pine v5. Pegar en el Pine Editor de TradingView.

## Pegarlo

1. TradingView → abrir un gráfico (ej. `BTCUSDT`)
2. Pestaña **Pine Editor** (abajo) → borrar todo → pegar el archivo
3. **Add to chart**
4. Para ver qué está calculando: encender **4 · Diagnostico**
   (label amarillo con `maxAlto`, `tramoMin`, `rango`, `swings`, `tf`)

## Qué dibuja

| bloque | niveles |
|---|---|
| **Retrocesos** | 0,382 / 0,5 / 0,61 / 0,786 |
| **Extensiones** | 1 / 1,25 / 1,5 / 1,75 / 2 / 3 (arriba del máximo) |
| **Abanico intradía** | cierre 21:00 ± fibo × 1.000 (solo TF ≤ 1D) |

## Reglas (validadas contra tus capturas, BNB 2026-11-20)

- Cada TF tiene su swing: **macro = semanal, micro = diario y 4h**
- Tramo = **máximo más alto → piso más bajo posterior**
- El fibo se tira **al revés**: `0 = mínimo`, `1 = máximo`
- Entradas: `n=3` (velas por extremo), `ventana=60` (swings)

## Verificación: simulación Python == motor

```
TF   pine simulado        motor Python         resultado
1w   503,75 -> 1375,11    503,75 -> 1375,11    IGUAL
1d   503,75 ->  809,99    503,75 ->  809,99    IGUAL
4h   503,75 ->  809,99    503,75 ->  809,99    IGUAL
```

## Cómo se arreglaron los bugs (v4)

- **`low[k]` acepta 0..5000** → el barrido es `for k = 0 to nBarras` con tope 4999.
  Un `for k = maxBar to bar_index` reventaba en 4H/1H
  (`Invalid number of bars back`) **y descuadraba los niveles**.
- **`request.security` suelto se ejecuta SIEMPRE** → va **dentro** del `if`.
- **Un solo array de swings** (no dos separados) → la `ventana` significa lo mismo
  que en Python.
- **El piso de hoy no está confirmado como pivote** → se barre explícitamente.

## Pendiente

**Compilación real**: no tengo acceso a TradingView; lo prueba Francisco.
Si tira error, el mensaje exacto se corrige en minutos.
