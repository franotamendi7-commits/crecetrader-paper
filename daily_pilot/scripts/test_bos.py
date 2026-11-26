#!/usr/bin/env python3
"""NUEVA IDEA 15: Break of Structure (BOS) 4h + confirmacion 1h.

Regla:
  · 4h: tendencia con maximos crecientes / minimos crecientes (estructura alcista)
  · entrada cuando el precio rompe el ultimo maximo (BOS)
  · confirmacion en 1h: cierre de la vela 1h por encima del maximo roto
  · stop fijo: ultimo minimo swing (debajo de la estructura)
  · target: 1.5R con BE en 1R (salida half)
  · espejo short: minimos decrecientes, rompe ultimo minimo

Mismo estandar estricto: 20 seeds, p<0.05, WF test>0.
"""
from __future__ import annotations
import json, math, random, statistics, sys
from pathlib import Path
B=Path('/Users/franciscootamendi/YouTubeTradingAgent')
sys.path.insert(0,str(B/'daily_pilot'/'scripts'))
import estrategias_validadas as E

OUT=B/'daily_pilot/datos/resultados_bos.jsonl'
SEEDS=20

def cargar(par,tf):
    p=E.VELAS/f'{par}_{tf}.json'
    return json.loads(p.read_text())['velas'] if p.exists() else []

def swings(v,n=5):
    hi,lo=[],[]
    for i in range(n,len(v)-n):
        if all(v[i]['high']>v[j]['high'] for j in range(i-n,i)) and \
           all(v[i]['high']>=v[j]['high'] for j in range(i+1,i+n+1)): hi.append((i,v[i]['high']))
        if all(v[i]['low']<v[j]['low'] for j in range(i-n,i)) and \
           all(v[i]['low']<=v[j]['low'] for j in range(i+1,i+n+1)): lo.append((i,v[i]['low']))
    return hi,lo

def detectar(v4,v1,side='long'):
    """BOS en 4h confirmado por cierre 1h por encima/del maximo/minimo roto."""
    hi,lo=swings(v4,5)
    out=[]
    # indice 4h -> rango de velas 1h correspondiente
    for k in range(len(hi)-1):
        j,piv=hi[k]
        # minimo anterior al pivote (stop)
        prev=[x for (i,x) in lo if i<j]
        if not prev: continue
        stop=prev[-1]
        if stop>=piv: continue
        # Buscar en 4h la primera vela que cierra por encima del pivote
        f=None
        for m in range(j+1,min(j+30,len(v4))):
            if v4[m]['close']>piv*1.001:
                f=m; break
        if f is None: continue
        # confirmacion 1h: cierre sobre el maximo roto en el mismo dia de la vela 4h
        t0,t1=v4[f]['ts'], v4[f]['ts']+4*3600*1000
        conf=[x for x in v1 if t0<=x['ts']<t1 and x['close']>piv*1.001]
        if not conf: continue
        entry=conf[-1]['close']
        if entry<=piv or stop>=entry: continue
        risk=entry-stop
        if risk/entry>0.15: continue
        out.append({'i4':f,'entry':entry,'stop':stop,'target':entry+1.5*risk,
                    'be_at':1.0,'max_bars':96,'dir':'long'})
    if side=='short':
        out=[]
        for k in range(len(lo)-1):
            j,piv=lo[k]
            prev=[x for (i,x) in hi if i<j]
            if not prev: continue
            stop=prev[-1]
            if stop<=piv: continue
            f=None
            for m in range(j+1,min(j+30,len(v4))):
                if v4[m]['close']<piv*0.999: f=m; break
            if f is None: continue
            t0,t1=v4[f]['ts'],v4[f]['ts']+4*3600*1000
            conf=[x for x in v1 if t0<=x['ts']<t1 and x['close']<piv*0.999]
            if not conf: continue
            entry=conf[-1]['close']
            if entry>=piv or entry<=stop: continue
            risk=stop-entry
            if risk/entry>0.15: continue
            out.append({'i4':f,'entry':entry,'stop':stop,'target':entry-1.5*risk,
                        'be_at':None,'max_bars':96,'dir':'short'})
    return out

