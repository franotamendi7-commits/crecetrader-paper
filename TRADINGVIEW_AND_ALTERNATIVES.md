# TradingView y Alternativas — YouTube Trading Agent

## TradingView (plan gratuito)

### Funciones disponibles gratuitamente
- Graficos basicos (1 grafico por pestana)
- Indicadores basicos (RSI, MACD, MA, Bollinger, etc.)
- Pine Script (editor, compilacion, backtesting basico)
- Alertas (limitadas: 1-2 alertas activas)
- Datos en tiempo real (limitados por exchange)
- Comunidad (scripts publicos)

### Limitaciones del plan gratuito
- 1 grafico por pestana (no multi-chart)
- Indicadores limitados (max 2-3 por grafico)
- Alertas limitadas (1-2 activas)
- Sin exportacion de datos
- Sin acceso a datos historicos extendidos
- Sin API de datos (no se puede automatizar la lectura)
- Sin webhooks avanzados
- Datos con retraso en algunos exchanges

### Pine Script (disponible en plan gratuito)
- Se puede escribir, compilar y ejecutar
- Se puede publicar en la comunidad
- Backtesting basico disponible
- No se puede automatizar la ejecucion
- No se puede acceder a datos externos

### Restricciones de automatizacion
- No se puede automatizar la lectura de datos de TradingView
- No se puede hacer scraping de graficos
- No se puede usar bots para interactuar con la plataforma
- Los terminos de servicio prohiben acceso automatizado

## Alternativas open source

### 1. Lightweight Charts (TradingView oficial)
- **URL:** https://github.com/nicholasgasior/lightweight-charts (o repo oficial de TradingView)
- **Licencia:** Apache 2.0
- **Coste:** $0
- **Funcion:** Graficos financieros interactivos (OHLCV, lineas, areas)
- **Ventajas:** Calidad visual profesional, mantenido por TradingView, sin dependencias
- **Limitaciones:** No tiene Pine Script, no tiene indicadores built-in
- **Uso:** Reconstruir graficos desde datos OHLCV para comparar con el analista

### 2. Plotly
- **URL:** https://github.com/plotly/plotly.py
- **Licencia:** MIT
- **Coste:** $0
- **Funcion:** Graficos interactivos (incluye candlestick, OHLC)
- **Ventajas:** Muy flexible, soporta muchos tipos de graficos
- **Limitaciones:** Mas pesado que Lightweight Charts

### 3. mplfinance
- **URL:** https://github.com/matplotlib/mplfinance
- **Licencia:** BSD
- **Coste:** $0
- **Funcion:** Graficos financieros con matplotlib
- **Ventajas:** Simple, integrado con pandas
- **Limitaciones:** Estatico (no interactivo)

### 4. TA-Lib / pandas-ta
- **URL:** https://github.com/TA-Lib/ta-lib-python / https://github.com/twopirllc/pandas-ta
- **Licencia:** BSD / MIT
- **Coste:** $0
- **Funcion:** Indicadores tecnicos (RSI, MACD, etc.)
- **Ventajas:** 100+ indicadores, compatible con pandas
- **Uso:** Calcular indicadores mencionados por el analista

## Recomendacion

- **Para visualizacion:** Lightweight Charts (calidad profesional, $0)
- **Para indicadores:** pandas-ta (100+ indicadores, $0)
- **Para reconstruccion de graficos:** Lightweight Charts + datos OHLCV de Kraken/Yahoo
- **TradingView:** Usar solo para referencia visual (plan gratuito), no como dependencia

## Estrategia de reconstruccion de graficos

1. Obtener datos OHLCV de fuente gratuita (Kraken, Yahoo Finance)
2. Calcular indicadores mencionados por el analista (pandas-ta)
3. Reconstruir grafico con Lightweight Charts (HTML interactivo)
4. Comparar con el grafico del analista (screenshot)
5. Documentar diferencias y similitudes

## Nota sobre TradingView

TradingView es la plataforma preferida del analista. No se contratará plan de pago. Se usará el plan gratuito solo para referencia visual. La reconstrucción de graficos se hará con herramientas open source (Lightweight Charts) a partir de datos gratuitos.
