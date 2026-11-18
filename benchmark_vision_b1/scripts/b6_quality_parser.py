#!/usr/bin/env python3
"""B6 (PROTOTIPO AISLADO, no conectado a produccion): parser y control de calidad
de respuestas de vision. Lee los *_analysis.json existentes; no reproduce videos.

Salida por frame: valid | needs_review | rejected + motivos.
IMPORTANTE: los rangos de precio son CONTROLES DE PLAUSIBILIDAD, no verificacion
visual. Que un numero sea plausible no prueba que este escrito en el grafico.
"""
import json
import re
from pathlib import Path

BASE = Path('/Users/franciscootamendi/YouTubeTradingAgent')
OUT = BASE / 'benchmark_vision_b1'
VIDEOS = ['EJoLhxbwYxo', 'LFHkc5dUoLw', 'LzPTdClLo_w', 'XLgPycsN0ls',
          'dPHvRw1wzYQ', 'jeOFS1TZYQA', 's3KxjqkzwKM', 'scJ-ai2FRiE']

INSTRUMENTOS = {'BTCUSD', 'ETHUSD', 'ES', 'NQ', 'XAUUSD', 'AMD', 'MDT',
                'VX1!', 'SPX', 'SP500', 'NDX', 'OTHER', 'UNKNOWN'}
# Ordenes de magnitud plausibles (control de plausibilidad, NO verificacion visual)
RANGOS = {
    'BTCUSD': (1e4, 1e6), 'ETHUSD': (1e2, 1e5), 'XAUUSD': (1e2, 1e5),
    'ES': (1e3, 1e5), 'NQ': (1e3, 1e6), 'AMD': (1e1, 1e4), 'MDT': (1e1, 1e4),
    'VX1!': (1e1, 1e3), 'SPX': (1e3, 1e5), 'SP500': (1e3, 1e5), 'NDX': (1e3, 1e6),
}
MAX_NIVELES = 12
PLANTILLA = 'list visible prices or null'


def parse_resp(v):
    """Parser tolerante: reconoce campos con o sin prefijo."""
    r = {'raw': v}
    m = re.search(r'INSTRUMENT:\s*([^\n\[]+)', v)
    r['instrument'] = m.group(1).strip().strip('()') if m else None
    m = re.search(r'TIMEFRAME:\s*([^\n\[]+)', v)
    r['timeframe'] = m.group(1).strip().strip('()') if m else None
    m = re.search(r'PRICES:\s*\[([^\]]*)\]', v)
    r['prices_raw'] = m.group(1).strip() if m else None
    m = re.search(r'STRUCTURE:\s*([^\n]+)', v)
    r['structure'] = m.group(1).strip() if m else None
    m = re.search(r'INDICATORS:\s*([^\n]+)', v)
    r['indicators'] = m.group(1).strip() if m else None
    # fallback sin prefijos: primera linea = instrumento
    if r['instrument'] is None:
        lineas = [l.strip() for l in v.strip().splitlines() if l.strip()]
        if lineas:
            r['instrument'] = lineas[0].split(',')[0]
        if len(lineas) > 1:
            r['timeframe'] = lineas[1]
    r['prices'] = nums(r['prices_raw']) if r['prices_raw'] is not None else None
    return r


def nums(s):
    out = []
    for tok in s.split(','):
        t = tok.strip()
        if not t:
            continue
        m = re.match(r'^([-+]?\d+)\.(\d+)$', t)
        if m:
            ent, dec = m.group(1), m.group(2)
            if len(dec) == 3:          # 7.619 -> 7619 (separador de miles)
                out.append(float(ent + dec))
            elif len(dec) <= 2:        # 78.71 -> 78.71 (posible miles ambiguo)
                out.append(float(ent + '.' + dec))
            else:
                out.append(float(ent + '.' + dec))
            continue
        try:
            out.append(float(t))
        except ValueError:
            pass
    return out


