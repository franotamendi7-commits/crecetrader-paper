#!/usr/bin/env python3
"""Pullback y reversion para los 22 pares sin scale-in — test robusto 20 seeds."""
from __future__ import annotations
import json, math, random, statistics, sys
from pathlib import Path
B=Path('/Users/franciscootamendi/YouTubeTradingAgent')
sys.path.insert(0,str(B/'daily_pilot'/'scripts'))
import estrategias_validadas as E

OUT=B/'daily_pilot/datos/resultados_pullback_reversion.jsonl'
SEEDS=20
CFG_P=dict(ema_fast=13,ema_trend=200,swing_n=5,regimen='ret_pos',fibo_ext=1.5,be_at=1.0)
CFG_R=dict(caida=0.12,rebote=0.30)

def sint(v,seed):
    c=[x['close'] for x in v]
    rets=[math.log(c[i]/c[i-1]) for i in range(1,len(c))]
    sg=[1 if r>=0 else -1 for r in rets]; mg=[abs(r) for r in rets]
    rh=[x['high']/x['close'] for x in v]; rl=[x['low']/x['close'] for x in v]
    rng=random.Random(seed); s2=sg[:]; rng.shuffle(s2)
    cl=[c[0]]
    for s,m in zip(s2,mg): cl.append(cl[-1]*math.exp(s*m))
    return [{'ts':x['ts'],'open':cl[i],'high':cl[i]*rh[i],'low':cl[i]*rl[i],
             'close':cl[i],'volumen':0} for i,x in enumerate(v)]

def probar(par,tipo,cfg,det):
    v=E.cargar(par,'4h')
    if len(v)<500: return None
    sen=det(v,cfg)
    if not sen: return None
    out=E.simular(v,sen,'half')
    real=sum(out)
    if not out: return None
    eq=peak=dd=0.0
    for x in out:
        eq+=x; peak=max(peak,eq); dd=min(dd,eq-peak)
    sims=[]
    for sd in range(SEEDS):
        sv=sint(v,5000+sd)
        so=det(sv,cfg); soo=E.simular(sv,so,'half') if so else []
        sims.append(sum(soo))
    p=(sum(1 for s in sims if s>=real)+1)/(SEEDS+1)
    k=int(len(out)*0.7)
    tr=sum(out[:k]); te=sum(out[k:])
    win=100*sum(1 for x in out if x>0)/len(out)
    ok=p<0.05 and te>0
    return {'par':par,'estrategia':tipo,'n':len(out),'win':round(win,1),
            'real_R':round(real,3),'dd_R':round(dd,2),
            'null_media_R':round(statistics.mean(sims),3),
            'null_max_R':round(max(sims),3),'p':round(p,4),
            'train_R':round(tr,3),'test_R':round(te,3),'seeds':SEEDS,
            'veredicto':'VALIDAR' if ok else 'DESCARTAR'}

def ya():
    if not OUT.exists(): return set()
    return {(json.loads(l)['par'],json.loads(l)['estrategia'])
            for l in OUT.read_text().splitlines() if l.strip() and json.loads(l).get('seeds')==SEEDS}

def main():
    pares=sys.argv[1:]
    done=ya()
    for par in pares:
        for tipo,cfg,det in (('pullback',CFG_P,E.senales_pullback),
                             ('reversion',CFG_R,E.senales_reversion)):
            if (par,tipo) in done: continue
            r=probar(par,tipo,cfg,det)
            if not r: continue
            with OUT.open('a') as f: f.write(json.dumps(r,ensure_ascii=False)+'\n')
            print(f"{par.replace('USDT',''):>6} {tipo:>9} n={r['n']:>4} "
                  f"win={r['win']:>5}% E={r['real_R']:+.3f}R DD={r['dd_R']:.1f}R "
                  f"p={r['p']:.3f} test={r['test_R']:+.3f} -> {r['veredicto']}",flush=True)

if __name__=='__main__': main()
