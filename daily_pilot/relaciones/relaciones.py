#!/usr/bin/env python3
"""C2 — Relacion entre videos a partir de claims (PAPER_ONLY).

Produce:
  - niveles_repetidos: mismo nivel (con tolerancia) en >=2 videos distintos
  - contradicciones: mismo nivel con sentidos opuestos (alcista/bajista)
  - linea_de_tiempo: por video, niveles y sentido
Metodo declarado: normalizacion de numeros en es-ES, agrupacion por
instrumento (regex) y tolerancia relativa. No usa vision.
"""
from __future__ import annotations

import json
import re
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, '/Users/franciscootamendi/YouTubeTradingAgent/daily_pilot/knowledge')
import store as S

INSTRUMENTOS = [
    ('BTCUSD', re.compile(r'\b(btc|bitcoin)\b', re.I)),
    ('ETHUSD', re.compile(r'\b(eth|ethereum)\b', re.I)),
    ('XAUUSD', re.compile(r'\b(oro|xau|gold)\b', re.I)),
    ('QQQ', re.compile(r'\b(qqq|nasdaq|nq)\b', re.I)),
    ('SPX', re.compile(r'\b(spx|s&p|s&p\s?500)\b', re.I)),
]
SENTIDO = [
    ('alcista', re.compile(r'\b(sube|suba|alcista|al alza|repunte|rebote|compra|comprar|compramo|'
                           r'reversi[oó]n alcista|rompe hacia arriba|m[aá]ximos)\b', re.I)),
    ('bajista', re.compile(r'\b(baja|bajista|a la baja|correcci[oó]n|corrige|caida|ca[ií]da|venta|vender|'
                           r'reversi[oó]n bajista|rompe hacia abajo|m[ií]nimos)\b', re.I)),
]
NUM = re.compile(r'(?<![\d.])(\d{1,3}(?:[.,]\d{3})+|\d{4,})(?![\d])')


def normalizar_numero(s: str):
    """'69.000' -> 69000 ; '1.780,5' -> 1780.5 ; '69,5' -> 69.5"""
    if not s:
        return None
    t = s.strip()
    if ',' in t and '.' in t:
        t = t.replace('.', '').replace(',', '.')
    elif ',' in t:
        t = t.replace(',', '.') if len(t.split(',')[1]) <= 2 else t.replace(',', '')
    else:
        t = t.replace('.', '') if re.search(r'\.\d{3}$', t) else t
    try:
        v = float(t)
    except ValueError:
        return None
    return v if v >= 1 else None


def instrumento(texto: str) -> str:
    """P1-3 FIX: un solo instrumento por cue. Si hay 0 o >1, NO_DETERMINADO
    (evita asignar todos los números del cue a un instrumento equivocado)."""
    hits = [nombre for nombre, pat in INSTRUMENTOS if pat.search(texto or '')]
    if len(hits) == 1:
        return hits[0]
    return 'NO_DETERMINADO'


VENTANA_ANTES, VENTANA_DESPUES = 80, 40


def instrumento_por_numero(texto: str, pos: int,
                            antes: int = VENTANA_ANTES,
                            despues: int = VENTANA_DESPUES) -> str:
    """P1-3 FIX (fin): instrumento por PROXIMIDAD al número, sin cruzar el fin
    de oración. «los 1.890. A continuación vemos el oro» -> 1890 NO es oro;
    «objetivo, 2132, 2077 igual que en el oro» -> 2132/2077 SÍ son oro."""
    if not texto:
        return 'NO_DETERMINADO'
    ini = max(0, pos - antes)
    fin = min(len(texto), pos + despues)
    corte = texto.find('. ', pos, fin)          # no cruzar "punto y aparte"
    if corte != -1:
        fin = corte
    seg = texto[ini:fin]
    hits = [nombre for nombre, pat in INSTRUMENTOS if pat.search(seg)]
    return hits[0] if len(hits) == 1 else 'NO_DETERMINADO'


def sentido(texto: str) -> str:
    for nombre, pat in SENTIDO:
        if pat.search(texto or ''):
            return nombre
    return 'neutro'


def instrumento_titulo(titulo: str) -> str:
    """Segunda fuente: el titulo del video. Solo si nombra UN unico instrumento."""
    hits = [nombre for nombre, pat in INSTRUMENTOS if pat.search(titulo or '')]
    return hits[0] if len(hits) == 1 else None


