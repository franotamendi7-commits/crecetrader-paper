#!/usr/bin/env python3
"""B4 — Genera una ficha de anotacion por frame (20 fichas)."""
import json
from pathlib import Path

BASE = Path('/Users/franciscootamendi/YouTubeTradingAgent')
B4 = BASE / 'benchmark_vision_b1'
FICHAS = B4 / 'B4_fichas_anotacion'
FICHAS.mkdir(parents=True, exist_ok=True)
manif = json.load(open(BASE / 'entregas_a74' / 'LFHkc5dUoLw' / 'MANIFIESTO.json'))

CAMPOS = [
    ('instrument', 'Instrumento exacto (o NO LEGIBLE)'),
    ('exchange', 'Exchange / origen (o NO LEGIBLE)'),
    ('timeframe', 'Temporalidad (o NO LEGIBLE)'),
    ('visible_price_labels', 'Niveles de precio con etiqueta visible (valor;ubicacion;legibilidad;confianza;justificacion)'),
    ('horizontal_levels', 'Lineas horizontales (soporte/resistencia) y si tienen etiqueta'),
    ('trendlines', 'Directrices (direccion, origen, fin)'),
    ('market_structure', 'Estructura de mercado: tendencia / rango / soporte / resistencia'),
    ('liquidity_zones', 'Zonas de liquidez visibles (o NO PRESENTE)'),
    ('indicators', 'Indicadores: MA / Fibonacci / Volumen / ninguno'),
    ('visible_candlestick_information', 'Informacion de velas legible (OHLC, cuerpo, mecha) o NO LEGIBLE'),
    ('unreadable_information', 'Elementos ilegibles (listar)'),
    ('abstentions', 'Campos que el anotador se abstiene de valorar'),
]

LEG = '1=claramente legible | 2=parcialmente legible | 3=no legible | 4=no presente'

for m in manif:
    fid = m['frame_id']
    md = [f"# Ficha de anotacion — {fid}", "",
          f"- Frame: `{m['frame']}`",
          f"- Video: `{m['video_id']}`",
          f"- Indice de extraccion: {m['idx']}",
          f"- Timestamp (pts_time): **{m['pts_time']} s**  (fps {m['fps']})",
          f"- Resolucion: {m['ancho']}x{m['alto']} px",
          f"- Ruta original: `{m['ruta_original']}`",
          f"- Copia verificada: `{m['ruta_copia']}`",
          f"- MD5: `{m['md5']}`", "",
          "## Instrucciones", "",
          "Complete cada campo con lo que **se ve en la imagen**. No infiera.",
          "Legibilidad: " + LEG + ". Confianza: 1 (duda) a 5 (seguro).",
          "Si un dato no puede leerse, escriba `NO LEGIBLE`. Si no existe en la imagen, `NO PRESENTE`.",
          "Para cada precio: `valor | ubicacion aproximada | legibilidad | confianza | justificacion visual`.", "",
          "| Campo | Valor | Legibilidad | Confianza (1-5) | Justificacion visual |",
          "|---|---|---|---|---|"]
    for key, desc in CAMPOS:
        md.append(f"| **{key}** — {desc} | | | | |")
    md += ["", "## Lista de precios (transcribir exactamente como aparecen)", "",
           "| Valor | Ubicacion | Legibilidad | Confianza | Justificacion |", "|---|---|---|---|---|"]
    for _ in range(6):
        md.append("| | | | | |")
    md += ["", "## Observaciones", "", "", "## Adjudicacion (uso del tercer anotador)", "",
           "- Estado: `pendiente`", "- Adjudicador:", "- Motivo:", ""]
    (FICHAS / f"ficha_{m['frame']}.md").write_text("\n".join(md), encoding='utf-8')

print('fichas generadas:', len(list(FICHAS.glob('ficha_*.md'))))
