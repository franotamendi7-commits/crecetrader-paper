#!/usr/bin/env python3
"""Fase 1 — Paquete de anotacion para la muestra ampliada (15 frames)."""
import csv
import json
from pathlib import Path
from PIL import Image, ImageDraw

BASE = Path('/Users/franciscootamendi/YouTubeTradingAgent')
B4 = BASE / 'benchmark_vision_b1'
OUT = B4 / 'B4_muestra_ampliada'
FICHAS = OUT / 'fichas'
FICHAS.mkdir(parents=True, exist_ok=True)
manifest = json.load(open(OUT / 'manifest_muestra_ampliada.json'))
TS = json.load(open(B4 / 'temporal' / 'timestamps.json'))

CAMPOS = ['instrument', 'exchange', 'timeframe', 'visible_price_labels',
          'horizontal_levels', 'trendlines', 'market_structure', 'liquidity_zones',
          'indicators', 'visible_candlestick_information', 'unreadable_information',
          'abstentions']

for m in manifest:
    vid = m['video_id']
    f = m['frame']
    pts = m['pts_time']
    idx = m['idx']
    orig = BASE / 'frames_hist' / vid / f
    md = [f"# Ficha — {vid} / {f}", "",
          f"- Video: `{vid}`", f"- Frame: `{f}`", f"- Indice: {idx}",
          f"- Timestamp: **{pts} s**",
          f"- Escena: {m['escena']}", f"- Motivo: {m['motivo']}",
          f"- Original: `frames_hist/{vid}/{f}`", "",
          "Completá con lo que **se ve**. Reglas en `../B4_GUIA_ANOTACION_HUMANA.md` "
          "y `../B4_ESQUEMA_ANOTACION.md` (plantilla v2).", "",
          "| Campo | Valor | Legibilidad (1 claro/2 parcial/3 no legible/4 no presente) | Confianza (1-5) | Justificacion |",
          "|---|---|---|---|---|"]
    for c in CAMPOS:
        md.append(f"| **{c}** | | | | |")
    md += ["", "## Precios", "", "| Valor | Ubicacion | Legibilidad | Confianza | Justificacion |",
           "|---|---|---|---|---|"]
    for _ in range(8):
        md.append("| | | | | |")
    md += ["", f"**Criterio:** si existe texto pero el valor exacto no es determinable con seguridad, "
           f"`NO LEGIBLE`. No anotar el valor 'mas probable'.", ""]
    (FICHAS / f"ficha_{vid}_{f}.md").write_text("\n".join(md), encoding='utf-8')

# contact sheet
COLS, CW, CH, LH = 4, 640, 352, 26
rows = (len(manifest) + COLS - 1) // COLS
canvas = Image.new('RGB', (COLS * CW, rows * (CH + LH)), (20, 20, 20))
dr = ImageDraw.Draw(canvas)
for i, m in enumerate(manifest):
    im = Image.open(BASE / 'frames_hist' / m['video_id'] / m['frame']).convert('RGB')
    im.thumbnail((CW, CH))
    x = (i % COLS) * CW
    y = (i // COLS) * (CH + LH)
    canvas.paste(im, (x, y + LH))
    dr.text((x + 4, y + 6), f"{m['video_id']} | {m['frame']} | {m['pts_time']}s", fill=(255, 220, 0))
canvas.save(OUT / 'contact_sheet_ampliada.jpg', quality=88)

(OUT / 'LEEME.md').write_text("""# B4 — Muestra ampliada (15 frames)

Seleccion experimental NO redundante. **No sustituye la seleccion historica de B1.**

- Manifest: `manifest_muestra_ampliada.csv` / `.json`
- Fichas: `fichas/`
- Contact sheet: `contact_sheet_ampliada.jpg` (complementaria, no reemplaza los originales)

## Distribucion para dos anotadores

- **Doble ciego completo**: los dos anotadores reciben las mismas 15 fichas y las completan por separado.
- Alternativa: 8 comunes + 7 exclusivas cada uno.

Cada uno volca a `anotador1.csv` / `anotador2.csv` con la estructura de
`../B4_referencia_humana_template_v2.csv`. Un tercero adjudica desacuerdos.

## Reglas

Ver `../B4_GUIA_ANOTACION_HUMANA.md` y `../B4_ESQUEMA_ANOTACION.md`.
Criterio: claro → transcribir; duda → `NO LEGIBLE`; inexistente → `NO PRESENTE`.
""", encoding='utf-8')
print('fichas:', len(list(FICHAS.glob('ficha_*.md'))))
print('contact sheet:', (OUT / 'contact_sheet_ampliada.jpg').stat().st_size, 'bytes')
