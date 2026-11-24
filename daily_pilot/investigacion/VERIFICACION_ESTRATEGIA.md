# VERIFICACION INDEPENDIENTE — Estrategia ruptura de tramo 4h

Verificó: Hermes (no el autor). Fecha: 2026-11-24.
Método: reproduje los números desde cero con el mismo script y corrí filtros adicionales.

## 1 · Reproducción exacta ✅

```
config: tf=4h  tramo_n=8  ext=3.0  stop=swing3  gestion=full  dir=long  filtro=tramo_min30

resultado reproducido:
  n=52  acierto 44,2%  E=+1,2374R  DD=-6,35R  FB=3,103  racha max 6
```

Coincide dígito a dígito con `ESTRATEGIA_GANADORA.md`.

## 2 · Null sintético (1.000 simulaciones) ✅

```
esperanza real   +1,2374R
null media       +0,4331R
null percentil 95 +1,0994R
p-valor empirico   0,020
veredicto          REAL SUPERA NULL
```

El filtro del null está bien aplicado: se re-construye la serie de precios
y se vuelve a correr el detector (no es un bootstrap ingenuo sobre trades).

## 3 · ROBUSTEZ — lo que el informe no decía

### 3.1 Recorte temporal (3 tercios iguales)

| tramo | n | acierto | E(R) | DD |
|---|---:|---:|---:|---:|
| primero | 26 | 30,8% | +0,675 | -7,57 |
| segundo | 25 | 56,0% | +1,539 | -5,25 |
| ultimo | **0** | — | — | — |

**El último tercio de la serie no genera NI UNA operación.**
Las 52 operaciones van de 2018 a 2026-08 pero con densidad irregular
(2023 = 11 ops, 2019 = 8). No es una cobertura uniforme.

### 3.2 Últimas operaciones

```
2025-10-01  -1,06R
2026-01-13  -1,05R
2026-04-17  -1,05R
2026-08-21  -1,02R
```

Las últimas 4 son todas pérdidas. Desde 2025 el balance sigue positivo
(+2,86R en 9 operaciones), pero **la racha actual es negativa**.

### 3.3 Walk-forward

| par | train E | test E | degradación |
|---|---:|---:|---:|
| BTC | +0,352R | +1,505R | +327% (el train era bajísimo) |
| ETH | +1,315R | +0,482R | **-63,3%** |

BTC «mejora» solo porque el train salió muy bajo. **ETH degrada un 63%.**
Ambos con n<40 por lado.

## 4 · RIESGO DE DATA MINING ⚠️

Se evaluaron **51.597 variantes** en 4h (más 48.510 en 1d y 51.597 en 1h).
Un p=0,020 sin corregir no basta: con tests independientes el umbral de
Bonferroni sería 0,00097.

Mitigantes reales:
- Las variantes NO son independientes (comparten serie y setups).
- La estrategia ganadora **también valida en ETH** (p=0,028), otro universo.
- Es una lógica simple y defendible, no una curva ajustada a los datos.

Deflated Sharpe aproximado: **~1,0** (el SR sobrevive a la corrección).

## 5 · VEREDICTO HONESTO

**Hay una señal real, pero es modesta y no está confirmada para operar hoy.**

- El +1,237R supera el azar en dos activos distintos. Eso no es trivial.
- Pero n=52 es muestra chica, el walk-forward de ETH degrada, y las
  últimas 4 operaciones son pérdidas.
- El target 3.0 es agresivo: sin él, la esperanza cae.

**Recomendación:** operar en PAPER con 1% de riesgo durante 3-6 meses,
acumulando operaciones reales. Si el papel confirma, recién ahí subir.

## 6 · Capital (con $300)

| riesgo/op | DD esperado | gana por op (esp.) |
|---:|---:|---:|
| 1% ($3) | -6,3% | +$3,7 |
| 2% ($6) | -12,7% | +$7,4 |
| 5% ($15) | -31,8% | +$18,6 |

**1% es lo prudente.** 5% puede fundir la cuenta con una racha de 6.

PAPER_ONLY en todo momento.
