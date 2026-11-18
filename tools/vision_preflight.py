#!/usr/bin/env python3
"""Preflight de estado de vision — SOLO LECTURA.

Valida el esquema de cada estado historico, detecta analysis_file nulo, rutas
relativas ambiguas, artefactos ausentes y discrepancias de transcripcion.
Emite informe JSON y Markdown. NO llama a Ollama, red, ffmpeg, YouTube ni
servicios externos. NO modifica estados (el modo --repair esta desactivado).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DEFAULT_STATE = BASE / 'experimental' / 'results' / 'historical_progress.json'

CAMPOS_ARTIFACT = ('video_path', 'frames_dir', 'transcript_path', 'analysis_file')
PASOS = ('download', 'frames', 'transcript', 'vision', 'validation')


def validar_esquema(entry: dict) -> list:
    errores = []
    if not isinstance(entry, dict):
        return ['entrada no es un diccionario']
    if 'status' not in entry:
        errores.append('falta status')
    if not isinstance(entry.get('progress'), dict):
        errores.append('progress no es un diccionario')
    else:
        for p in PASOS:
            if p not in entry['progress']:
                errores.append(f'progress.{p} ausente')
    if 'artifacts' not in entry or not isinstance(entry.get('artifacts'), dict):
        errores.append('artifacts ausente o invalido')
    return errores


def resolver(ruta, cwd: Path):
    if ruta is None:
        return None
    p = Path(str(ruta))
    return p if p.is_absolute() else (cwd / p)


def comprobar_rutas(entry: dict, cwd: Path) -> list:
    """Detecta analysis_file nulo, rutas relativas ambiguas y artefactos ausentes."""
    hallazgos = []
    art = entry.get('artifacts') or {}
    for campo in CAMPOS_ARTIFACT:
        val = art.get(campo)
        if val is None:
            if campo in ('transcript_path', 'analysis_file'):
                hallazgos.append({'tipo': 'nulo', 'campo': campo,
                                  'detalle': f'{campo} es null'})
            continue
        p = Path(str(val))
        if not p.is_absolute():
            hallazgos.append({'tipo': 'ruta_relativa', 'campo': campo,
                              'detalle': f'{val} (relativa al cwd)'})
        rp = resolver(val, cwd)
        if rp is None or not rp.exists():
            hallazgos.append({'tipo': 'artefacto_ausente', 'campo': campo,
                              'detalle': f'{val} no existe'})
    return hallazgos


def estado_transcripcion(data_dir: Path, video_id: str) -> dict:
    """Detecta .vtt sin .json (el pipeline exige JSON)."""
    d = data_dir / video_id
    json_p = d / f'{video_id}_transcript.json'
    vtt = list(d.glob('*.vtt')) if d.exists() else []
    return {
        'video_id': video_id,
        'json_presente': json_p.exists(),
        'vtt_presente': bool(vtt),
        'discrepancia': bool(vtt) and not json_p.exists(),
    }


def guardar_atomico(path: Path, obj: dict) -> None:
    """Escritura atomica: tmp + os.replace + fsync."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(str(tmp), str(path))
    with open(path, 'ab') as fh:
        fh.flush()
        os.fsync(fh.fileno())


def reanudar_frames(analysis: dict) -> dict:
    """Devuelve el conjunto de frames ya completados y los pendientes."""
    resultados = analysis.get('frame_results', []) if isinstance(analysis, dict) else []
    hechos = [r for r in resultados if (r.get('vision') or '').strip()]
    return {
        'completados': [r.get('frame') for r in hechos],
        'pendientes': [r.get('frame') for r in resultados if r not in hechos],
        'duplicados': len(resultados) - len({r.get('frame') for r in resultados}),
    }


def preflight(state_path: Path = DEFAULT_STATE, cwd: Path = BASE) -> dict:
    state = json.loads(Path(state_path).read_text(encoding='utf-8'))
    videos = state.get('videos', {})
    out = {'state': str(state_path), 'videos': {}, 'resumen': {}}
    tot = {'nulos': 0, 'relativas': 0, 'ausentes': 0, 'discrepancias': 0, 'errores_esquema': 0}
    for vid, entry in videos.items():
        err = validar_esquema(entry)
        hall = comprobar_rutas(entry, cwd)
        trans = estado_transcripcion(cwd / 'data_hist', vid)
        tipos = {}
        for h in hall:
            tipos[h['tipo']] = tipos.get(h['tipo'], 0) + 1
        for k in tot:
            if k == 'errores_esquema':
                tot[k] += len(err)
            else:
                tot[k] += tipos.get({'nulos': 'nulo', 'relativas': 'ruta_relativa',
                                     'ausentes': 'artefacto_ausente',
                                     'discrepancias': None}.get(k, ''), 0)
        if trans['discrepancia']:
            tot['discrepancias'] += 1
        out['videos'][vid] = {'errores_esquema': err, 'hallazgos': hall,
                              'transcripcion': trans,
                              'progress': entry.get('progress')}
    out['resumen'] = {'videos': len(videos), **tot}
    return out


def a_markdown(inf: dict) -> str:
    r = inf['resumen']
    lineas = [f"# Preflight de estado de visión — {date.today().isoformat()}", "",
              f"Estado: `{inf['state']}`", "",
              f"Vídeos: {r['videos']} · analysis_file nulos: {r['nulos']} · "
              f"rutas relativas: {r['relativas']} · artefactos ausentes: {r['ausentes']} · "
              f"discrepancias de transcripción: {r['discrepancias']} · errores de esquema: {r['errores_esquema']}", ""]
    for vid, d in inf['videos'].items():
        if not d['errores_esquema'] and not d['hallazgos'] and not d['transcripcion']['discrepancia']:
            continue
        lineas.append(f"## {vid}")
        for e in d['errores_esquema']:
            lineas.append(f"- esquema: {e}")
        for h in d['hallazgos']:
            lineas.append(f"- {h['tipo']}: {h['campo']} — {h['detalle']}")
        if d['transcripcion']['discrepancia']:
            lineas.append(f"- transcripción: hay .vtt sin .json")
        lineas.append("")
    return "\n".join(lineas)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--state', default=str(DEFAULT_STATE))
    ap.add_argument('--check-only', action='store_true')
    ap.add_argument('--repair', action='store_true', help='NO implementado: no usar')
    ap.add_argument('--json-out', default=None)
    ap.add_argument('--md-out', default=None)
    a = ap.parse_args()
    if a.repair:
        print('ERROR: --repair no esta implementado. Solo lectura.')
        return 2
    inf = preflight(Path(a.state))
    md = a_markdown(inf)
    if a.json_out:
        Path(a.json_out).write_text(json.dumps(inf, ensure_ascii=False, indent=2))
    if a.md_out:
        Path(a.md_out).write_text(md)
    print(md)
    print('\n(resumen JSON)')
    print(json.dumps(inf['resumen'], ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
