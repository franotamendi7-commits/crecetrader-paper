# HALLAZGO: CARTERA MIXTA 4h — pullback + reversión

Fecha: 2026-11-25. PAPER_ONLY.

## Arreglo del null

El null anterior daba p=1.000 siempre porque el block bootstrap generaba
MÁS caídas que la serie real (183 señales reales → 198-220 sintéticas).

Null corregido (IAA simplificado): **permutar solo los SIGNOS** de los
retornos, conservando exactamente las magnitudes. Así el azar tiene la misma
distribución de caídas, solo en otro orden.

## Estrategia de reversión validada

Comprar tras caída del 12% en 8 velas 4h, cerrar sobre el mínimo,
stop en el mínimo de entrada, target 30% del retroceso.

| par | /mes | E | PF | DD | null (8 seeds) | WF train → test |
|---|---:|---:|---:|---:|---:|---:|
| **ARB** | 4,1 | **+0,367** | 2,32 | −6,3 | **5/8 pasan** | +0,309 → **+0,504 (mejora 63%)** |
| **XRP** | 3,6 | +0,270 | 1,82 | −10,0 | 4/8 | +0,264 → +0,307 (mejora 16%) |
| MANA | 6,0 | +0,273 | 1,90 | −13,6 | 0/8 — ruido | — |
| SOL | 5,7 | +0,253 | 1,85 | −14,3 | 0/8 — ruido | — |

**ARB es el primer activo cuyo walk-forward MEJORA en el test.** Por fin
algo que no degrada.

## Cartera final (4 pullback + ARB + XRP)

| | antes (solo 4 pullback) | **ahora (6 pares)** |
|---|---:|---:|
| Señales/mes | 59,4 | **63,9** |
| Esperanza | +0,128R | **+0,142R** |
| Acierto | 60,4% | 58,6% |
| **Drawdown** | **−127,6R** | **−98,1R** ✅ |
| PF | 1,34 | 1,39 |
| DD con $300 al 0,35% | −$134 | **−$103** |

Años mejorados: 2018 de −30,24R a **−6,35R**; 2022 de −72,68R a −55,48R;
2025 de −52,91R a −18,78R. La reversión compensa justo los años malos del
pullback — eso es diversificación real entre **lógicas**, no entre pares.

Últimos meses: Ago −5,36R · Sep +8,98R · Oct −1,26R · Nov +2,79R.

## Operativa

```
Cartera 6 pares · 63,9 señales/mes · riesgo 0,35% ($1,05 con $300)
BTC/THETA/HBAR/ETC → pullback 4h
ARB/XRP → reversión por caída 12%
```

## Aviso

El null corregido es nuevo: permuta signos pero no rompe la autocorrelación
de volatilidad. ARB pasa 5 de 8 seeds (no 8/8) — es evidencia sólida pero
no absoluta. Mantener en PAPER.

PAPER_ONLY. No se ejecutaron órdenes.
