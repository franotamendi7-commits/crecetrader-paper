#!/usr/bin/env python3
"""ESTRATEGIAS VALIDADAS — modulo unico de produccion (PAPER_ONLY).

Dos estrategias, ambas validadas con null sintetico multi-seed y
walk-forward 70/30:

  1 · PULLBACK BULL-RUN (4 pares): BTC, THETA, HBAR, ETC
      ema13/200 · swing5 · ret_pos · target Fib 1.5 · 50% en 1R + BE

  2 · REVERSION POR CAIDA (2 pares): ARB, XRP
      caida 12% en 8 velas · stop en minimo · target 30% del retroceso

Cartera: 63,9 señales/mes · E=+0,142R · DD=-98,1R · PF=1,39
Riesgo: 0,35% del capital por operación.

NO ejecuta ordenes. Lee velas del archivo DIRECTO (nunca via velas()).
"""
from __future__ import annotations

import math
import random
import statistics
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
VELAS = BASE / 'daily_pilot' / 'datos' / 'velas'

PULLBACK = {
    'BTCUSDT': dict(ema_fast=13, ema_trend=200, swing_n=5, regimen='ret_pos', fibo_ext=1.5, be_at=1.0),
    'THETAUSDT': dict(ema_fast=13, ema_trend=200, swing_n=5, regimen='ret_pos', fibo_ext=1.5, be_at=1.0),
    'HBARUSDT': dict(ema_fast=13, ema_trend=200, swing_n=5, regimen='ret_pos', fibo_ext=1.5, be_at=1.0),
    'ETCUSDT': dict(ema_fast=13, ema_trend=200, swing_n=5, regimen='ret_pos', fibo_ext=1.5, be_at=1.0),
}
REVERSION = {
    'ARBUSDT': dict(caida=0.12, rebote=0.30),
    'XRPUSDT': dict(caida=0.12, rebote=0.30),
}
RIESGO_PCT = 0.0035
CAPITAL = 300.0


def cargar(par: str, tf: str = '4h') -> list[dict]:
    """Lee velas DIRECTO del archivo. Nunca usa velas() para no pisar la cache."""
    p = VELAS / f'{par}_{tf}.json'
    if not p.exists():
        return []
    import json
    return json.loads(p.read_text())['velas']


def ema(vals, n):
    k = 2/(n+1); out=[None]*len(vals); e=None
    for i,x in enumerate(vals):
        e = x if e is None else x*k + e*(1-k)
        out[i]=e
    return out


def swing_points(v, n=5):
    altos, bajos = [], []
    for i in range(len(v)):
        izq=v[max(0,i-n):i]; der=v[i+1:i+1+n]
        if len(der)<n: continue
        if all(v[i]['high']>=x['high'] for x in izq+der): altos.append((i,v[i]['high']))
        if all(v[i]['low']<=x['low'] for x in izq+der): bajos.append((i,v[i]['low']))
    return altos, bajos


# ------------------------------------------------------------------ pullback
def senales_pullback(v, cfg):
    c=[x['close'] for x in v]; h=[x['high'] for x in v]; l=[x['low'] for x in v]
    ef=ema(c,cfg['ema_fast']); et=ema(c,cfg['ema_trend'])
    _, bajos = swing_points(v, cfg['swing_n'])
    altos,_ = swing_points(v, cfg['swing_n'])
    out=[]
    start=cfg['ema_trend']+cfg['swing_n']+30
    for i in range(start,len(v)-1):
        if et[i] is None or ef[i] is None: continue
        if c[i]<=et[i] or ef[i]<=et[i]: continue
        if c[i]/c[i-30]-1 < 0: continue                  # regimen ret_pos
        if l[i]>ef[i]*1.003 or c[i]<=ef[i]: continue
        cand=[p for (j,p) in bajos if j<i]
        if not cand: continue
        stop=cand[-1]; entry=c[i]
        if stop>=entry: continue
        ch=[p for (j,p) in altos if j<i]
        rng=(ch[-1]-stop) if ch else (entry-stop)
        if rng<=0: continue
        target=stop+rng*cfg['fibo_ext']
        if target<=entry: continue
        out.append({'i':i,'entry':entry,'stop':stop,'target':target,'be_at':cfg['be_at'],'max_bars':120})
    return out


