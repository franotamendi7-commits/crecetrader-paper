#!/usr/bin/env python3
"""MONITOR DE SEÑALES — aplica la estrategia VALIDADA a precios reales.

Estrategia: ruptura de tramo bajista en 4h, long only, stop swing3,
target extension 3.0, gestion full. Validada: n=52, E=+1,237R, p=0,020.

Para cada par:
  · busca la ultima señal con el filtro validado (tramo >=30 velas)
  · calcula entry / stop / target 3.0
  · si la señal sigue ABIERTA: da el ticket (riesgo, posicion, margen 20x)
  · si ya cerro: indica resultado

Uso:
    python3 daily_pilot/scripts/monitor_senales.py

PAPER_ONLY: calcula, no ejecuta. NUNCA manda ordenes.
"""
from __future__ import annotations

import datetime
import json
import os
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
PILOT = BASE / 'daily_pilot'
sys.path.insert(0, str(PILOT / 'core'))
sys.path.insert(0, str(PILOT / 'scripts'))

import busqueda_estrategia as B  # noqa: E402

P = dict(tramo_n=8, ext=3.0, stop_mode='swing3', be=None, gestion='full',
         direction='long', filters={'tramo_min30'})
CAPITAL = 300.0     # USD, capital real del usuario
RIESGO_PCT = 0.01   # 1% por operacion (recomendacion de la verificacion)
APALANCAMIENTO = 20  # Quantfury

PARES = ['BTCUSDT', 'ETHUSDT']


def ts_fecha(ts):
    return datetime.datetime.utcfromtimestamp(ts / 1000).strftime('%Y-%m-%d %H:%M')


def monitor(par: str) -> dict:
    ruta = PILOT / 'datos' / 'velas' / f'{par}_4h.json'
    if not ruta.exists():
        return {'par': par, 'error': 'sin velas 4h'}
    velas = json.loads(ruta.read_text())['velas']
    if not velas:
        return {'par': par, 'error': 'velas vacias'}

    ult_precio = float(velas[-1]['close'])
    sets = []
    for s in B.construir_setups(velas, '4h', 8):
        if s['side'] != 'long' or not B.aplicar_filtros(s, P['filters']):
            continue
        o = B.simular_trade(s, velas, 3.0, 'swing3', None, 'full')
        if o is not None:
            sets.append((s, o))

    base = {'par': par.replace('USDT', ''),
            'precio_actual': ult_precio,
            'actualizado': ts_fecha(velas[-1]['ts']),
            'n_ops_historicas': len(sets)}

    if not sets:
        base.update(senal=False, estado='SIN SEÑAL',
                    nota='No hay ruptura de tramo bajista >=30 velas pendiente.')
        return base

    s, _ = max(sets, key=lambda x: x[0]['entry_idx'])
    ei = s['entry_idx']
    entry = float(s['entry'])
    stop = float(B.stop_price(s, 'swing3'))
    rng = float(s['range'])
    target = float(s['low'] + rng * 3.0)
    risk_u = entry - stop
    if risk_u <= 0:
        base.update(senal=False, estado='SIN SEÑAL', nota='stop invalido')
        return base

    R_target = (target - entry) / risk_u
    riesgo_usd = CAPITAL * RIESGO_PCT
    unidades = riesgo_usd / risk_u
    notional = unidades * entry
    margen = notional / APALANCAMIENTO

    # estado de la señal: se considera ABIERTA si el stop no se toco y el target no se alcanzo
    posteriores = velas[ei + 1:]
    stop_hit = any(v['low'] <= stop for v in posteriores)
    target_hit = any(v['high'] >= target for v in posteriores)
    if stop_hit:
        estado = 'CERRADA · STOP'
    elif target_hit:
        estado = 'CERRADA · TARGET'
    else:
        estado = 'ABIERTA'

    base.update(
        senal=(estado == 'ABIERTA'),
        estado=estado,
        fecha_senal=ts_fecha(velas[ei]['ts']),
        entry=round(entry, 2),
        stop=round(stop, 2),
        target=round(target, 2),
        target_R=round(R_target, 2),
        riesgo_por_unidad=round(risk_u, 2),
        ticket={'capital': CAPITAL, 'riesgo_pct': RIESGO_PCT * 100,
                'riesgo_usd': round(riesgo_usd, 2),
                'unidades': round(unidades, 4),
                'notional': round(notional, 2),
                'margen_20x': round(margen, 2)},
        nota=('Señal abierta: stop bajo el swing de 3 velas, target extension 3.0 del tramo.'
              if estado == 'ABIERTA'
              else 'Ultima señal ya definida. Esperando nueva ruptura.'))
    return base


def main():
    out = {'generado': datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'),
           'estrategia': 'ruptura tramo 4h · long · swing3 · ext3.0 · full',
           'validacion': 'n=52 · E=+1,237R · p=0,020 · DD=-6,35R',
           'pares': [monitor(p) for p in PARES],
           'aviso': 'PAPER ONLY. Costos del backtest: 0.10% comision + 0.05% slippage (conservador; Quantfury no cobra).'}
    dest = PILOT / 'datos' / 'monitor_senales.json'
    dest.write_text(json.dumps(out, indent=2), encoding='utf-8')
    print(f'-> {dest}')
    for p in out['pares']:
        print(json.dumps(p, ensure_ascii=False))


if __name__ == '__main__':
    main()