def cargar() -> list[dict]:
    conn = S.conectar()
    filas = conn.execute(
        'SELECT c.video_id, c.seq, c.start, c.texto, c.tipo, c.nivel, c.procedencia, '
        'c.temporalidad, v.title, v.published FROM claims c '
        'LEFT JOIN videos v ON v.video_id=c.video_id').fetchall()
    conn.close()
    out = []
    for vid, seq, start, texto, tipo, nivel, proc, tf, titulo, published in filas:
        inst_titulo = instrumento_titulo(titulo)
        pares = []
        for m in NUM.finditer(texto or ''):
            v = normalizar_numero(m.group(1))
            if not v:
                continue
            inst = instrumento_por_numero(texto, m.start())
            origen = 'proximidad'
            pares.append((v, inst, origen))
        out.append({'video_id': vid, 'seq': seq, 'start': start, 'texto': texto,
                    'tipo': tipo, 'nivel': nivel, 'procedencia': proc,
                    'timeframe': tf or 'neutro',   # C12: OB/zona depende de la temporalidad
                    'published': published, 'titulo': titulo,
                    'instrumento': instrumento(texto),
                    'sentido': sentido(texto),
                    'nums_inst': pares,
                    'numeros': [v for v, _, _ in pares]})
    return out


def clave_nivel(v: float, tol: float = 0.005) -> int:
    """Banda logaritmica: mismo entero si los valores difieren < tol (relativo)."""
    import math
    return int(round(math.log(v) / math.log(1.0 + tol)))


# Rango plausible declarado por instrumento: filtra anos, percentiles y ruido.
RANGO = {
    'BTCUSD': (5000.0, 250000.0),
    'ETHUSD': (300.0, 10000.0),
    'XAUUSD': (500.0, 6000.0),
    'QQQ': (100.0, 1000.0),
    'SPX': (1000.0, 10000.0),
}
ANOS = set(range(1990, 2036))


def plausible(inst: str, v: float) -> bool:
    if v in ANOS:
        return False
    r = RANGO.get(inst)
    return bool(r) and r[0] <= v <= r[1]


def analizar(claims: list[dict], tol: float = 0.005) -> dict:
    por_inst = defaultdict(lambda: defaultdict(list))
    descartados = 0
    for c in claims:
        for v, inst, _origen in (c.get('nums_inst') or []):
            if inst == 'NO_DETERMINADO':
                descartados += 1
                continue
            if not plausible(inst, v):
                descartados += 1
                continue
            por_inst[inst][clave_nivel(v, tol)].append((v, c))
    repetidos, contradicciones = [], []
    for inst, grupos in por_inst.items():
        for _, items in grupos.items():
            videos = {c['video_id'] for _, c in items}
            vals = sorted({v for v, _ in items})
            if len(videos) >= 2:
                repetidos.append({'instrumento': inst, 'nivel_aproximado': vals[0],
                                  'variantes': vals[:6], 'n_videos': len(videos),
                                  'videos': sorted(videos)[:8]})
            sentidos = {c['sentido'] for _, c in items} - {'neutro'}
            if len(sentidos) > 1:
                contradicciones.append({'instrumento': inst, 'nivel_aproximado': vals[0],
                                        'sentidos': sorted(sentidos), 'n_videos': len(videos),
                                        'ejemplos': [{'video': c['video_id'], 'start': c['start'],
                                                      'sentido': c['sentido'],
                                                      'texto': (c['texto'] or '')[:120]}
                                                     for _, c in items[:4]]})
    repetidos.sort(key=lambda x: -x['n_videos'])
    # Niveles sin instrumento: se reportan, NO se asignan a ciegas.
    sin_inst = defaultdict(int)
    for c in claims:
        for _v, inst, _o in (c.get('nums_inst') or []):
            if inst == 'NO_DETERMINADO':
                sin_inst[c['video_id']] += 1
    linea = defaultdict(list)
    for c in claims:
        insts = [i for _, i, _o in (c.get('nums_inst') or []) if i != 'NO_DETERMINADO']
        if insts:
            linea[c['video_id']].append({'published': c['published'],
                                         'instrumento': sorted(set(insts)),
                                         'numeros': c['numeros'][:5], 'sentido': c['sentido'],
                                         'start': c['start']})
    return {
        'metodo': ('instrumento y sentido por regex; nivel normalizado es-ES; '
                   f'agrupacion por banda relativa {tol:.1%}; sin vision'),
        'n_claims': len(claims), 'niveles_descartados': descartados,
        'niveles_sin_instrumento': dict(sin_inst),
        'niveles_repetidos': repetidos,
        'contradicciones': contradicciones,
        'linea_de_tiempo': {k: v for k, v in sorted(linea.items())},
    }


if __name__ == '__main__':
    tol = float(sys.argv[1]) if len(sys.argv) > 1 else 0.005
    claims = cargar()
    res = analizar(claims, tol)
    out = Path(__file__).resolve().parent / 'relaciones.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, ensure_ascii=False, indent=2))
    print(f'claims={res["n_claims"]} repetidos={len(res["niveles_repetidos"])} '
          f'contradicciones={len(res["contradicciones"])} videos={len(res["linea_de_tiempo"])}')