# ------------------------------------------------------------------ reversion
def senales_reversion(v, cfg):
    c=[x['close'] for x in v]; l=[x['low'] for x in v]
    out=[]
    for i in range(13, len(v)-1):
        ref=max(c[i-8:i])
        if c[i] >= ref*(1-cfg['caida']): continue
        if c[i] <= l[i]*1.002: continue
        entry=c[i]; stop=l[i]
        if stop>=entry: continue
        target=entry+(ref-entry)*cfg['rebote']
        if target<=entry: continue
        out.append({'i':i,'entry':entry,'stop':stop,'target':target,'be_at':None,'max_bars':60})
    return out


# ------------------------------------------------------------------ simulacion
def simular(v, senales, salida='half'):
    res=[]
    for s in senales:
        i,e,st0,tg = s['i'],s['entry'],s['stop'],s['target']
        risk=e-st0
        if risk<=0: continue
        R=(tg-e)/risk
        be_trigger = e+s['be_at']*risk if s.get('be_at') else None
        st=st0; be=False; partial=False; realized=0.0; out=0.0
        for j in range(i+1,min(i+s.get('max_bars',120),len(v))):
            hi,lo=v[j]['high'],v[j]['low']
            if be_trigger and not be and hi>=be_trigger:
                be=True; st=e
            if salida=='half' and not partial and hi>=e+risk:
                partial=True; realized+=0.5
            if lo<=st:
                realized += 0.5*(0 if st==e else -1) if partial else (0 if st==e else -1)
                out=realized; break
            if hi>=tg:
                realized += 0.5*R if partial else R
                out=realized; break
        res.append(out)
    return res


def size_position(entry, stop, capital=CAPITAL, pct=RIESGO_PCT):
    dist=entry-stop
    if dist<=0: return None
    und=capital*pct/dist
    return {'unidades':round(und,6), 'riesgo_usd':round(capital*pct,2),
            'notional':round(und*entry,2), 'margen_20x':round(und*entry/20,2)}


def senales_par(par):
    """Devuelve (senales, resultados, tipo) para un par de la cartera."""
    v=cargar(par)
    if not v: return [], [], None
    if par in PULLBACK:
        s=senales_pullback(v, PULLBACK[par]); tipo='pullback'
    elif par in REVERSION:
        s=senales_reversion(v, REVERSION[par]); tipo='reversion'
    else:
        return [], [], None
    return s, simular(v,s), tipo


# ------------------------------------------------------------------ null corregido
def null_corregido(v, detector, n_sim=80, seed=7):
    """Permuta SIGNOS de los retornos, conserva magnitudes."""
    c=[x['close'] for x in v]
    rets=[math.log(c[i]/c[i-1]) for i in range(1,len(c))]
    signs=[1 if r>=0 else -1 for r in rets]; mags=[abs(r) for r in rets]
    rh=[x['high']/x['close'] for x in v]; rl=[x['low']/x['close'] for x in v]
    rng=random.Random(seed)
    real=detector(v); out=simular(v,real)
    real_E=statistics.mean(out) if out else 0.0
    sims=[]
    for _ in range(n_sim):
        s2=signs[:]; rng.shuffle(s2)
        cl=[c[0]]
        for s,m in zip(s2,mags): cl.append(cl[-1]*math.exp(s*m))
        vv=[{'ts':x['ts'],'open':cl[i],'high':cl[i]*rh[i],'low':cl[i]*rl[i],
             'close':cl[i],'volumen':x.get('volumen',0)} for i,x in enumerate(v)]
        so=simular(vv,detector(vv))
        sims.append(statistics.mean(so) if so else 0.0)
    sims.sort()
    p=sum(1 for s in sims if s>=real_E)/len(sims)
    return {'real':round(real_E,3),'p':round(p,3),
            'p50':round(sims[len(sims)//2],3),'p95':round(sims[int(.95*len(sims))],3),
            'veredicto':'PASA' if p<=0.05 else 'RUIDO'}


if __name__ == '__main__':
    for par in list(PULLBACK)+list(REVERSION):
        s,o,t=senales_par(par)
        m=statistics.mean(o) if o else 0
        print(f"{par:>10} {t:>9} n={len(s):>5} E={m:+.3f}")
