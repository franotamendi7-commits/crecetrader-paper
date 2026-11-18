# Catálogo de APIs Gratuitas — YouTube Trading Agent

## APIs de Mercado (sin suscripción)

### 1. Kraken (YA EN USO)
- **URL:** https://www.kraken.com/features/api
- **Cobertura:** Crypto (BTC, ETH, etc.)
- **OHLCV:** Si (1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w)
- **Histórico:** Si (limitado por llamada)
- **API key:** No requerida para datos públicos
- **Límites:** Rate limited (sin límite diario estricto para datos públicos)
- **Coste:** $0
- **Estado:** YA VERIFICADO Y EN USO

### 2. CoinGecko (free tier)
- **URL:** https://www.coingecko.com/en/api
- **Cobertura:** Crypto (BTC, ETH, etc.)
- **OHLCV:** Si (1d, limitado)
- **Histórico:** Si (limitado)
- **API key:** Opcional (free tier sin key, 10-30 calls/min)
- **Límites:** 10-30 calls/min (free), 10,000 calls/mes
- **Coste:** $0 (free tier permanente)
- **Riesgo:** Free tier puede cambiar

### 3. Yahoo Finance (via yfinance)
- **URL:** https://github.com/ranaroussi/yfinance
- **Cobertura:** Stocks, ETFs, indices, crypto, forex
- **OHLCV:** Si (1m, 5m, 15m, 30m, 1h, 1d, 1w, 1mo)
- **Histórico:** Si (amplio)
- **API key:** No requerida
- **Límites:** Rate limited (sin límite oficial, pero puede bloquear)
- **Coste:** $0
- **Riesgo:** No oficial, puede cambiar/bloquear

### 4. Alpha Vantage (free tier)
- **URL:** https://www.alphavantage.co/
- **Cobertura:** Stocks, forex, crypto, indices
- **OHLCV:** Si (intraday y daily)
- **Histórico:** Si (limitado en free tier)
- **API key:** Requerida (free)
- **Límites:** 25 calls/día (free tier)
- **Coste:** $0 (free tier permanente)
- **Riesgo:** Límite muy bajo (25/día)

### 5. OHLC.io (free tier limitado)
- **URL:** https://ohlc.io
- **Cobertura:** Stocks, ETFs, crypto, indices
- **OHLCV:** Si (daily, 5m, 1h, 1m para crypto)
- **Histórico:** Si
- **API key:** Requerida
- **Límites:** Free tier: solo AAPL, NVDA, JNJ, PEP, MSFT, SPY, QQQ (7 símbolos)
- **Coste:** $0 (free tier permanente)
- **Riesgo:** Free tier muy limitado

### 6. Databento ($125 créditos iniciales)
- **URL:** https://databento.com
- **Cobertura:** US stocks, ETFs (no crypto)
- **OHLCV:** Si (tick, minute, hour, day)
- **Histórico:** Si
- **API key:** Requerida
- **Límites:** $125 créditos iniciales (no permanente)
- **Coste:** $0 inicial, luego pago
- **Riesgo:** Créditos se agotan

### 7. Binance Public API (BLOQUEADO)
- **URL:** https://api.binance.com
- **Cobertura:** Crypto
- **Estado:** BLOQUEADO (451 geoblock desde Argentina)
- **Coste:** $0 (si fuera accesible)
- **Riesgo:** Geoblock permanente

## Resumen de cobertura para universo inicial

| Instrumento | Kraken | CoinGecko | Yahoo Finance | Alpha Vantage | OHLC.io |
|---|---|---|---|---|---|
| BTC | Si | Si | Si | Si | Si |
| ETH | Si | Si | Si | Si | Si |
| S&P 500 | No (ETF SPY) | No | Si (SPY/^GSPC) | Si | Si (SPY) |
| QQQ | No | No | Si | Si | Si (QQQ) |
| Oro | No (XAU) | No | Si (GC=F) | Si | No |

## Recomendación

- **Principal:** Kraken (crypto) + Yahoo Finance (stocks/ETFs/indices) — ambos $0, sin API key
- **Respaldo:** CoinGecko (crypto) + Alpha Vantage (stocks, con límite 25/día)
- **Evitar:** Binance (geoblock), OHLC.io (free tier muy limitado), Databento (créditos se agotan)

## Catálogos de APIs (referencia)

- https://github.com/public-apis/public-apis (catálogo de APIs gratuitas)
- https://github.com/n0shake/Public-APIs (otro catálogo)
- https://rapidapi.com/hub (marketplace, muchos free tiers)

## Nota sobre APIs gratuitas

No confundir "gratuito" con "open source". Una API gratuita puede:
- Cambiar sus límites sin aviso
- Dejar de ser gratuita
- Requerir registro y API key
- Tener rate limits estrictos
- Tener datos demorados

Siempre documentar riesgos y tener alternativas.
