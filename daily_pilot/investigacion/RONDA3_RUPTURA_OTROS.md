# ESTRATEGIA NUEVA PARA LOS OTROS 30 PARES — resultado

Fecha: 2026-11-25. PAPER_ONLY.

## Intento: ruptura de máximo con volumen

Setup opuesto al pullback: entrar cuando el precio ROMPE un máximo de
20/40/60 velas 4h, con volumen sobre su media, tendencia alcista y
retorno 30 velas positivo. Stop swing fijo, target Fib 1.5/2.0, 50% en 1R.

## Frecuencia y esperanza (sin validar)

**26 de 30 pares dieron E>0.** Mejores:

| par | /mes | E | PF | DD |
|---|---:|---:|---:|---:|
| SOL | 5,6 | +0,273 | 1,96 | −18,6 |
| DOGE | 3,9 | +0,253 | 1,96 | −12,5 |
| RUNE | 3,8 | +0,237 | 1,84 | −9,7 |
| **ETH** | 4,1 | +0,184 | 1,56 | −34,8 |
| UNI | 3,4 | +0,165 | 1,56 | −12,3 |
| ADA | 4,8 | +0,160 | 1,47 | −17,7 |

**ETH sí funciona con ruptura** (falló con pullback: p=0,217). Pero...

## Validación: TODOS salen RUIDO

| par | E | null p | WF train | WF test |
|---|---:|---:|---:|---:|
| SOL | +0,273 | 0,150 | +0,330 | +0,104 |
| DOGE | +0,253 | 0,150 | +0,246 | **+0,234** (−4,9%) |
| RUNE | +0,237 | 0,200 | +0,257 | +0,136 |
| ETH | +0,184 | 0,250 | +0,295 | **−0,278** |
| UNI | +0,165 | 0,200 | +0,114 | +0,303 |
| ADA | +0,160 | 0,075 | +0,204 | +0,069 |
| NEAR | +0,159 | 0,350 | +0,243 | −0,008 |
| LINK | +0,132 | 0,450 | +0,150 | +0,100 |

**0 de 8 validados** (ninguno pasa p≤0,05).

## Veredicto

Los números atractivos (E +0,27, PF 1,96) son **ruido**: el null sintético
los reproduce. Con solo 3-5 señales/mes el null tiene poco poder y el p
no baja de 0,075.

**DOGE es la única excepción interesante**: walk-forward casi sin degradación
(−4,9%) y test +0,234R, pero no pasa el null (p=0,150). Queda en observación,
no se incluye.

## Estado final

- Cartera 4h (BTC+THETA+HBAR+ETC) sigue siendo la única validada.
- Los otros 30 pares: **no hay estrategia validada** después de probar
  pullback, ruptura con volumen, mean-reversion y short.
- ETH: falla con pullback y con ruptura; queda afuera.

PAPER_ONLY. No se ejecutaron órdenes.
