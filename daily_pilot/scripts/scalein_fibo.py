#!/usr/bin/env python3
#!/usr/bin/env python3
"""SCALE-IN FIBONACCI — la idea de Francisco, medida.

Concepto (de sus capturas 25/11):
  · Cambio de ESTRUCTURA confirmado en 1h + validación en 4h.
  · Entrada inicial en la zona del mínimo de rango / Fibo 0.382-0.5.
  · Si el precio retrocede a 0.5 y 0.61, AGREGAR capital (promediar).
  · Stop fijo estructural (bajo el mínimo del tramo).
  · Riesgo TOTAL máximo 5% del capital (no 5% por tramo).
  · Target extensión Fibo 1.25 / 1.5.

Se mide con velas 1h reales de BTC. PAPER_ONLY.
"""
import sys, json, math, statistics, datetime
from pathlib import Path
sys.path.insert(0, '/Users/franciscootamendi/YouTubeTradingAgent/daily_pilot/scripts')

V = Path('/Users/franciscootamendi/YouTubeTradingAgent/daily_pilot/datos/velas')
CAPITAL = 5680.38          # capital real de la captura de Quantfury
RIESGO_TOTAL = 0.01        # 1% del capital por operación
MIN_R = 0.04               # filtro: target al menos 4% sobre el stop


def ema(vals, n):
    k=2/(n+1); e=None; out=[None]*len(vals)
    for i,x in enumerate(vals):
        e=x if e is None else x*k+e*(1-k); out[i]=e
    return out


def swing_highs(v, n=5):
    out=[]
    for i in range(n,len(v)-n):
        if all(v[i]['high']>=x['high'] for x in v[i-n:i]+v[i+1:i+1+n]):
            out.append((i,v[i]['high']))
    return out


def detectar(v1, v4, cfg):
    """Genera operaciones con scale-in. v4 se alinea por timestamp a v1."""
    c=[x['close'] for x in v1]; l=[x['low'] for x in v1]; h=[x['high'] for x in v1]
    e20=ema(c,20); e50=ema(c,50)
    sh=swing_highs(v1, cfg['swing_n'])
    # mapa 4h: tendencia alcista si close > ema50 4h
    c4=[x['close'] for x in v4]; e4=ema(c4,50)
    t4={x['ts']: (c4[i] > e4[i] if e4[i] else False) for i,x in enumerate(v4)}
    ops=[]
    i=cfg['look']+200
    while i < len(v1)-1:
        # rango: minimo y maximo de las ultimas 'look' velas 1h
        lo=min(l[i-cfg['look']:i]); hi=max(h[i-cfg['look']:i])
        rng=hi-lo
        if rng<=0 or rng/lo > cfg['max_rango']:
            i+=1; continue
        fib382=lo+rng*0.382; fib5=lo+rng*0.5; fib61=lo+rng*0.618
        # entrada: precio en zona 0.382-0.5 (minimos de rango)
        if not (fib382*0.995 <= c[i] <= fib5*1.005):
            i+=1; continue
        # cambio de estructura en 1h: cerro por encima del ultimo swing high
        prev=[p for (j,p) in sh if j<i]
        if not prev:
            i+=1; continue
        if c[i] <= prev[-1]:
            i+=1; continue
        # validacion 4h: tendencia alcista
        ts4 = v1[i]['ts'] - (v1[i]['ts'] % (4*3600*1000))
        if not t4.get(ts4, False):
            i+=1; continue
        if e20[i] and e50[i] and e20[i] < e50[i]:
            i+=1; continue

        stop = lo * (1 - cfg['stop_pct'])       # stop fijo bajo el minimo
        # targets extension
        t125 = lo + rng*1.25; t15 = lo + rng*1.5
        # legs: entrada inicial + recompras en 0.5 y 0.61
        legs=[(i, c[i], 0.4)]                   # 40% del riesgo
        j=i+1; added5=added61=False
        while j < len(v1) and j <= i+cfg['max_bars']:
            # recompra en 0.5
            if not added5 and l[j] <= fib5*1.002 and c[j] >= fib5*0.995:
                legs.append((j, c[j], 0.3)); added5=True
            # recompra en 0.61
            if not added61 and l[j] <= fib61*1.002 and c[j] >= fib61*0.995:
                legs.append((j, c[j], 0.3)); added61=True
            if l[j] <= stop: break
            if h[j] >= (t125 if cfg['target']==1.25 else t15): break
            j+=1
        exit_i=min(j,len(v1)-1)
        exit_price = (t125 if cfg['target']==1.25 else t15) if h[exit_i] >= (t125 if cfg['target']==1.25 else t15) else v1[exit_i]['close']
        if l[exit_i] <= stop: exit_price=stop
        # P&L en dolares: cada leg con su peso del riesgo total
        pnl=0.0
        for (ei,entry,peso) in legs:
            riesgo_usd=CAPITAL*RIESGO_TOTAL*peso
            dist=entry-stop
            if dist<=0: continue
            und=riesgo_usd/dist
            pnl += und*(exit_price-entry)
        ops.append({'i':i,'ts':v1[i]['ts'],'legs':len(legs),
                    'stop':stop,'target':exit_price,'pnl':pnl,
                    'ret_pct':100*pnl/CAPITAL,
                    'R':(exit_price-stop)/stop})
        # salto para no solapar
        i = exit_i+1
    return ops


