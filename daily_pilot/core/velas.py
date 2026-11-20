#!/usr/bin/env python3
"""Obtencion de velas (OHLC) para el motor.

Fuentes:
  1. Binance public API (solo lectura, sin firma) -> /api/v3/klines
  2. Fallback local: capturas de TradingView guardadas en daily_pilot/datos/velas/

La API key SOLO LECTURA va en ~/.hermes/.env (NUNCA en el repo). Las klines
publicas no requieren firma, asi que el piloto puede leer precios sin key.

PAPER_ONLY: lee, no ordena.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.request
from pathlib import Path

PAPER_ONLY = True

BASE = Path(__file__).resolve().parents[2]
DIR_VELAS = BASE / 'daily_pilot' / 'datos' / 'velas'
CACHE_SEGUNDOS = 300          # 5 min: no martillar la API
BINANCE = 'https://api.binance.com'

# intervalos de Binance
INTERVALOS = {'1m': '1m', '5m': '5m', '15m': '15m', '1h': '1h', '4h': '4h',
              '1d': '1d', '1w': '1w', '1M': '1M'}


def _cache_path(par: str, tf: str) -> Path:
    DIR_VELAS.mkdir(parents=True, exist_ok=True)
    return DIR_VELAS / f'{par}_{tf}.json'


def _leer_cache(par: str, tf: str) -> list[dict] | None:
    p = _cache_path(par, tf)
    if not p.exists():
        return None
    if time.time() - p.stat().st_mtime > CACHE_SEGUNDOS:
        return None
    try:
        return json.loads(p.read_text())['velas']
    except Exception:
        return None


def _escribir_cache(par: str, tf: str, velas: list[dict]) -> None:
    DIR_VELAS.mkdir(parents=True, exist_ok=True)
    _cache_path(par, tf).write_text(json.dumps(
        {'par': par, 'tf': tf, 'fuente': 'binance', 'velas': velas},
        indent=1, ensure_ascii=False))


def binance_klines(par: str, tf: str, limite: int = 500) -> list[dict]:
    """Velas de Binance. Sin key: endpoint publico."""
    intervalo = INTERVALOS.get(tf)
    if intervalo is None:
        raise ValueError(f'tf no soportada: {tf}')
    url = f'{BINANCE}/api/v3/klines?symbol={par}&interval={intervalo}&limit={limite}'
    req = urllib.request.Request(url, headers={'User-Agent': 'CreceTrader-pilot/0.1'})
    with urllib.request.urlopen(req, timeout=20) as r:
        datos = json.loads(r.read().decode())
    return [{'ts': int(k[0]), 'open': float(k[1]), 'high': float(k[2]),
             'low': float(k[3]), 'close': float(k[4]), 'volumen': float(k[5])}
            for k in datos]


def velas(par: str, tf: str, limite: int = 500, forzar: bool = False) -> dict:
    """Velas de un par en una temporalidad. Cachea 5 min.

    Devuelve {'par','tf','fuente','velas'} o {'error': ...}
    """
    if not forzar:
        c = _leer_cache(par, tf)
        if c:
            return {'par': par, 'tf': tf, 'fuente': 'cache', 'velas': c}
    try:
        v = binance_klines(par, tf, limite)
        _escribir_cache(par, tf, v)
        return {'par': par, 'tf': tf, 'fuente': 'binance', 'velas': v}
    except Exception as e:
        # fallback: cache vieja aunque este vencida
        c = _leer_cache(par, tf) or _leer_cache_vieja(par, tf)
        if c:
            return {'par': par, 'tf': tf, 'fuente': 'cache', 'velas': c}
        return {'par': par, 'tf': tf, 'error': f'{type(e).__name__}: {e}'}


def _leer_cache_vieja(par: str, tf: str) -> list[dict] | None:
    p = _cache_path(par, tf)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())['velas']
    except Exception:
        return None


def precio_actual(par: str) -> float | None:
    try:
        with urllib.request.urlopen(
                f'{BINANCE}/api/v3/ticker/price?symbol={par}',
                timeout=15) as r:
            return float(json.loads(r.read().decode())['price'])
    except Exception:
        return None


if __name__ == '__main__':
    r = velas(sys.argv[1] if len(sys.argv) > 1 else 'BTCUSDT',
              sys.argv[2] if len(sys.argv) > 2 else '1d', forzar=True)
    if 'error' in r:
        print('ERROR:', r['error'])
    else:
        print(f"{r['par']} {r['tf']} -> {len(r['velas'])} velas ({r['fuente']})")
        print('ultima:', r['velas'][-1])