def simular(v,sen):
    """Simulacion simple: mismo esqueleto que estrategias_validadas.simular."""
    res=[]
    for s in sen:
        # mapear indice 4h a indice de v (4h)
        i=s['i4']; e=s['entry']; st0=s['stop']; tg=s['target']
        if s['dir']=='long':
            risk=e-st0
            if risk<=0: continue
            R=(tg-e)/risk
            be=e+s['be_at']*risk if s.get('be_at') else None
            st=st0; partial=False; realized=0.0; out=0.0
            for j in range(i+1,min(i+s['max_bars'],len(v))):
                hh,ll=v[j]['high'],v[j]['low']
                if be and hh>=be: st=max(st,e)
                if not partial and hh>=e+risk: partial=True; realized+=0.5
                if ll<=st:
                    realized+= 0 if st==e else (-0.5 if partial else -1)
                    out=realized; break
                if hh>=tg:
                    realized+=0.5*R if partial else R
                    out=realized; break
        else:
            risk=st0-e
            if risk<=0: continue
            R=(e-tg)/risk
            st=st0; partial=False; realized=0.0; out=0.0
            for j in range(i+1,min(i+s['max_bars'],len(v))):
                hh,ll=v[j]['high'],v[j]['low']
                if not partial and ll<=e-risk: partial=True; realized+=0.5
                if hh>=st:
                    realized+= -0.5 if partial else -1
                    out=realized; break
                if ll<=tg:
                    realized+=0.5*R if partial else R
                    out=realized; break
        res.append(out)
    return res

def sint(v,seed):
    c=[x['close'] for x in v]
    rets=[math.log(max(c[i],1e-9)/max(c[i-1],1e-9)) for i in range(1,len(c))]
    sg=[1 if r>=0 else -1 for r in rets]; mg=[abs(r) for r in rets]
    rh=[x['high']/max(x['close'],1e-9) for x in v]; rl=[x['low']/max(x['close'],1e-9) for x in v]
    rng=random.Random(seed); s2=sg[:]; rng.shuffle(s2)
    cl=[c[0]]
    for s,m in zip(s2,mg): cl.append(cl[-1]*math.exp(s*m))
    return [{'ts':x['ts'],'open':cl[i],'high':cl[i]*rh[i],'low':cl[i]*rl[i],
             'close':cl[i],'volumen':0} for i,x in enumerate(v)]

def probar(par,side):
    v4,v1=cargar(par,'4h'),cargar(par,'1h')
    if len(v4)<1000 or len(v1)<5000: return None
    sen=detectar(v4,v1,side)
    if len(sen)<8: return None
    out=simular(v4,sen)
    real=sum(out)
    eq=peak=dd=0.0
    for x in out:
        eq+=x; peak=max(peak,eq); dd=min(dd,eq-peak)
    sims=[]
    for sd in range(SEEDS):
        s4,s1=sint(v4,9000+sd),sint(v1,9000+sd)
        ss=detectar(s4,s1,side)
        so=simular(s4,ss) if ss else []
        sims.append(sum(so))
    p=(sum(1 for s in sims if s>=real)+1)/(SEEDS+1)
    k=int(len(out)*0.7)
    tr,te=sum(out[:k]),sum(out[k:])
    win=100*sum(1 for x in out if x>0)/len(out)
    return {'par':par,'estrategia':'BOS_'+side,'n':len(out),'win':round(win,1),
            'real_R':round(real,2),'dd_R':round(dd,2),
            'null_media_R':round(statistics.mean(sims),2),
            'null_max_R':round(max(sims),2),'p':round(p,4),
            'train_R':round(tr,2),'test_R':round(te,2),'seeds':SEEDS,
            'veredicto':'VALIDAR' if (p<0.05 and te>0) else 'DESCARTAR'}

def ya():
    if not OUT.exists(): return set()
    return {(json.loads(l)['par'],json.loads(l)['estrategia'])
            for l in OUT.read_text().splitlines() if l.strip()}

def main():
    pares=sys.argv[1:]
    done=ya()
    for par in pares:
        for side in ('long','short'):
            if (par,'BOS_'+side) in done: continue
            r=probar(par,side)
            if not r: continue
            with OUT.open('a') as f: f.write(json.dumps(r,ensure_ascii=False)+'\n')
            print(f"{par.replace('USDT',''):>6} BOS {side:>5} n={r['n']:>4} win={r['win']:>5}% "
                  f"E={r['real_R']:+.2f}R DD={r['dd_R']:.1f}R p={r['p']:.3f} "
                  f"test={r['test_R']:+.2f}R -> {r['veredicto']}",flush=True)

if __name__=='__main__': main()
