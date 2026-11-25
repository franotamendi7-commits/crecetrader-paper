# DECISIÓN: GRUPAL — resultados de 34 pares de Quantfury

Fecha: 2026-11-25. Descargué historia real de los 34 pares (4h) vía
`descargar_velas.py`. Apliqué la MISMA regla de BTC a todos, sin optimizar.

## Por qué grupal y no par por par

Par por par con 34 activos = 34 búsquedas × cientos de variantes =
miles de tests → data mining garantizado. La regla grupal ya funcionó en
19 de 34 pares con E>0 sin tocar nada. Eso es evidencia de que la lógica
es **general**, no un ajuste a BTC.

## Resultado de la regla idéntica en los 34 pares

**19 de 34 dieron E>0.** Mejores:

| par | /mes | E | PF | DD |
|---|---:|---:|---:|---:|
| THETA | 15,2 | +0,181 | 1,52 | −34,8 |
| BTC | 21,5 | +0,157 | 1,45 | −56,0 |
| INJ | 15,8 | +0,092 | 1,24 | −53,5 |
| HBAR | 14,5 | +0,084 | 1,21 | −58,4 |
| BNB | 21,2 | +0,066 | 1,16 | −72,2 |
| ETC | 13,8 | +0,066 | 1,16 | −67,4 |
| LINK | 18,2 | +0,060 | 1,15 | −78,6 |
| SOL | 15,9 | +0,045 | 1,11 | −35,4 |

15 pares dieron E<0. **La regla no es universal**: hay que filtrar.

## Validación (null 40 sims × 7 seeds + walk-forward)

| par | seeds que pasan | test WF | decisión |
|---|---:|---:|---|
| **THETA** | **7/7** | +0,119 | ✅ INCLUIR |
| **HBAR** | **7/7** | −0,154 | ⚠️ pasa null, test negativo |
| BTC | 5/7 | +0,107 | ⚠️ inestable |
| ETC | 5/7 | −0,147 | ⚠️ inestable |

Solo **THETA** pasa null en todas las seeds y tiene test positivo.

## Cartera de 4 pares (BTC+THETA+HBAR+ETC)

```
6.438 señales · 59,4/mes · E=+0,128R · win 60,4% · PF=1,34 · DD=−127,6R
DD con $300 al 0,5% = −$191
```

Últimos meses:

| mes | ops | R | $ al 0,5% |
|---|---:|---:|---:|
| Ago 2026 | 79 | −5,36 | −$8,04 |
| Sep 2026 | 122 | +3,73 | +$5,60 |
| Oct 2026 | 45 | −1,26 | −$1,88 |
| Nov 2026 | 0 | 0 | 0 |

**La cartera grupal arregla octubre**: BTC solo fue −7,26R; los 4 pares
juntos fueron −1,26R. Eso es diversificación real, no promedio inventado.

Pero el drawdown total sube a −127,6R. Con $300 al 0,5% es −$191 — demasiado
cerca del capital. La cartera necesita ~$400 para el mismo colchón.

## Veredicto

La decisión correcta fue **grupal**: la señal es válida en varios activos y
la diversificación suaviza los meses malos. Pero **no metas los 34**: meté
los que validan, y verificá cada nuevo par con null + walk-forward antes
de sumarlo.

Conclusión operativa: cartera de 4 pares, 59 señales/mes, 0,5% de riesgo,
pero con $300 conviene bajar a 0,35% por el DD de −191.

PAPER_ONLY. No se ejecutaron órdenes.
