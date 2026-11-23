#!/usr/bin/env python3
"""Agente de estrategia — CreceTrader.

Pipeline: transcripcion -> niveles dichos (con cita) -> clasificacion por el metodo (C05)
          -> niveles calculados -> informe estructurado.

Read-only sobre las fuentes; escribe en daily_pilot/investigacion/.
PAPER_ONLY: describe y calcula, no ejecuta.

Uso:
  python3 -B agente_estrategia.py --video <vid>
  python3 -B agente_estrategia.py --todos          # el ultimo video de cada mes
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import sqlite3
import sys

BASE = pathlib.Path(__file__).resolve().parents[2]
PILOT = BASE / 'daily_pilot'
sys.path.insert(0, str(PILOT / 'core'))
sys.path.insert(0, str(PILOT / 'knowledge'))
from precios import precios_de_texto                      # noqa: E402
from zonas import zonas, RETROCESOS, EXTENSIONES          # noqa: E402
from intradia import abanico, HORA_ANCLA
from zonas import tf_para                 # noqa: E402

# vocabulario que marca el tipo de nivel (del corpus + del experto)
Pistas = {
    'retroceso': re.compile(r'pullback|retroceso|correcci[oó]n|vuelta|reversi[oó]n', re.I),
    'extension': re.compile(r'extensi[oó]n|proyecci[oó]n|objetivo|aim| metas?', re.I),
    'abanico': re.compile(r'intrad[ií]a|intradia|abanico|scalping|21:00|nueve de la noche', re.I),
    'anclaje': re.compile(r'calculado|1 de enero|anual|anclaje|punto de partida', re.I),
    'oferta': re.compile(r'oferta|comprar|compra en|entrada', re.I),
}


def catalogar(texto: str) -> list[str]:
    return [k for k, rx in Pistas.items() if rx.search(texto or '')]


def niveles_dichos(vid: str) -> list[dict]:
    """Niveles que el canal DICE, con cita y timestamp."""
    tp = BASE / 'data_hist' / vid / f'{vid}_transcript.json'
    if not tp.exists():
        return []
    d = json.loads(tp.read_text())
    out = []
    for s in d.get('segments', []):
        t = s.get('text', '')
        ps = precios_de_texto(t)
        if not ps:
            continue
        out.append({
            'start': s.get('start'),
            'precios': ps,
            'pistas': catalogar(t),
            'cita': t.strip()[:200],
        })
    return out


def consolidar(dichos: list[dict], umbral: int = 1) -> dict:
    """Frecuencia de cada precio y las pistas acumuladas."""
    cnt = collections.Counter()
    pistas = collections.defaultdict(set)
    citas = {}
    for x in dichos:
        for p in x['precios']:
            cnt[p] += 1
            citas.setdefault(p, x['cita'])
            pistas[p] |= set(x['pistas'])
    return {p: {'precio': p, 'menciones': n, 'pistas': sorted(pistas[p]), 'cita': citas[p]}
            for p, n in cnt.items() if n >= umbral and p > 1000}


def calcular(precio: float, tramo=None) -> dict:
    """Niveles que el metodo manda aunque el canal no los diga (C05).

    SIN TRAMO NO SE CALCULA: el fibo necesita un minimo y un maximo reales.
    Inventarlo con el rango de todos los numeros dichos da niveles absurdos.
    """
    ab = abanico(precio)
    out = {'abanico_intradia': {'punto_cero': ab['punto_cero'], 'niveles': ab['niveles'],
                                'unidad': ab['unidad']},
           'fibo_por_plazo': None,
           'fuente': 'calculado (C05), no dicho por el canal'}
    # tramo puede venir como dict (tramo_real) o como secuencia
    if isinstance(tramo, dict):
        if 'error' in tramo:
            out['aviso'] = f'SIN TRAMO REAL: {tramo["error"]}. No se calcula fibo (no se inventa).'
            return out
        tramo = (tramo['minimo'], tramo['maximo'])
    if not tramo:
        out['aviso'] = 'SIN TRAMO: el canal no dio minimo/maximo. No se calcula fibo (no se inventa).'
        return out
    bajo, alto = float(min(tramo)), float(max(tramo))
    z = {}
    for plazo in ('largo', 'media', 'corto'):
        try:
            z[plazo] = {'tf': tf_para(plazo), **zonas(bajo, alto, plazo=plazo)}
        except ValueError as e:
            z[plazo] = {'error': str(e)}
    out['fibo_por_plazo'] = z
    out['tramo'] = {'minimo': bajo, 'maximo': alto}
    return out


def tramo_real(par: str = 'BTCUSDT', tf: str = '1d', n: int = 3, ventana: int = 60) -> dict:
    """El tramo del ciclo (C05-B) con velas reales de Binance.

    Cada TF tiene su swing; el agente usa el tramo del diario como referencia
    (el fibo por plazo se calcula sobre ese tramo).
    """
    try:
        from velas import velas
        from tramos import tramo_ciclo
        r = velas(par, tf, limite=500)
        if 'error' in r:
            return {'error': r['error']}
        t = tramo_ciclo(r['velas'], n=n, ventana=ventana)
        if 'error' in t:
            return {'error': t['error']}
        return {'minimo': t['minimo'], 'maximo': t['maximo'],
                'par': par, 'tf': tf, 'fuente': r['fuente']}
    except Exception as e:
        return {'error': f'{type(e).__name__}: {e}'}


def informe(vid: str) -> dict:
    dichos = niveles_dichos(vid)
    cons = consolidar(dichos)
    top = sorted(cons.values(), key=lambda x: -x['menciones'])
    base = top[0]['precio'] if top else 0.0
    return {
        'video_id': vid,
        'precio_referencia': base,
        'precio_referencia_menciones': top[0]['menciones'] if top else 0,
        'n_cues_con_precio': len(dichos),
        'niveles_dichos': top,
        'tramo_real': tramo_real(),
        'calculados': calcular(base, tramo_real()) if base else None,
        'paper_only': True,
        'nota': 'Los niveles_dichos salen del audio (fuentes). Los calculados salen de C05 (no los dice el canal).',
    }


def fmt(inf: dict) -> str:
    L = [f"# AGENTE DE ESTRATEGIA — {inf['video_id']}", '']
    L.append(f"cues con precio: {inf['n_cues_con_precio']}")
    L.append('')
    L.append('## Niveles que el canal DICE (con cita)')
    for n in inf['niveles_dichos'][:12]:
        L.append(f"- **{int(n['precio'])}** ×{n['menciones']} {n['pistas']}")
        L.append(f"  > {n['cita'][:120]}")
    c = inf.get('calculados')
    if c:
        L += ['', '## Calculados por el metodo (C05, no dichos)']
        if not c.get('fibo_por_plazo'):
            L.append('  (sin tramo: no se calcula)')
        for plazo, z in (c.get('fibo_por_plazo') or {}).items():
            L.append(f"- **{plazo}** ({z.get('tf')})")
            for k, v in (z.get('zonas_compra') or {}).items():
                L.append(f"    retroceso {k}: {v}")
            for k, v in (z.get('extensiones') or {}).items():
                L.append(f"    extension {k}: {v}")
        ab = c['abanico_intradia']
        L += ['', f"## Abanico intradia (punto cero {ab['punto_cero']:.0f} = cierre {HORA_ANCLA}:00, {ab['unidad']})"]
        L.append('  ' + ', '.join(f'{x:,.0f}' for x in ab['niveles']))
        if c.get('aviso'):
            L += ['', '> **' + c['aviso'] + '**']
    return '\n'.join(L)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--video', default='')
    ap.add_argument('--todos', action='store_true')
    ap.add_argument('--out', default='')
    a = ap.parse_args()
    import store as S
    conn = sqlite3.connect(f'file:{S.STORE_PATH}?mode=ro', uri=True)
    if a.video:
        ids = [a.video]
    elif a.todos:
        ids = [r[0] for r in conn.execute(
            "SELECT video_id FROM videos WHERE published IS NOT NULL "
            "GROUP BY substr(published,1,7) ORDER BY published DESC")]
    else:
        ids = [conn.execute('SELECT video_id FROM videos ORDER BY published DESC LIMIT 1').fetchone()[0]]
    for vid in ids:
        inf = informe(vid)
        txt = fmt(inf)
        print(txt)
        dst = pathlib.Path(a.out) if a.out else PILOT / 'investigacion' / f'AGENTE_{vid}.md'
        dst.write_text(txt)
        js = dst.with_suffix('.json')
        js.write_text(json.dumps(inf, ensure_ascii=False, indent=2))
        print(f'\n-> {dst}\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
