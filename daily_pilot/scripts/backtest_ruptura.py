#!/usr/bin/env python3
"""Backtest de RUPTURA DE TRAMO (C05 + extensiones).

La operativa real de Francisco, mecanica y simple:
  · Se detecta el tramo (maximo mas alto -> piso posterior) en un TF.
  · ENTRADA: el precio CIERRA por encima del maximo del tramo.
  · STOP   : el minimo del tramo (estructural). Si eso queda muy lejos,
             se usa el swing previo como alternativa.
  · TARGET : extension de fibo del tramo (por defecto 1.5).

  Sin look-ahead: la entrada es el cierre de la vela de ruptura.
  PAPER_ONLY: no ejecuta ordenes.

Uso:
  python3 daily_pilot/scripts/backtest_ruptura.py --par BTCUSDT --tf 4h
  python3 daily_pilot/scripts/backtest_ruptura.py --par BTCUSDT --tf 4h --montecarlo 500
  python3 daily_pilot/scripts/backtest_ruptura.py --par BTCUSDT --tf 4h --walkforward
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
PILOT = BASE / 'daily_pilot'
sys.path.insert(0, str(PILOT / 'core'))

PAPER_ONLY = True


# ------------------------------------------------------------------ tramo
def _tramos(velas: list[dict], n: int = 5) -> list[dict]:
    """Todos los tramos terminados de la serie, en orden.

    Un tramo = maximo local (pico) seguido del minimo posterior (base).
    """
    out = []
    k = n + 1
    while k < len(velas) - 1:
        # pico: maximo de una ventana centrada
        vent = velas[max(0, k - n):min(len(velas), k + n + 1)]
        if len(vent) < 3:
            break
        pico = max(range(max(0, k - n), min(len(velas), k + n + 1)), key=lambda j: velas[j]['high'])
        mx = velas[pico]['high']
        if pico != k or pico >= len(velas) - 1:
            k += 1
            continue
        pos = [j for j in range(pico + 1, min(pico + 60, len(velas)))]
        if not pos:
            break
        mn = min(velas[j]['low'] for j in pos)
        base = next(j for j in pos if velas[j]['low'] == mn)
        if mx > mn:
            out.append({'max': mx, 'min': mn, 'pico': pico, 'base': base})
            k = base + 1
        else:
            k += 1
    return out


def ext_fibo(mn: float, mx: float, e: float) -> float:
    """Extension e sobre el rango mn->mx (0=minimo, 1=maximo)."""
    return mn + (mx - mn) * e


def simular(velas: list[dict], ext: float = 1.5, n_swing: int = 5,
            stop_pct_max: float = 8.0) -> list[float]:
    """Corre la estrategia y devuelve la lista de resultados en R."""
    outs = []
    for t in _tramos(velas, n_swing):
        # ENTRADA: primera vela DESPUES del pico que cierra sobre el maximo
        entro = None
        for j in range(t['pico'] + 1, len(velas)):
            if velas[j]['close'] > t['max']:
                entro = j
                break
        if entro is None:
            continue
        entry = velas[entro]['close']
        stop = t['min']
        riesgo_pct = (entry - stop) / entry * 100
        if riesgo_pct <= 0:
            continue
        if riesgo_pct > stop_pct_max:
            stop = min(v['low'] for v in velas[max(0, entro - n_swing * 2):entro])
            riesgo_pct = (entry - stop) / entry * 100
            if riesgo_pct <= 0 or riesgo_pct > stop_pct_max:
                continue
        target = ext_fibo(t['min'], t['max'], ext)
        risk = entry - stop
        R = (target - entry) / risk
        oc, hit = -1.0, 'stop'
        for j in range(entro + 1, len(velas)):
            y = velas[j]
            if y['low'] <= stop:
                oc, hit = -1.0, 'stop'
                break
            if y['high'] >= target:
                oc, hit = R, 'target'
                break
        outs.append(round(oc, 4))
    return outs


# --------------------------------------------------------------- metricas
def metricas(outs: list[float]) -> dict:
    if not outs:
        return {'n': 0}
    pos = [o for o in outs if o > 0]
    neg = [o for o in outs if o < 0]
    pf = (sum(pos) / abs(sum(neg))) if (neg and sum(neg)) else (float('inf') if pos else 0.0)
    cum = peak = dd = 0.0
    for o in outs:
        cum += o
        peak = max(peak, cum)
        dd = min(dd, cum - peak)
    racha = mx = 0
    for o in outs:
        if o < 0:
            racha += 1
            mx = max(mx, racha)
        else:
            racha = 0
    return {
        'n': len(outs),
        'acierto_pct': round(len(pos) / len(outs) * 100, 1),
        'factor_beneficio': round(pf, 3) if pf != float('inf') else None,
        'esperanza_R': round(sum(outs) / len(outs), 4),
        'total_R': round(cum, 2),
        'drawdown_R': round(dd, 2),
        'max_racha_perdidas': mx,
    }


def montecarlo(outs: list[float], n_sim: int = 500, seed: int = 7) -> dict:
    """Remuestreo aleatorio de los resultados para ver dispersion."""
    if not outs:
        return {}
    rnd = random.Random(seed)
    medias, dds = [], []
    for _ in range(n_sim):
        muestra = [rnd.choice(outs) for _ in outs]
        m = metricas(muestra)
        medias.append(m['esperanza_R'])
        dds.append(m['drawdown_R'])
    medias.sort()
    dds.sort()
    def q(a, p):
        return a[min(len(a) - 1, int(p * len(a)))]
    return {
        'sims': n_sim,
        'esp_media': round(statistics.mean(medias), 4),
        'esp_p5': round(q(medias, 0.05), 4),
        'esp_p50': round(q(medias, 0.50), 4),
        'esp_p95': round(q(medias, 0.95), 4),
        'dd_p50': round(q(dds, 0.50), 2),
        'dd_p95': round(q(dds, 0.95), 2),
        'prob_esp_negativa': round(sum(1 for m in medias if m < 0) / len(medias), 3),
    }


def walk_forward(velas: list[dict], ext: float = 1.5, n_swing: int = 5) -> list[dict]:
    """Corta en 3 bloques y reporta IS vs OOS."""
    n = len(velas)
    cortes = [n // 3, 2 * n // 3]
    res = []
    for k in range(3):
        ini = 0 if k == 0 else cortes[k - 1]
        fin = n if k == 2 else cortes[k]
        outs = simular(velas[ini:fin], ext, n_swing)
        res.append({'bloque': k + 1, 'velas': fin - ini, **metricas(outs)})
    return res


# ------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--par', default='BTCUSDT')
    ap.add_argument('--tf', default='4h')
    ap.add_argument('--ext', type=float, default=1.5)
    ap.add_argument('--detalle', type=int, default=500)
    ap.add_argument('--montecarlo', type=int, default=0)
    ap.add_argument('--walkforward', action='store_true')
    args = ap.parse_args()

    from velas import velas as cargar
    r = cargar(args.par, args.tf, limite=args.detalle)
    if 'error' in r or len(r['velas']) < 50:
        print(json.dumps({'error': r.get('error', 'sin datos suficientes')}, ensure_ascii=False))
        return 1
    v = r['velas']

    outs = simular(v, args.ext)
    salida = {
        'par': args.par, 'tf': args.tf, 'ext': args.ext, 'velas': len(v),
        'fuente': r.get('fuente'), 'paper_only': PAPER_ONLY,
        'base': metricas(outs),
    }
    if outs and args.montecarlo:
        salida['montecarlo'] = montecarlo(outs, args.montecarlo)
    if args.walkforward:
        salida['walk_forward'] = walk_forward(v, args.ext)
    print(json.dumps(salida, indent=1, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