PARES_VALIDADOS = ['BTCUSDT','ETHUSDT','SOLUSDT','XRPUSDT','ADAUSDT']


def detectar_validados(v1, v4):
    """Scale-in con el filtro R>=4% ya aplicado (5 pares validados)."""
    ops = detectar(v1, v4, dict(look=24, max_rango=0.12, stop_pct=0.03,
                                target=1.25, swing_n=5, max_bars=72))
    return [o for o in ops if o.get('R', 0) >= MIN_R]


def metricas(ops):
    if not ops: return None
    p=[o['pnl'] for o in ops]
    eq=peak=dd=0.0
    for x in p:
        eq+=x; peak=max(peak,eq); dd=min(dd,eq-peak)
    w=[x for x in p if x>0]; l=[x for x in p if x<=0]
    return {'n':len(ops),'retorno':round(eq,2),'pct':round(100*eq/CAPITAL,1),
            'win':round(100*len(w)/len(p),1),'dd':round(dd,2),
            'E':round(statistics.mean(p),2),
            'legs':round(statistics.mean(o['legs'] for o in ops),2)}


if __name__=='__main__':
    v1=json.loads((V/'BTCUSDT_1h.json').read_text())['velas']
    v4=json.loads((V/'BTCUSDT_4h.json').read_text())['velas']
    print(f"velas 1h: {len(v1)} | 4h: {len(v4)}")
    print(f"{'look':>5} {'maxr':>6} {'stop%':>6} {'tgt':>5} | {'n':>4} {'ret$':>8} {'%':>7} {'win':>6} {'dd$':>8} {'legs':>5}")
    res=[]
    for look,rango,stop,tgt in [(24,0.12,0.03,1.25),(24,0.12,0.03,1.5),
                                (48,0.15,0.03,1.25),(48,0.15,0.04,1.25),
                                (12,0.08,0.02,1.25),(48,0.15,0.03,1.5)]:
        cfg=dict(look=look,max_rango=rango,stop_pct=stop,target=tgt,
                 swing_n=5,max_bars=72)
        ops=detectar(v1,v4,cfg); m=metricas(ops)
        if not m: continue
        print(f"{look:>5} {rango:>6.2f} {stop:>6.2f} {tgt:>5.2f} | {m['n']:>4} {m['retorno']:>8.2f} {m['pct']:>6.1f}% "
              f"{m['win']:>5.1f}% {m['dd']:>8.2f} {m['legs']:>5.2f}")
        res.append((m['pct'],look,rango,stop,tgt,m))
    res.sort(reverse=True)
    print("\nmejor:",res[0][1:5] if res else None)
