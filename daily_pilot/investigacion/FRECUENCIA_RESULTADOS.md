# ESTRATEGIAS DE ALTA FRECUENCIA — resultados reales

Fecha: 2026-11-25. Datos: Binance BTCUSDT/ETHUSDT 4h (9,3 años).
Método: mismo null sintético (block bootstrap, 80 sims) y walk-forward 70/30
que la estrategia lenta. Sin comisiones (Quantfury no cobra). PAPER_ONLY.

## Hallazgo estructural

La estrategia lenta (ruptura de tramo) da 0,5 señales/mes porque su filtro
exige tramos de ≥5 días. Incluso sin filtro da solo 5,7/mes en 4h. **El setup
es estructuralmente lento**: cambiar el filtro no alcanza.

## 1 · Mean-reversion en rango — NO SIRVE

| variante | /mes | E(R) | DD | PF | null p | veredicto |
|---|---:|---:|---:|---:|---:|---|
| BTC lb12 8% tk0.5 | 9,3 | +0,002 | −58,4 | 1,00 | 0,975 | **RUIDO** |
| BTC lb20 10% tk0.5 | 6,8 | −0,016 | −52,6 | 0,97 | — | perdedora |
| BTC lb50 15% tk0.5 | 3,1 | −0,209 | −80,9 | 0,72 | — | perdedora |
| ETH lb12 8% tk0.5 | 6,4 | −0,047 | −54,1 | 0,92 | — | perdedora |
| ETH lb30 12% tk0.5 | 2,6 | +0,199 | −15,3 | 1,33 | 0,412 | **RUIDO** |

Walk-forward BTC: train +0,019R → test −0,022R (**−216%**).
**Descartada.** Comprar soportes en 4h no funciona en BTC.

## 2 · Pullback en tendencia — SÍ PASA EL NULL, pero débil

| variante | ops | /mes | E(R) | win% | DD | PF | null p | veredicto |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| BTC ema13 tR2 | 2880 | **25,9** | +0,136 | 37,7 | −67,0 | 1,22 | **0,000** | **PASA** |
| BTC ema34 tR2 | 1395 | 12,5 | +0,176 | 38,8 | −41,0 | 1,29 | **0,000** | **PASA** |
| ETH ema13 tR2 | 2675 | **24,0** | +0,135 | 37,7 | −100,0 | 1,22 | **0,000** | **PASA** |

### Walk-forward (70/30)

| variante | train E | test E | degradación |
|---|---:|---:|---:|
| BTC ema13 | +0,188 | +0,033 | **−82,4%** |
| BTC ema34 | +0,232 | +0,056 | **−75,9%** |
| ETH ema13 | +0,146 | +0,071 | −51,4% |

## Comparación con la estrategia lenta

| | lenta (ruptura) | pullback ema13 |
|---|---:|---:|
| señales/mes | 0,5 | **25,9** |
| E(R) | **+1,237** | +0,136 |
| DD(R) | **−6,3** | −67,0 |
| null p | 0,020 | 0,000 |
| WF degradación | — | −82% |

## Veredicto honesto

**El pullback logra la frecuencia que pediste (≈25/mes) y su venta es real
(p=0,000 contra el azar), pero la esperanza es 9 veces menor y el drawdown
10 veces mayor.** Con $300 al 1% ($3/op) son +$10/mes esperados con un DD
esperado de −$201. No es estructuralmente operable con ese capital.

Siguiente paso lógico: reducir el drawdown del pullback con un filtro de
régimen (solo operar cuando EMA50 tiene pendiente positiva) y/o subir el
target a 3R. Eso se mide, no se asume.

## No usar

Los números de 1h con E=+3,8R a +12,9R son **artefactos**: el stop de 3 velas
1h es demasiado ajustado y infla el denominador de R. Descartados.

PAPER_ONLY. No se ejecutaron órdenes.
