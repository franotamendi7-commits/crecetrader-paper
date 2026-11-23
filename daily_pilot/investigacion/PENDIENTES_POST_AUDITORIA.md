# Pendientes para cuando vuelva DeepSeek

Ancla: `45ae824` (rama `crecetrader-limpio`) · 2026-11-23

La idea es **hacerlo todo junto** después del veredicto de la auditoría
(`PROMPT_AUDITORIA_5_HERRAMIENTAS.md`).

## A · Lo que pidió Francisco (anotado)

1. **Test de humo del dashboard**
   Verificar que los paneles nuevos (**ALERTAS DE NIVEL**, **BACKTEST DE NIVELES**)
   cargan bien y no rompen nada: HTML autocontenido, sin errores, números reales.
   Hoy: `generar_dashboard_v5.py` corre OK (56 KB, 0 SVG).

2. **Mejorar `canal_acierta.py`**
   Hoy usa `st_mtime` del archivo como fecha y **todos los vídeos se procesaron el
   mismo día** → da 6,1%, un número que **no significa nada**.
   Hay que:
   - buscar la fecha real de publicación (YouTube data API / metadata del vídeo)
   - exigir un mínimo de días posteriores para evaluar
   - y marcar cuántos vídeos tienen muestra suficiente

3. **Ver si DeepSeek marca P0/P1** en las 5 herramientas y aplicar lo que corresponda

## B · Ya hecho (para no repetir)

| # | herramienta | evidencia |
|---|---|---|
| 1 | `agente_ticket.py` | BTC 4H → `no_operar`, tramo 55.130→86.999 |
| 2 | `alertas_niveles.py` | BTC a 0,35% del concordante 61.247 |
| 3 | `backtest_niveles.py` | BTC 1D: 72,9% rebote medio |
| 4 | `canal_acierta.py` | ⚠️ sin histórico util |
| 5 | `paper_trading.py` | abrir/cerrar/resumen OK |

Suite: **15/15** y **16/17**. Dashboard sin barras (0 SVG).

## C · Advertencias ya conocidas (del prompt)

- **Backtest**: `detalle=90` velas → muestra chica, tasas poco significativas.
- **Alertas**: `concordancia()` asume BTC cuando el nivel no trae par.
- **Paper**: resultado USD = `res% × 1000 × riesgo_pct/2`; no contempla comisión
  ni deslizamiento.
- **`canal_acierta`**: sin fecha de publicación real.

## D · Decisión de Francisco

**Ni un centavo en Vembit** (ni en ninguna plataforma nueva). Solo curiosidad;
no se integra su API al sistema.
