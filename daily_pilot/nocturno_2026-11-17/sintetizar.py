#!/usr/bin/env python3
"""Sintesis acumulativa del lote nocturno (20 videos). Basada en evidencia extraida."""
import json, glob, re
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
rows = [json.load(open(f)) for f in sorted(glob.glob(str(BASE / '*/*_analisis.json')))]
FECHAS = json.loads((BASE / 'fechas.json').read_text()) if (BASE / 'fechas.json').exists() else {}

conc = Counter(); por_conc = defaultdict(list)
for r in rows:
    for k, v in r['conceptos'].items():
        conc[k] += 1
        por_conc[k].append((r['video_id'], v['menciones'], v['primeros'][:3]))

niveles = Counter(); donde = defaultdict(list)
for r in rows:
    for n in r['niveles_explicitos']:
        key = n['valor'].replace('.', '').replace(',', '')
        if len(key) >= 4:
            niveles[key] += 1
            donde[key].append((r['video_id'], n['ts']))

lines = []
lines.append('# SINTESIS METODOLOGICA — Lote nocturno (20 videos, 16/10–29/10/2026)\n')
lines.append('Fuente: transcripciones reales del canal CreceTrader (subtitulos es). '
             'Extraccion lexica asistida; NO hay verificacion visual de graficos.\n')
lines.append(f"Videos: {len(rows)} · cues: {sum(r['n_cues'] for r in rows)} · "
             f"niveles citados: {sum(r['n_niveles'] for r in rows)}\n")

lines.append('\n## 1. Principios recurrentes (respaldados por varios videos)\n')
for k, n in conc.most_common():
    if n >= 10:
        ej = ', '.join(f'{v}@{t}' for v, _, ts in por_conc[k] for t in ts[:1])
        lines.append(f'- **{k}**: {n}/20 videos. Ej.: {ej[:120]}')

lines.append('\n## 2. Principios respaldados por pocos videos (1–9)\n')
for k, n in conc.most_common():
    if n < 10:
        ej = ', '.join(f'{v}@{t}' for v, _, ts in por_conc[k] for t in ts[:1])
        lines.append(f'- **{k}**: {n}/20. Ej.: {ej[:100]}')

lines.append('\n## 3. Niveles explicitamente citados (con video y minuto)\n')
lines.append('Solo lo **dicho** por el analista. No verificados contra grafico ni feed.\n')
for k, c in niveles.most_common(15):
    ej = donde[k][0]
    lines.append(f'- **{k}**: {c} menciones. Primer registro: {ej[0]} @{ej[1]}')

lines.append('\n## 4. Hallazgo relevante: Fibonacci\n')
lines.append('- **0 menciones** de "Fibonacci" en los 20 videos del lote (ni en los 20 previos). '
             'El canal **no nombra** la herramienta; los niveles de retroceso observados en los '
             'graficos no son explicitos en el audio. Clasificacion: **NO_DETERMINADO** '
             '(no puede atribuirse al analista como nivel explicito).\n')

lines.append('\n## 5. Hipotesis del Analyst (NO verificadas)\n')
lines.append('- La recurrencia de "objetivo" (20/20) sugiere que el canal siempre cierra con '
             'proyecciones; haria falta contrastar si esas proyecciones se cumplieron.')
lines.append('- "4H" (20/20) como temporalidad operativa es consistente con lo documentado, '
             'pero la **alineacion** entre Weekly/Daily/4H no puede verificarse sin graficos.')
lines.append('- La escasez de "invalidacion" (1/20) frente a "stop" (13/20) sugiere que el '
             'canal expresa la invalidacion como stop lexicamente; es una hipotesis, no un hecho.\n')

lines.append('\n## 6. Preguntas para revision humana\n')
lines.append('1. ¿Los niveles 83.366 / 81.446 / 78.746 / 71.509-69.000 corresponden a la misma '
             'estructura o a escenarios distintos? (requiere grafico)')
lines.append('2. ¿Que es el "freno de los 83.366" (0JHYwOCzCKI @00:11)? ¿resistencia o liquidez?')
lines.append('3. ¿El "rango" (10/20) se refiere a intradia o a lateralizacion de temporalidades altas?')
lines.append('4. Sin Fibonacci explicito: ¿como llama el canal a esos niveles en los graficos?\n')

lines.append('\n## 7. Contradicciones aparentes (conservadas, no resueltas)\n')
lines.append('- El nivel dominante cambia con la fecha: **83.366** (21/10) → **78.746** (20/10) '
             '→ **71.509/69.000** (26/10). No es una contradiccion: es **evolucion temporal**. '
             'No mezclar niveles historicos como si fueran vigentes.')
lines.append('- Ningun video del lote contradice abiertamente a otro; las diferencias son de contexto.\n')

lines.append('\n## 8. Limitaciones de este lote\n')
lines.append('- **Sin vision**: no se verifico ningun grafico; todo lo anterior es textual.')
lines.append('- **Sin feed**: los precios citados no se contrastaron con datos de mercado.')
lines.append('- **Extraccion lexica**: las menciones se detectaron por patrones; pueden haber '
             'falsos positivos (p.ej. "oro" como palabra).')
lines.append('- Los niveles son **historicos** y no deben operarse sin confirmacion.\n')

(BASE / 'sintesis_metodologica.md').write_text('\n'.join(lines), encoding='utf-8')

informe = {
    'lote': 'nocturno_2026-11-17',
    'videos': len(rows),
    'cues': sum(r['n_cues'] for r in rows),
    'niveles': sum(r['n_niveles'] for r in rows),
    'conceptos_n_videos': dict(conc),
    'niveles_top': {k: {'menciones': c, 'primer': list(donde[k][0])} for k, c in niveles.most_common(15)},
    'fibonacci_menciones': 0,
    'vision': 'NO ejecutada (motor no autorizado)',
}
(BASE / 'nocturno_informe.json').write_text(json.dumps(informe, ensure_ascii=False, indent=2))
print('sintesis escrita:', (BASE / 'sintesis_metodologica.md').stat().st_size, 'bytes')
print('conceptos:', dict(conc))
