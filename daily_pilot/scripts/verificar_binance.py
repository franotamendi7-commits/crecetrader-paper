#!/usr/bin/env python3
"""Verifica la clave de Binance SIN mostrarla.

    python3 daily_pilot/scripts/verificar_binance.py

Dice:
  · si la key esta cargada (si/no)
  · cuantos activos con saldo
  · si la cuenta PUEDE operar o retirar (alerta de seguridad)
  · el total aproximado en USD (con precios de mercado)

Nunca imprime la key ni el secret.
"""
from __future__ import annotations

import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / 'daily_pilot' / 'core'))


def main() -> int:
    try:
        import binance_readonly as B
    except Exception as e:
        print('IMPORT ERROR:', type(e).__name__, e)
        return 2

    # 1. ¿esta cargada?
    try:
        ak, sk = B._credenciales()
        print(f'key cargada: SI (api_key {ak[:4]}…{ak[-4:]}, secret {len(sk)} chars)')
    except Exception as e:
        print('key cargada: NO ->', e)
        print('\nPegala en ~/.hermes/.env como:')
        print('  BINANCE_API_KEY=tu_key')
        print('  BINANCE_SECRET_KEY=tu_secret')
        return 1

    # 2. balance
    try:
        b = B.balance()
        print(f"activos con saldo: {b['n_activos']}")
        print(f"canTrade (puede operar): {b['canTrade']}  |  canWithdraw: {b['puede_retirar']}")
        if b['canTrade']:
            print('⚠️  ALERTA: la cuenta PUEDE OPERAR. La clave deberia ser SOLO LECTURA.')
            print('   Revisa Binance -> API Management y desactiva "Spot & Margin Trading".')
        else:
            print('✅ la cuenta NO puede operar (solo lectura efectiva).')
        px = B.precios([f"{a['activo']}USDT" for a in b['activos']] or None)
        v = B.valor_usd(b, px)
        print(f"total aproximado: ${v['total_usdt']:,.2f} USD")
        for f in v['filas'][:8]:
            val = f"${f['valor_usdt']:,.2f}" if f['valor_usdt'] is not None else 'sin precio'
            print(f"   {f['activo']:<8} {f['total']:>14,.6f}  ≈ {val}")
        return 0
    except Exception as e:
        print('ERROR al leer la cuenta:', type(e).__name__, str(e)[:150])
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
