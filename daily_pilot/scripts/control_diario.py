#!/usr/bin/env python3
"""Control periodico del canal CreceTrader (cada 2 h, via LaunchAgent).

Actualiza daily_pilot/estado/estado_hoy.json con los estados canonicos.
NO ejecuta vision. NO toca E1. Reutiliza el flujo existente (daily_pilot.py).
"""
from __future__ import annotations

import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, '/Users/franciscootamendi/YouTubeTradingAgent')
sys.path.insert(0, '/Users/franciscootamendi/YouTubeTradingAgent/daily_pilot/scripts')

BASE = Path(__file__).resolve().parents[2]
PILOT = BASE / 'daily_pilot'
ESTADO = PILOT / 'estado' / 'estado_hoy.json'
ANALISIS = PILOT / 'analisis'

ESTADOS = ['SIN VIDEO NUEVO', 'VIDEO NUEVO ENCONTRADO', 'ANALISIS PENDIENTE',
           'VIDEO NUEVO ANALIZADO', 'ERROR DE ANALISIS']


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def hoy() -> str:
    """Frontera de 'hoy' en UTC (los detectado/analizado se guardan en UTC)."""
    return datetime.now(timezone.utc).strftime('%Y-%m-%d')


def evidencia(vid: str) -> dict | None:
    p = ANALISIS / f'{vid}_analisis.json'
    if not p.exists():
        return None
    try:
        d = json.loads(p.read_text(encoding='utf-8'))
    except Exception:
        return None
    if not d.get('analizado_at'):
        return None
    return {'archivo': str(p), 'analizado_at': d.get('analizado_at'), 'n_cues': d.get('n_cues')}


