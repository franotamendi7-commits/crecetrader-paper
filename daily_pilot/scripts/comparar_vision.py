#!/usr/bin/env python3
"""Compara la lectura del VLM contra la anotación humana de Francisco.

Uso:
  python3 daily_pilot/scripts/comparar_vision.py --humano TU_ANOTACION.csv --vlm /tmp/vision_19.json

 Métricas honestas:
  - acuerdo por campo (instrumento, estructura, vela)
  - precisión/recordación de NIVELES con tolerancia (por defecto 0.5%)
  - NO reporta "exactitud" sin ground truth firmado.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

CAMPOS = ('instrumento', 'estructura', 'vela_actual')

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--humano', required=True)
    ap.add_argument('--vlm', required=True)
    ap.add_argument('--tolerancia', type=float, default=0.005)
    a = ap.parse_args()

    vlm = json.loads(Path(a.vlm).read_text())
    def norm(s):
        """05 · 004_303.7s  <->  scene_004_303.7s.jpg"""
        s = str(s).strip()
        s = s.replace('scene_', '').replace('.jpg', '')
        s = s.split(' · ')[-1] if ' · ' in s else s
        return s.replace(' ', '')
    por_frame = {norm(r['frame']): r for r in vlm['frames']}

    filas = list(csv.DictReader(open(a.humano)))
    filas = [f for f in filas if (f.get('instrumento') or '').strip()]
    if not filas:
        print('La planilla humana está vacía: nada que comparar.')
        return 1

    n = len(filas)
    aciertos = {c: 0 for c in CAMPOS}
    niveles_ok, niveles_total, niveles_encontrados = 0, 0, 0

    for f in filas:
        fr = f['frame']
        r = por_frame.get(norm(fr))
        if not r or not r.get('json_valido'):
            print(f'  {fr:26s} SIN LECTURA DEL VLM')
            continue
        d = r['data']
        for c in CAMPOS:
            if (d.get(c) or '').upper() == (f.get({'vela_actual': 'vela'}.get(c, c)) or '').upper():
                aciertos[c] += 1
        # niveles
        reales = [float(x) for x in (f.get('niveles_que_se_ven') or '').split(';') if x.strip()]
        leidos = [n_['precio'] for n_ in d.get('niveles_visibles', [])
                  if isinstance(n_.get('precio'), (int, float)) and n_['precio'] > 0]
        for real in reales:
            niveles_total += 1
            if any(abs(l - real) / real <= a.tolerancia for l in leidos):
                niveles_ok += 1
        niveles_encontrados += len(leidos)
        print(f"  {fr:26s} VLM={str(d.get('instrumento')):8s}/{str(d.get('estructura')):20s} "
              f"niveles_leidos={len(leidos)} niveles_tuyos={len(reales)}")

    print('\n=== ACUERDO POR CAMPO ===')
    for c in CAMPOS:
        print(f'  {c:14s} {aciertos[c]}/{n}  ({100*aciertos[c]/n:.0f}%)')
    if niveles_total:
        print(f'\nNIVELES: {niveles_ok}/{niveles_total} de los tuyos aparecieron en la lectura del VLM '
              f'(tolerancia {a.tolerancia:.1%})')
        print(f'         el VLM reportó {niveles_encontrados} niveles en total')
    else:
        print('\n(No anotaste niveles: no se puede medir niveles.)')
    print('\nIMPORTANTE: con', n, 'frames esto es una MUESTRA, no una métrica definitiva.')
    return 0

if __name__ == '__main__':
    sys.exit(main())
