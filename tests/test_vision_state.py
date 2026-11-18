#!/usr/bin/env python3
"""Pruebas de persistencia y estado de vision (sin red, sin Ollama)."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'tools'))
from vision_preflight import (validar_esquema, comprobar_rutas, estado_transcripcion,
                              guardar_atomico, reanudar_frames)


def _entry(**art):
    base = {'status': 'processing',
            'progress': {k: False for k in ('download', 'frames', 'transcript', 'vision', 'validation')},
            'artifacts': {'video_path': None, 'frames_dir': None,
                          'transcript_path': None, 'analysis_file': None}}
    base['artifacts'].update(art)
    return base


def test_analysis_file_none():
    h = comprobar_rutas(_entry(analysis_file=None), Path('/tmp'))
    assert any(x['tipo'] == 'nulo' and x['campo'] == 'analysis_file' for x in h)


def test_directorio_destino_inexistente(tmp_path):
    h = comprobar_rutas(_entry(video_path=str(tmp_path / 'no' / 'x.mp4')), tmp_path)
    assert any(x['tipo'] == 'artefacto_ausente' for x in h)


def test_vtt_sin_json(tmp_path):
    d = tmp_path / 'VID'
    d.mkdir()
    (d / 'VID.es.vtt').write_text('WEBVTT\n')
    t = estado_transcripcion(tmp_path, 'VID')
    assert t['vtt_presente'] and not t['json_presente'] and t['discrepancia']


def test_escritura_atomica(tmp_path):
    p = tmp_path / 'state.json'
    guardar_atomico(p, {'a': 1})
    assert json.loads(p.read_text()) == {'a': 1}
    assert not p.with_suffix('.json.tmp').exists()


def test_interrupcion_antes_del_replace(tmp_path, monkeypatch):
    p = tmp_path / 'state.json'
    guardar_atomico(p, {'version': 'previa'})
    import os
    real = os.replace

    def boom(*a, **k):
        raise OSError('interrumpido')

    monkeypatch.setattr('vision_preflight.os.replace', boom)
    with pytest.raises(OSError):
        guardar_atomico(p, {'version': 'nueva'})
    monkeypatch.setattr('vision_preflight.os.replace', real)
    assert json.loads(p.read_text())['version'] == 'previa'


def test_reanudacion_no_duplica():
    an = {'frame_results': [
        {'frame': 'frame_0001.jpg', 'vision': 'BTCUSD'},
        {'frame': 'frame_0002.jpg', 'vision': 'BTCUSD'},
        {'frame': 'frame_0002.jpg', 'vision': 'BTCUSD'},
    ]}
    r = reanudar_frames(an)
    assert r['duplicados'] == 1
    assert r['completados'] == ['frame_0001.jpg', 'frame_0002.jpg', 'frame_0002.jpg']


def test_reanudacion_preserva_id_y_timestamp():
    an = {'frame_results': [
        {'frame': 'frame_0042.jpg', 'pts_time': 123.0, 'vision': 'ETHUSD'},
    ]}
    r = reanudar_frames(an)
    assert r['completados'] == ['frame_0042.jpg']
    assert an['frame_results'][0]['pts_time'] == 123.0
    assert an['frame_results'][0]['frame'] == 'frame_0042.jpg'


def test_validar_esquema_ok():
    assert validar_esquema(_entry()) == []
    assert validar_esquema({'status': 'x'}) != []