def _cargar_piloto():
    """Carga daily_pilot/scripts/daily_pilot.py por ruta (evita el namespace package)."""
    import importlib.util
    p = Path(__file__).resolve().parent / 'daily_pilot.py'
    spec = importlib.util.spec_from_file_location('piloto_diario', p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ultimo_analisis() -> dict | None:
    """El analisis mas reciente en daily_pilot/analisis/ (evidencia real)."""
    mejor = None
    for p in sorted((PILOT / 'analisis').glob('*_analisis.json')):
        try:
            d = json.loads(p.read_text(encoding='utf-8'))
        except Exception:
            continue
        if d.get('analizado_at') and (mejor is None or d['analizado_at'] > mejor[0]):
            mejor = (d['analizado_at'], d)
    return mejor[1] if mejor else None


def situacion_de(analisis: dict, video: dict | None) -> dict:
    """P0-5 FIX: la situacion se deriva del ULTIMO ANALISIS REAL, no del video nuevo."""
    if not analisis:
        return {'frase': 'NO DISPONIBLE · sin análisis completado', 'instrumento': 'NO DISPONIBLE',
                'temporalidad': 'NO DISPONIBLE', 'fuente': 'NO DISPONIBLE'}
    inst = list(analisis.get('instrumentos') or {}) or 'NO DISPONIBLE'
    return {
        'frase': (f"Último análisis real: {analisis.get('video_id')} · "
                  f"{analisis.get('n_cues')} cues · instrumentos {inst}"),
        'instrumento': inst,
        'temporalidad': 'NO DISPONIBLE',
        'evidencia': {'video_id': analisis.get('video_id'), 'analizado_at': analisis.get('analizado_at'),
                      'sha256_transcript': analisis.get('sha256_transcript')},
        'limitaciones': analisis.get('limitaciones') or [],
        'fuente': 'analisis/' + f"{analisis.get('video_id')}_analisis.json",
    }


def main() -> int:
    pd = _cargar_piloto()
    fetch_rss, cargar_registro, guardar_registro, transcribir = (
        pd.fetch_rss, pd.cargar_registro, pd.guardar_registro, pd.transcribir)
    rss = fetch_rss()
    reg = cargar_registro()
    errores = []
    ultimo = rss[0] if rss else None
    vid = ultimo['video_id'] if ultimo else None
    pendientes = []

    # detectar y procesar videos nuevos
    if vid and vid not in reg['videos']:
        try:
            tp = transcribir(vid)
            estado_reg = 'transcrito' if tp else 'sin_transcripcion'
        except Exception as exc:
            tp, estado_reg = None, f'error: {exc}'
            errores.append(f'{vid}: {exc}')
        reg['videos'][vid] = {
            'video_id': vid, 'titulo': ultimo.get('titulo', ''), 'published': ultimo.get('publicado', ''),
            'url': f'https://www.youtube.com/watch?v={vid}',
            'detectado': now_iso(), 'transcript': str(tp) if tp else None, 'estado': estado_reg}
        guardar_registro(reg)

    # derivar estado
    if not vid:
        estado = 'SIN VIDEO NUEVO'
    elif vid not in reg['videos']:
        estado = 'VIDEO NUEVO ENCONTRADO'
    else:
        ent = reg['videos'][vid]
        ev = evidencia(vid)
        if (ent.get('estado') or '').lower().startswith('error'):
            estado = 'ERROR DE ANALISIS'
        elif not ev:
            estado = 'ANALISIS PENDIENTE'
        elif (ent.get('detectado') or '')[:10] == hoy():
            estado = 'VIDEO NUEVO ANALIZADO'
        else:
            estado = 'SIN VIDEO NUEVO'
    if estado not in ESTADOS:
        estado = 'SIN VIDEO NUEVO'

    base = {}
    if ESTADO.exists():
        try:
            base = json.loads(ESTADO.read_text(encoding='utf-8'))
        except Exception:
            base = {}
    salida = dict(base)
    salida.update({
        'schema': 'ytra_estado_v1', 'paper_only': True,
        'aviso': 'PAPER ONLY · no ejecuta órdenes',
        'estado': estado, 'ultima_revision': now_iso(),
        'deteccion_at': reg['videos'].get(vid, {}).get('detectado') if vid else None,
        'analisis_at': (evidencia(vid) or {}).get('analizado_at') if vid else None,
        'video': ({'video_id': vid, 'titulo': ultimo.get('title') or ultimo.get('titulo'),
                   'url': ultimo.get('url') or f'https://www.youtube.com/watch?v={vid}',
                   'publicado': ultimo.get('published') or ultimo.get('publicado'),
                   'fuente': 'RSS CreceTrader'}
                  if ultimo else None),
        'errores': errores,
    })
    # P0-5: separar el estado del video nuevo del ULTIMO ANALISIS real
    ua = ultimo_analisis()
    salida['ultimo_analisis_completo'] = ({
        'video_id': ua.get('video_id'), 'analizado_at': ua.get('analizado_at'),
        'n_cues': ua.get('n_cues'), 'sha256_transcript': ua.get('sha256_transcript'),
        'archivo': f"daily_pilot/analisis/{ua.get('video_id')}_analisis.json"} if ua else None)
    # P0 FIX: un solo campo canonico. 'ultimo_analizado' quedaba con el video viejo.
    salida['ultimo_analizado'] = salida['ultimo_analisis_completo']
    salida['situacion'] = situacion_de(ua, salida.get('video'))
    # H-04 FIX: macro/escenarios heredados del video viejo contradicen el estado.
    # Solo se conservan si corresponden al ultimo analisis; si no, NO DETERMINADO.
    for k in ('macro', 'escenarios', 'escenarios_estado'):
        v = salida.get(k)
        vid_viejo = (v or {}).get('video_id') if isinstance(v, dict) else None
        # H-04: sin video_id o con otro video -> no se puede acreditar; NO DETERMINADO.
        if v is None or vid_viejo is None or vid_viejo != (ua or {}).get('video_id'):
            salida[k] = {'video_id': (ua or {}).get('video_id'), 'estado': 'NO DETERMINADO',
                         'motivo': 'no corresponde al ultimo analisis; recalcular desde analisis/'} \
                if k != 'escenarios_estado' else None
    ESTADO.parent.mkdir(parents=True, exist_ok=True)
    ESTADO.write_text(json.dumps(salida, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'[{now_iso()}] estado={estado} video={vid}')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        sys.exit(1)
