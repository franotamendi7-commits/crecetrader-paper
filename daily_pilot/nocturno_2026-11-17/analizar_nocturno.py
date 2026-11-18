#!/usr/bin/env python3
"""Analisis textual asistido de los videos nocturnos (NO interpretacion de graficos).

Reglas:
- EXPLICO : numero o afirmacion dicha en la transcripcion, con timestamp.
- INTERPRETACION : inferencia del analista, marcada como tal.
- NO_DETERMINADO : sin evidencia suficiente.
Nada de lo aqui generado es una operacion ni un nivel validado.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent
TS = re.compile(r'^(\d+):(\d{2}):(\d{2})[.,](\d{3})$')
NUM = re.compile(r'(?<![\d.])(\d{1,3}(?:[.,]\d{3})+(?:[.,]\d+)?|\d{2,3}(?:[.,]\d{3})+)(?![\d])')

INSTRUMENTOS = {
    'BTC': r'\bBTC\b|Bitcoin|bitcoin',
    'ETH': r'\bETH\b|Ethereum|ethereum',
    'SPX': r'\bSPX\b|S&P\s?500|SP500',
    'QQQ': r'\bQQQ\b',
    'NQ': r'\bNQ\b|Nasdaq\s?100|futuro',
    'XAUUSD': r'\boro\b|XAU|gold',
}

TEMPORALIDADES = {
    'Weekly': r'semanal|weekly|semana',
    'Daily': r'diario|diaria|daily|dia ',
    '4H': r'4\s?h|4h|cuatro horas',
    'Intradia': r'intrad[ií]a|intradia|intrad[ií]o|rango',
}

CONCEPTOS = {
    'fibonacci': r'fibonacci|fibo',
    'liquidez': r'liquidez|l[ií]quido',
    'acumulacion': r'acumulaci[oó]n|acumular',
    'distribucion': r'distribuci[oó]n|distribuir',
    'fomo': r'fomo',
    'holders': r'holders?|inversores|dinero institucional|instituciones',
    'estructura': r'estructura|m[aá]ximos y m[ií]nimos|maximos decrecientes|minimos decrecientes',
    'tendencia': r'tendencia|alcista|bajista',
    'rango': r'rango|lateralidad|lateral',
    'soporte': r'soporte|sostener',
    'resistencia': r'resistencia|techo',
    'invalidacion': r'invalidaci[oó]n|invalida|invalidar',
    'stop': r'\bstop\b|p[eé]rdida',
    'objetivo': r'objetivo|meta|proyecci[oó]n|proyecta',
    'entrada': r'entrada|comprar|compro|compramos',
    'volumen': r'volumen|volume',
    'reversal': r'reversi[oó]n|revertir|girar',
    'divergencia': r'divergencia|diverge',
    'techo_techo': r'techo|triple techo|double top|doble techo',
    'catalizador': r'catalizador|CPI|FOMC|Fed|etfs|IPC',
}

ESCENARIOS = {
    'alcista': r'alcista|sube|subir|repunte|rebote|recuperar|recuperaci[oó]n',
    'bajista': r'bajista|cae|caer|ca[ií]da|rompe a la baja|correcci[oó]n',
}

CONDICIONES = {
    'activacion': r'\bsi\b|mientras|siempre que|a menos que|para que',
    'entrada': r'entrada|comprar|compro|aquisición|zona de compras',
    'invalidacion': r'invalidaci[oó]n|stop|rompa|por debajo de|por encima de',
}


def parse_vtt(path: Path) -> list[dict]:
    texto = path.read_text(encoding='utf-8', errors='replace')
    cues = []
    bloque = []
    for linea in texto.splitlines():
        if '-->' in linea:
            partes = [x.strip() for x in linea.split('-->')]
            if len(partes) >= 2:
                bloque = [partes[0], partes[1].split()[0]]
        elif linea.strip() and bloque and not linea.startswith('WEBVTT') \
                and not linea.startswith('Kind:') and not linea.startswith('Language:'):
            if len(bloque) == 2:
                limpio = re.sub(r'<[^>]+>', '', linea.strip()).strip()
                if limpio:
                    cues.append({'start': bloque[0], 'end': bloque[1], 'text': limpio})
                bloque = []
    # normaliza a HH:MM:SS.mmm
    out = []
    for c in cues:
        s, e = c['start'], c['end']
        m = TS.match(s)
        if not m:
            continue
        out.append({'start': f'{int(m.group(1)):02d}:{m.group(2)}:{m.group(3)}.{m.group(4)}',
                    'end': e, 'text': c['text']})
    # dedup por (start,text)
    visto = set(); fin = []
    for c in out:
        k = (c['start'], c['text'])
        if k in visto:
            continue
        visto.add(k); fin.append(c)
    return fin


def hhmm(ts: str) -> str:
    m = TS.match(ts)
    return f'{int(m.group(1)):02d}:{m.group(2)}' if m else ts


def analizar(vid: str, cues: list[dict], meta: dict) -> dict:
    Completo = ' '.join(c['text'] for c in cues)
    por_ventana = {}
    for c in cues:
        t = c['text']
        for inst, pat in INSTRUMENTOS.items():
            if re.search(pat, t, re.I):
                por_ventana.setdefault(inst, []).append(hhmm(c['start']))
    niveles = []
    for c in cues:
        for m in NUM.finditer(c['text']):
            niveles.append({'valor': m.group(1), 'ts': hhmm(c['start']),
                            'contexto': c['text'][:140]})
    conceptos = {}
    for nombre, pat in CONCEPTOS.items():
        hits = [hhmm(c['start']) for c in cues if re.search(pat, c['text'], re.I)]
        if hits:
            conceptos[nombre] = {'menciones': len(hits), 'primeros': hits[:6]}
    escenarios = {}
    for nombre, pat in ESCENARIOS.items():
        hits = [{'ts': hhmm(c['start']), 'texto': c['text'][:120]}
                for c in cues if re.search(pat, c['text'], re.I)]
        if hits:
            escenarios[nombre] = hits[:8]
    condiciones = {}
    for nombre, pat in CONDICIONES.items():
        hits = [{'ts': hhmm(c['start']), 'texto': c['text'][:120]}
                for c in cues if re.search(pat, c['text'], re.I)]
        if hits:
            condiciones[nombre] = hits[:8]
    return {
        'video_id': vid,
        'titulo': meta.get('title'),
        'fecha_titulo': meta.get('fecha'),
        'duracion_s': meta.get('duration'),
        'n_cues': len(cues),
        'instrumentos_mencionados': {k: len(v) for k, v in por_ventana.items()},
        'instrumentos_ts': {k: v[:6] for k, v in por_ventana.items()},
        'temporalidades': {k: len([1 for c in cues if re.search(p, c['text'], re.I)])
                           for k, p in TEMPORALIDADES.items()},
        'niveles_explicitos': niveles[:120],
        'n_niveles': len(niveles),
        'conceptos': conceptos,
        'escenarios': escenarios,
        'condiciones': condiciones,
        'limitaciones': [
            'Analisis TEXTUAL unicamente: sin verificacion visual de graficos.',
            'Los numeros provienen de la transcripcion; no contrastados con feed.',
            'Los niveles son historicos; no tratar como vigentes sin confirmacion.',
        ],
    }


def main() -> None:
    listado = {}
    for linea in (BASE / '_listado.txt').read_text().splitlines():
        partes = linea.split('|')
        if len(partes) >= 3:
            listado[partes[0]] = {'title': partes[1], 'duration': partes[2]}
    FECHAS = {
        'cjUwyMHygEs': '2026-10-29', 'xHR9d-0ToXU': '2026-10-29', 'lwb4Qxy8D9w': '2026-10-28',
        '3OZ2vJPj92o': '2026-10-28', 'CmbG9QntQ10': '2026-10-27', 'G3GPk1mxPcQ': '2026-10-26',
        'D6XrdvQVTgk': '2026-10-26', 'ac6-r7g8pao': '2026-10-24', 'TT07djUkfhE': '2026-10-23',
        'B4Vf3bSk5GY': '2026-10-22', 'lkMTbT7tK8c': '2026-10-22', 'NVZfPTaeuLc': '2026-10-22',
        '0JHYwOCzCKI': '2026-10-21', 'avNOZfXdyX8': '2026-10-21', '2QjLmPdDKlk': '2026-10-20',
        'nqzn3DsZzKU': '2026-10-19', 'MgTOoUWEq-M': '2026-10-19', 'y9gsOU6_Bzw': '2026-10-18',
        'FkPGRd7kXnE': '2026-10-17', '_Lxz34x7eGg': '2026-10-16',
    }
    resumen = {}
    for vid in FECHAS:
        d = BASE / vid
        vtt = sorted(d.glob('*.vtt'))
        if not vtt:
            resumen[vid] = {'estado': 'SIN_VTT'}
            continue
        cues = parse_vtt(vtt[0])
        meta = dict(listado.get(vid, {}))
        meta['fecha'] = FECHAS[vid]
        r = analizar(vid, cues, meta)
        (d / f'{vid}_analisis.json').write_text(json.dumps(r, ensure_ascii=False, indent=2))
        resumen[vid] = {'estado': 'OK', 'cues': r['n_cues'], 'niveles': r['n_niveles'],
                        'instrumentos': r['instrumentos_mencionados']}
        print(f"{vid} cues={r['n_cues']} niveles={r['n_niveles']}", flush=True)
    (BASE / 'nocturno_resumen.json').write_text(json.dumps(resumen, ensure_ascii=False, indent=2))
    print('OK resumen')


if __name__ == '__main__':
    main()
