#!/usr/bin/env python3
"""Binance SOLO LECTURA — balance y precios de la cuenta de Francisco.

La clave vive en `~/.hermes/.env` (FUERA del repo, nunca se escribe aqui):
    BINANCE_API_KEY=...
    BINANCE_SECRET_KEY=...

Regla de oro (Francisco): **es solo lectura**. Esta clave debe tener
*Enable Reading* SI y *Spot & Margin Trading* NO y *Withdrawals* NO.
Este modulo NO tiene ninguna funcion para crear/enviar ordenes.

PAPER_ONLY: lee, no ejecuta.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

PAPER_ONLY = True
BASE_URL = 'https://api.binance.com'
ENV_PATH = Path.home() / '.hermes' / '.env'


class SoloLecturaError(RuntimeError):
    """Se intento algo que no es leer."""


def cargar_env(ruta: Path = ENV_PATH) -> dict:
    """Levanta las variables de ~/.hermes/.env sin mostrarlas."""
    if not ruta.exists():
        raise FileNotFoundError(f'no existe {ruta}')
    out = {}
    for linea in ruta.read_text().splitlines():
        linea = linea.strip()
        if not linea or linea.startswith('#') or '=' not in linea:
            continue
        k, v = linea.split('=', 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def _credenciales() -> tuple[str, str]:
    env = cargar_env()
    ak = env.get('BINANCE_API_KEY')
    sk = env.get('BINANCE_SECRET_KEY')
    if not ak or not sk:
        raise SoloLecturaError(
            'faltan BINANCE_API_KEY o BINANCE_SECRET_KEY en ~/.hermes/.env')
    return ak, sk


def _firma(query: str, secret: str) -> str:
    return hmac.new(secret.encode(), query.encode(), hashlib.sha256).hexdigest()


def _get(path: str, params: dict | None = None, firmar_req: bool = False) -> dict:
    """GET a Binance. Si firmar_req, agrega la firma (solo lectura)."""
    p = dict(params or {})
    ak, sk = _credenciales()
    headers = {'X-MBX-APIKEY': ak}
    if firmar_req:
        p['timestamp'] = int(time.time() * 1000)
        q = urllib.parse.urlencode(p)
        p['signature'] = _firma(q, sk)
    url = BASE_URL + path
    if p:
        url += '?' + urllib.parse.urlencode(p)
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())


# ------------------------------------------------------------------ lectura
def precios(pares: list[str] | None = None) -> dict:
    """Precio de mercado (publico, no usa la key)."""
    d = _get('/api/v3/ticker/price')
    por = {x['symbol']: float(x['price']) for x in d}
    if pares:
        return {k: v for k, v in por.items() if k in pares}
    return por


def balance() -> dict:
    """Balances de la cuenta (requiere la key, SOLO lectura).

    Devuelve los activos con saldo > 0 y el total estimado en USDT.
    """
    cuenta = _get('/api/v3/account', firmar_req=True)
    activos = []
    for b in cuenta.get('balances', []):
        libre = float(b.get('free', 0))
        bloq = float(b.get('locked', 0))
        total = libre + bloq
        if total <= 0:
            continue
        activos.append({'activo': b['asset'], 'libre': libre,
                        'bloqueado': bloq, 'total': total})
    # poder operar? la key solo-lectura NO lo reporta; lo avisamos igual
    puede_operar = cuenta.get('canTrade', None)
    return {
        'activos': sorted(activos, key=lambda x: -x['total']),
        'n_activos': len(activos),
        'canTrade': puede_operar,
        'puede_retirar': cuenta.get('canWithdraw', None),
        'aviso_solo_lectura': (
            'SI puede operar/retirar con esta cuenta. La KEY deberia ser '
            'solo-lectura: revisa Binance -> API Keys.'
            if puede_operar else 'la cuenta no puede operar'),
        'paper_only': PAPER_ONLY,
    }


def valor_usd(ball: dict, precios_usdt: dict | None = None) -> dict:
    """Valor aproximado en USDT de cada activo (para el total del dash)."""
    px = dict(precios_usdt or {})
    filas = []
    for a in ball['activos']:
        act = a['activo']
        if act == 'USDT':
            val = a['total']
        elif f'{act}USDT' in px:
            val = a['total'] * px[f'{act}USDT']
        else:
            val = None
        filas.append({**a, 'valor_usdt': round(val, 2) if val is not None else None})
    total = sum(f['valor_usdt'] for f in filas if f['valor_usdt'])
    return {'filas': filas, 'total_usdt': round(total, 2), 'paper_only': PAPER_ONLY}


if __name__ == '__main__':
    try:
        b = balance()
        print('activos:', b['n_activos'], '| canTrade:', b['canTrade'], '|', b['aviso_solo_lectura'])
        px = precios([f"{a['activo']}USDT" for a in b['activos']] or None)
        v = valor_usd(b, px)
        print('total aproximado USD:', v['total_usdt'])
    except Exception as e:
        print('ERROR:', type(e).__name__, str(e)[:120])
