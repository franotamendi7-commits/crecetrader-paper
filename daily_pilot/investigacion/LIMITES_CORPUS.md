# LÍMITES DEL CORPUS — por qué no hay «precios calculados por plazo»

**Fecha**: 2026-11-18 · **Muestra**: 97 videos re-analizados, **1.315 niveles**
**Método**: cada nivel se cruza con la cue donde aparece (±1 cue) y se detecta TF e instrumento por regex.

## El número

| | niveles | % |
|---|---|---|
| **Total de niveles** | **1.315** | 100% |
| Con **timeframe** | 201 | **15,3%** |
| Con **instrumento** | 89 | **6,8%** |

Desglose de TF: `4H` 72 · `Daily` 73 · `Weekly` 45 · `Intradía` 11.
Desglose de instrumento: `BTC` 56 · `NQ` 17 · `XAUUSD` 9 · `ETH` 7.

## Consecuencia

**El canal dice números sin decir el timeframe (85%) ni el instrumento (93%).**

Por tanto:
- ❌ **No** se pueden calcular zonas «de corto / mediano / largo plazo» de forma defendible:
  el 85% de los extremos necesarios no existe en el corpus.
- ❌ **No** se puede dar «precios calculados de Amazon»: **Amazon no está en el corpus**.
- ⚠️ Calcular zonas sobre los niveles **sueltos** mezcla ETH/oro/BTC y da rangos absurdos
  (1.065–165.000). **Eso es exactamente lo que no hay que hacer.**

## Lo que SÍ se puede defender

1. **Lo dicho por el canal, con contexto** (nivel + frase + menciones).
   Ej.: 69.000 x180 «perdido con esa fuerza»; 56.750 x57 «no descartemos los 56.750».
2. **El método (C01–C12)** aplicado por el trader.
3. **Zonas solo si el trader define el rango** (mín/máx por plazo) — no inferidas.

## Qué haría falta para calcular de verdad

- Que el corpus tenga **TF por nivel** (hoy 15%) → habría que re-extraer de otra forma
  (no el cue, sino el **segmento de video** donde el canal habla de ese marco).
- O que **el trader defina los rangos** por activo y plazo.

## Reproducir

```bash
cd /Users/franciscootamendi/YouTubeTradingAgent
python3 daily_pilot/scripts/reanalizar_tf.py            # re-analiza todos
python3 - <<'EOF'
import json, pathlib, collections
tf=collections.Counter(); inst=collections.Counter(); tot=con_tf=con_inst=0
for p in pathlib.Path('daily_pilot/analisis').glob('*_analisis.json'):
    a=json.loads(p.read_text())
    for n in (a.get('niveles_con_tf') or []):
        tot+=1
        if n['tf']: con_tf+=1; tf[n['tf']]+=1
        if n['instrumento']: con_inst+=1; inst[n['instrumento']]+=1
print(tot, con_tf, round(100*con_tf/tot,1), con_inst, round(100*con_inst/tot,1))
print(dict(tf), dict(inst))
EOF
```
