# RONDA 4: REVERSION SEMANAL — no se puede validar (artefacto del null)

Fecha: 2026-11-25. PAPER_ONLY.

## Intento

Comprar después de caídas fuertes (8% en 8 velas o 12% en 8 velas 4h),
cerrar sobre el mínimo, stop en el mínimo de entrada, target 30-100% del
retroceso. Estructuralmente distinto a todo lo anterior: **no necesita
tendencia alcista**.

## Números sin validar

**30 de 30 pares dieron E>0**, con DD bajos:

| par | /mes | E | PF | DD |
|---|---:|---:|---:|---:|
| ARB | 4,1 | +0,367 | 2,32 | −6,3 |
| MANA | 6,0 | +0,273 | 1,90 | −13,6 |
| XRP | 3,6 | +0,270 | 1,82 | −10,0 |
| INJ | 9,0 | +0,268 | 1,93 | −10,9 |
| STX | 7,8 | +0,268 | 1,88 | −14,8 |
| SOL | 5,7 | +0,253 | 1,85 | −14,3 |
| AAVE | 18,4 | +0,216 | 1,66 | −27,9 |

Walk-forward: ARB train +0,309 → test +0,504 (**mejora**). MANA +0,271 →
+0,295. XRP +0,264 → +0,307. Son los primeros tests que NO degradan.

## PROBLEMA: el null no es válido para este setup

Todos dieron **p=1.000 (0 de 7 seeds)**. Diagnosticado:

```
señales REALES (ARB):  183
señales NULL:          198, 200, 220
```

El block bootstrap **genera más caídas artificiales** que la serie real,
así que el "azar" gana más que la estrategia. El p-valor sale 1,0 por un
artefacto del generador de series sintéticas, **no porque la estrategia sea
ruido**.

Esto significa una de dos cosas:
1. La estrategia es real y el null necesita preservar la distribución de
   caídas (no solo bloques de retornos), o
2. La estrategia es ruido y el null actual no lo detecta.

**No puedo decidirlo con la herramienta que tengo.** Por eso NO la agrego
a la cartera. Meterla sería saltarse la validación que pediste.

## Lo que haría falta

Un null que conserve la **frecuencia y magnitud de las caídas** (por
ejemplo block bootstrap condicionado por tramo, o permutar las señales
dentro de regímenes similares). Eso es trabajo nuevo, no un parche de dos
líneas.

## Estado final

| Estrategia | Estado |
|---|---|
| Cartera 4h (BTC+THETA+HBAR+ETC) | ✅ Única validada |
| Reversión semanal | ⚠️ Prometedora, **sin validar** |
| Ruptura con volumen | ❌ Ruido |
| Pullback en otros 30 pares | ❌ Ruido |
| Short / 1d / ML / correlación | ❌ Descartados |

PAPER_ONLY. No se ejecutaron órdenes.
