#!/usr/bin/env python3
"""PAPER TRADING — registrar operaciones simuladas y ver la curva.

Nunca manda una orden: solo anota. PAPER_ONLY obligatorio.

    python3 daily_pilot/scripts/paper_trading.py --abrir long BTCUSDT 67304 --sl 65000 --tp 80179
    python3 daily_pilot/scripts/paper_trading.py --cerrar 1
    python3 daily_pilot/scripts/paper_trading.py --resumen
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / 'daily_pilot' / 'core'))
ARCHIVO = BASE / 'daily_pilot' / 'datos' / 'paper_trades.json'


def _cargar() -> dict:
    if ARCHIVO.exists():
        return json.loads(ARCHIVO.read_text())
    return {'operaciones': [], 'papel_inicial': 1000.0}


def _guardar(d: dict):
    ARCHIVO.parent.mkdir(parents=True, exist_ok=True)
    ARCHIVO.write_text(json.dumps(d, indent=1, ensure_ascii=False))


def abrir(lado: str, par: str, entrada: float, sl: float, tp: float,
          riesgo_pct: float = 2.0, motivo: str = '', capital=None) -> dict:
    """Abre una operacion simulada. PAPER_ONLY."""
    lado = lado.lower()
    if lado not in ('long', 'short'):
        raise SystemExit('lado debe ser long o short')
    if lado == 'long' and not (sl < entrada < tp):
        raise SystemExit('long requiere sl < entrada < tp')
    if lado == 'short' and not (tp < entrada < sl):
        raise SystemExit('short requiere tp < entrada < sl')
    d = _cargar()
    cap = capital if capital is not None else d.get('papel_inicial', 1000.0)
    n = len(d['operaciones']) + 1
    stop_pct = abs(entrada - sl) / entrada * 100
    notional = cap * (riesgo_pct / 100.0) / (stop_pct / 100.0)
    op = {'id': n, 'lado': lado, 'par': par, 'entrada': entrada, 'sl': sl, 'tp': tp,
          'riesgo_pct': riesgo_pct, 'capital': cap, 'stop_pct': round(stop_pct, 4),
          'notional': round(notional, 2),
          'riesgo_usd': round(cap * riesgo_pct / 100.0, 2),
          'motivo': motivo, 'abierta': True,
          'fecha_apertura': datetime.now(timezone.utc).isoformat(),
          'resultado': None}
    d['operaciones'].append(op)
    _guardar(d)
    print(f"#{n} {lado.upper()} {par} @ {entrada:.4f} | SL {sl:.4f} ({stop_pct:.2f}%) "
          f"| TP {tp:.4f} | notional ${notional:,.2f}")
    return op


def cerrar(id_op: int, precio: float = None, comision_pct: float = 0.1) -> dict:
    """Cierra la operacion. P&L sobre el notional menos comision/slippage."""
    from velas import velas
    d = _cargar()
    ops = [o for o in d['operaciones'] if o['id'] == id_op and o['abierta']]
    if not ops:
        raise SystemExit('operacion no encontrada o ya cerrada')
    op = ops[0]
    if precio is None:
        r = velas(op['par'], '1d', limite=2)
        if 'error' in r:
            raise SystemExit(r['error'])
        precio = float(r['velas'][-1]['close'])
    if op['lado'] == 'long':
        res = (precio - op['entrada']) / op['entrada'] * 100
    else:
        res = (op['entrada'] - precio) / op['entrada'] * 100
    notional = op['notional']
    comision = notional * (comision_pct / 100.0)
    op['abierta'] = False
    op['precio_cierre'] = precio
    op['resultado_pct'] = round(res, 2)
    op['comision_usd'] = round(comision, 2)
    op['resultado_usd'] = round(res / 100 * notional - comision, 2)
    op['fecha_cierre'] = datetime.now(timezone.utc).isoformat()
    _guardar(d)
    print(f"#{op['id']} cerrada @ {precio:.4f} -> {op['resultado_pct']:+.2f}% "
          f"(${op['resultado_usd']:+.2f})")
    return op


def resumen() -> None:
    d = _cargar()
    ops = d['operaciones']
    cerradas = [o for o in ops if not o['abierta']]
    g = [o for o in cerradas if (o.get('resultado_pct') or 0) > 0]
    p = [o for o in cerradas if (o.get('resultado_pct') or 0) <= 0]
    tot = sum(o.get('resultado_usd') or 0 for o in cerradas)
    print(f"PAPER TRADING · {len(ops)} operaciones ({len(cerradas)} cerradas)")
    if cerradas:
        print(f"  ganadoras {len(g)} · perdedoras {len(p)} · "
              f"tasa {len(g)/len(cerradas)*100:.1f}%")
        print(f"  resultado acumulado ${tot:+.2f} sobre papel de $1.000")
    abiertas = [o for o in ops if o['abierta']]
    for o in abiertas:
        print(f"  ABIERTA #{o['id']} {o['lado']} {o['par']} @ {o['entrada']}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--abrir', nargs=3, metavar=('LADO', 'PAR', 'ENTRADA'))
    ap.add_argument('--sl', type=float, default=None)
    ap.add_argument('--tp', type=float, default=None)
    ap.add_argument('--riesgo', type=float, default=2.0)
    ap.add_argument('--cerrar', type=int, default=None)
    ap.add_argument('--precio', type=float, default=None)
    ap.add_argument('--capital', type=float, default=None)
    ap.add_argument('--comision', type=float, default=0.1)
    ap.add_argument('--resumen', action='store_true')
    a = ap.parse_args()

    if a.resumen:
        resumen()
        return 0
    if a.abrir:
        if a.sl is None or a.tp is None:
            raise SystemExit('falta --sl o --tp')
        abrir(a.abrir[0].lower(), a.abrir[1].upper(),
               float(a.abrir[2]), a.sl, a.tp, a.riesgo, capital=a.capital)
        return 0
    if a.cerrar:
        cerrar(a.cerrar, a.precio, a.comision)
        return 0
    resumen()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
