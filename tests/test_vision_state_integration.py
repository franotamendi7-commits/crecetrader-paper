#!/usr/bin/env python3
"""Integracion con las funciones REALES de produccion (sin Ollama, sin red).

Usa fixtures temporales. No toca datos historicos.
"""
import json
import sys
import threading
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tools'))

from scripts.rss_priority_processor import _save_analysis, save_state, load_state  # noqa: E402
from vision_preflight import validar_esquema, comprobar_rutas  # noqa: E402


def _state(video_id='V1', analysis=None):
    return {'videos': {video_id: {
        'title': 't', 'status': 'processing', 'retry_count': 0, 'last_error': None,
        'progress': {k: False for k in ('download', 'frames', 'transcript', 'vision', 'validation')},
        'artifacts': {'video_path': None, 'frames_dir': None,
                      'transcript_path': None, 'analysis_file': analysis}}}}


def test_save_state_real_atomico_y_regresable(tmp_path):
    pf = tmp_path / 'state.json'
    save_state(_state(), pf, None)
    assert pf.exists() and json.loads(pf.read_text())['videos']['V1']['title'] == 't'
    cargado = load_state(pf)
    assert cargado['videos']['V1']['status'] == 'processing'
    assert not pf.with_suffix('.json.tmp').exists()


def test_save_state_rutas_se_convierten_a_string(tmp_path):
    pf = tmp_path / 'state.json'
    s = _state(analysis='relativo/analysis.json')
    save_state(s, pf, None)
    assert isinstance(json.loads(pf.read_text())['videos']['V1']['artifacts']['analysis_file'], str)


def test_save_analysis_none_deriva_ruta(monkeypatch, tmp_path):
    """R1: con analysis_file=None se deriva la ruta esperada y no se crashea."""
    monkeypatch.setattr('scripts.rss_priority_processor.BASE_DIR', tmp_path)
    frame = ROOT / 'frames_hist/LFHkc5dUoLw/frame_3994.jpg'
    _save_analysis(None, 'V1', {'title': 't'}, frame, 'INSTRUMENT: BTCUSD', None)
    esperado = tmp_path / 'experimental' / 'results' / 'historical' / 'V1_analysis.json'
    assert esperado.exists()
    assert json.loads(esperado.read_text())['frame_results'][0]['vision'] == 'INSTRUMENT: BTCUSD'


def test_save_analysis_real_crea_y_no_duplica(tmp_path):
    af = tmp_path / 'analysis.json'
    frame = ROOT / 'frames_hist/LFHkc5dUoLw/frame_3994.jpg'
    _save_analysis(af, 'V1', {'title': 't'}, frame, 'INSTRUMENT: BTCUSD', None)
    _save_analysis(af, 'V1', {'title': 't'}, frame, 'INSTRUMENT: ETHUSD', None)
    d = json.loads(af.read_text())
    assert len(d['frame_results']) == 1
    assert d['frame_results'][0]['vision'] == 'INSTRUMENT: ETHUSD'
    assert d['frames_processed'] == 1


def test_save_analysis_escritura_atomica(tmp_path):
    """R3: el analisis se escribe de forma atomica (sin .tmp residual, JSON valido)."""
    af = tmp_path / 'analysis.json'
    frame = ROOT / 'frames_hist/LFHkc5dUoLw/frame_3994.jpg'
    _save_analysis(af, 'V1', {'title': 't'}, frame, 'x', None)
    assert af.exists()
    assert not list(tmp_path.glob('*.tmp'))
    assert json.loads(af.read_text())['video_id'] == 'V1'


def test_reanudacion_conserva_completados(tmp_path):
    af = tmp_path / 'analysis.json'
    f1 = ROOT / 'frames_hist/LFHkc5dUoLw/frame_3994.jpg'
    f2 = ROOT / 'frames_hist/LFHkc5dUoLw/frame_3995.jpg'
    _save_analysis(af, 'V1', {}, f1, 'INSTRUMENT: BTCUSD', None)
    _save_analysis(af, 'V1', {}, f2, '', None)          # pendiente (vacio)
    d = json.loads(af.read_text())
    hechos = [r['frame'] for r in d['frame_results'] if (r.get('vision') or '').strip()]
    assert hechos == ['frame_3994.jpg']
    assert d['frame_results'][1]['frame'] == 'frame_3995.jpg'


def test_rutas_desde_otro_directorio(tmp_path):
    """Las rutas relativas se resuelven contra el cwd; desde otro dir no existen."""
    entry = _state(analysis='data_hist/LFHkc5dUoLw/LFHkc5dUoLw_transcript.json')['videos']['V1']
    h = comprobar_rutas(entry, tmp_path)
    assert any(x['tipo'] == 'artefacto_ausente' for x in h)
    h2 = comprobar_rutas(entry, ROOT)
    assert not any(x['tipo'] == 'artefacto_ausente' for x in h2)


def test_concurrencia_sin_carrera(tmp_path):
    """R2: dos procesos concurrentes con el mismo progress_file no interfieren."""
    pf = tmp_path / 'state.json'
    errores = []

    def worker(n):
        try:
            for i in range(25):
                s = _state()
                s['videos']['V1']['retry_count'] = n * 100 + i
                save_state(s, pf, None)
        except Exception as e:                       # pragma: no cover
            errores.append(type(e).__name__)

    ts = [threading.Thread(target=worker, args=(n,)) for n in range(4)]
    [t.start() for t in ts]
    [t.join() for t in ts]
    assert not errores, f'carrera detectada: {errores}'
    d = json.loads(pf.read_text())
    assert d['videos']['V1']['retry_count'] >= 0
    assert not list(tmp_path.glob('*.tmp'))


def test_load_state_normaliza_rutas(tmp_path):
    """R4: load_state resuelve rutas relativas contra BASE_DIR (sin depender del cwd)."""
    pf = tmp_path / 'state.json'
    s = _state(analysis='data_hist/LFHkc5dUoLw/LFHkc5dUoLw_transcript.json')
    save_state(s, pf, None)
    cargado = load_state(pf)
    af = cargado['videos']['V1']['artifacts']['analysis_file']
    assert Path(af).is_absolute()
    assert str(ROOT) in af


def test_load_state_no_depende_del_cwd(tmp_path, monkeypatch):
    """R4: funciona igual desde cualquier directorio de trabajo."""
    pf = tmp_path / 'state.json'
    save_state(_state(analysis='data_hist/LFHkc5dUoLw/LFHkc5dUoLw_transcript.json'), pf, None)
    monkeypatch.chdir('/tmp')
    cargado = load_state(pf)
    assert Path(cargado['videos']['V1']['artifacts']['analysis_file']).is_absolute()


def test_validacion_esquema_preflight_real():
    real = json.loads((ROOT / 'experimental/results/historical_progress.json').read_text())
    mal = 0
    for e in real.get('videos', {}).values():
        if validar_esquema(e):
            mal += 1
    assert mal == 0