def evaluar(v):
    motivos = []
    rechazos = []
    r = parse_resp(v)
    raw_low = (v or '').lower()

    # R1 plantilla sin rellenar
    if PLANTILLA in raw_low:
        rechazos.append('R1_texto_plantilla_sin_rellenar')
    # R2 campos ausentes
    faltan = [c for c in ('instrument', 'timeframe', 'prices') if r.get(c) in (None, '', [])]
    if len(faltan) >= 2:
        rechazos.append('R2_campos_ausentes:' + ','.join(faltan))
    elif faltan:
        motivos.append('R2_campo_ausente:' + ','.join(faltan))
    # R3 instrumento desconocido
    inst = (r.get('instrument') or '').upper()
    if inst and inst not in INSTRUMENTOS:
        motivos.append(f'R3_instrumento_no_listado:{inst}')
    # R4 magnitud incompatible (plausibilidad)
    if inst in RANGOS and r['prices']:
        lo, hi = RANGOS[inst]
        fuera = [n for n in r['prices'] if not (lo <= n <= hi)]
        if fuera:
            motivos.append(f'R4_magnitud_improbable:{len(fuera)}/{len(r["prices"])}')
    # R5 exceso de niveles
    if r['prices'] and len(r['prices']) > MAX_NIVELES:
        motivos.append(f'R5_exceso_niveles:{len(r["prices"])}')
    # R6 duplicados exactos
    if r['prices'] and len(set(r['prices'])) < len(r['prices']):
        motivos.append('R6_precios_duplicados')
    # R7 secuencia artificial (paso constante) o cuenta atras hasta 0
    if r['prices']:
        ps = r['prices']
        if 0 in ps and len(ps) >= 6:
            rechazos.append('R7_secuencia_artificial_cuenta_atras')
        elif len(ps) >= 6:
            difs = [abs(ps[i + 1] - ps[i]) for i in range(len(ps) - 1)]
            if difs and max(difs) <= max(ps) * 0.02:
                motivos.append('R7_secuencia_paso_constante')
    # R8 respuesta truncada (sin campo final o con corchete sin cerrar)
    if 'INDICATORS:' not in (v or '') or v.count('[') > v.count(']'):
        rechazos.append('R8_respuesta_truncada')
    # R9 UNKNOWN con precios presentes
    if inst == 'UNKNOWN' and r['prices']:
        motivos.append('R9_unknown_con_precios')
    # nota: verificabilidad visual (no hay OCR de referencia)
    nota = 'verificacion_visual_no_disponible'

    if rechazos:
        estado = 'rejected'
    elif motivos:
        estado = 'needs_review'
    else:
        estado = 'valid'
    return {'estado': estado, 'rechazos': rechazos, 'motivos': motivos,
            'nota': nota, 'parse': {k: r.get(k) for k in
            ('instrument', 'timeframe', 'structure', 'indicators')},
            'n_precios': len(r['prices']) if r['prices'] else 0}


def main():
    resumen = {}
    filas = []
    for vid in VIDEOS:
        p = BASE / 'experimental' / 'results' / 'historical' / f'{vid}_analysis.json'
        if not p.exists():
            continue
        d = json.load(open(p))
        counts = {'valid': 0, 'needs_review': 0, 'rejected': 0}
        for fr in d['frame_results']:
            ev = evaluar(fr.get('vision', ''))
            counts[ev['estado']] += 1
            filas.append({'video_id': vid, 'frame': fr['frame'], **{k: v for k, v in ev.items() if k != 'parse'}})
        resumen[vid] = {'total': sum(counts.values()), **counts}
    (OUT / 'results' / 'b6_parser_report.json').write_text(json.dumps(
        {'resumen': resumen, 'filas': filas}, ensure_ascii=False, indent=2))
    print(f"{'video':16} {'total':>5} {'valid':>6} {'review':>7} {'rejected':>9}")
    for vid, c in resumen.items():
        print(f"{vid:16} {c['total']:>5} {c['valid']:>6} {c['needs_review']:>7} {c['rejected']:>9}")
    print('TOTAL', {k: sum(c[k] for c in resumen.values()) for k in ('total', 'valid', 'needs_review', 'rejected')})


if __name__ == '__main__':
    main()
