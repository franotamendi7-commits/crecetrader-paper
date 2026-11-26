#!/usr/bin/env python3
"""Semaforo: que tan cerca esta cada par de disparar una senal.

Calcula la distancia entre el precio actual y el nivel de activacion
de cada detector, usando las MISMAS velas que usan los trackers.

verde   → muy cerca (<=0.5% del disparador): falta confirmacion de vela 1h
amarillo→ en rango esperando ruptura (0.5%-3%)
rojo    → sin formacion / lejos (>3% o sin datos)

Es Solo lectura: no ejecuta nada, no cambia journals.
"""
from __future__ import annotations
import json, math, sys
from pathlib import Path

B=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(B/'daily_pilot'/'scripts'))
import scalein_fibo as S
import estrategias_validadas as E
import test_bos as T

V=B/'daily_pilot'/'datos'/'velas'
DIV={'USDBRL','EURUSD','GBPUSD','AUDUSD','NZDUSD','USDCAD','USDCHF',
     'USDCNY','USDHKD','USDJPY','USDMXN','USDNOK'}
ETF={'BOVA11','COPX','DIA','ECH'}


def cargar(par,tf):
    # los pares Yahoo guardan {DIVISAS,ETFS}_{tf}.json; cripto termina USDT
    nombre = par if par in DIV|ETF else par+'USDT'
    p=V/f'{nombre}_{tf}.json'
    return json.loads(p.read_text())['velas'] if p.exists() else []


def distancia(par, estrategia):
    v1,v4=cargar(par,'1h'),cargar(par,'4h')
    if len(v1)<300 or len(v4)<100: return None
    precio=v1[-1]['close']
    c=[x['close'] for x in v4]

    if estrategia=='bos':
        piv=[]
        for i in range(5,len(v4)-5):
            if all(v4[i]['high']>v4[j]['high'] for j in range(i-5,i)) and \
               all(v4[i]['high']>=v4[j]['high'] for j in range(i+1,i+6)):
                piv.append(v4[i]['high'])
        if not piv: return None
        nivel=max(piv[-3:])
    elif estrategia=='pullback':
        ef=E.ema(c,13); et=E.ema(c,200)
        if et[-1] is None or c[-1]<=et[-1]: return None
        nivel=ef[-1]
    elif estrategia=='scalein':
        lows=[x['low'] for x in v4[-24:]]
        nivel=min(lows)
    elif estrategia=='reversion':
        ref=max(c[-8:]); nivel=ref*(1-0.12)
    else: return None
    if not nivel or nivel<=0: return None
    return abs(precio-nivel)/precio*100, precio, nivel


def clasificar(pct):
    if pct is None: return 'rojo','sin formacion'
    if pct<=0.5: return 'verde','falta confirmacion 1h'
    if pct<=3.0: return 'amarillo','esperando ruptura'
    return 'rojo','lejos del nivel'


def calcular(pares):
    out=[]
    for par,est in pares:
        d=distancia(par,est)
        color,txt=clasificar(d[0] if d else None)
        out.append({'par':par,'estrategia':est,'color':color,'estado':txt,
                    'dist':round(d[0],2) if d else None,
                    'precio':round(d[1],5) if d else None,
                    'nivel':round(d[2],5) if d else None})
    orden={'verde':0,'amarillo':1,'rojo':2}
    out.sort(key=lambda x:(orden[x['color']], x['dist'] if x['dist'] is not None else 999))
    return out


if __name__=='__main__':
    carga=json.loads((B/'daily_pilot'/'datos'/'cartera_mixta.json').read_text())
    pares=[]
    for e in carga['estrategias']:
        for p in e['pares']:
            pares.append((p if p in DIV|ETF else p.replace('USDT',''),e['clave']))
    r=calcular(pares)
    print(json.dumps(r,indent=2))
