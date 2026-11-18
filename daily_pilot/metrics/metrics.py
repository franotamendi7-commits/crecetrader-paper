#!/usr/bin/env python3
"""Metricas del piloto (PAPER_ONLY). Sin backtest, sin promesas.

Registra senales y resultados y calcula:
  - tasa de acierto (solo con resultados reales)
  - R medio y expectativa
  - drawdown de la curva de R acumulado
Si no hay resultados reales, NO inventa: marca NO DISPONIBLE y solo
muestra la expectativa TEORICA derivada de los R multiplos declarados.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
PILOT = BASE / 'daily_pilot'
DIR = PILOT / 'metrics'
SENALES = DIR / 'senales.jsonl'
RESULTADOS = DIR / 'resultados.jsonl'

PAPER_ONLY = True


def _append(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as f:
        f.write(json.dumps(obj, ensure_ascii=False) + '\n')


def _read(path: Path) -> list:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except Exception:
                pass
    return out


def registrar_senal(senal: dict, video_id: str = '', fecha: str = '') -> dict:
    e = {
        'video_id': video_id,
        'fecha': fecha or datetime.now(timezone.utc).strftime('%Y-%m-%d'),
        'id': senal.get('id'),
        'instrument': senal.get('instrument') or '',
        'direction': senal.get('direction') or '',
        'nivel': senal.get('nivel') or senal.get('tipo') or '',
        'decision_rm': senal.get('decision') or '',
        'r_multiples': senal.get('risk', {}).get('r_multiples') or [],
        'perdida_potencial': senal.get('risk', {}).get('perdida_potencial'),
    }
    _append(SENALES, e)
    return e


def registrar_resultado(senal_id: str, resultado: str, r_real: float | None = None) -> dict:
    assert resultado in ('OBJETIVO_ALCANZADO', 'INVALIDADO', 'EXPIRADO'), resultado
    e = {'fecha': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
         'id': senal_id, 'resultado': resultado, 'r_real': r_real}
    _append(RESULTADOS, e)
    return e


def calcular() -> dict:
    senales = _read(SENALES)
    resultados = _read(RESULTADOS)
    por_id = {r['id']: r for r in resultados}
    pares = [(s, por_id[s['id']]) for s in senales if s['id'] in por_id]
    out = {
        'paper_only': PAPER_ONLY,
        'n_senales': len(senales),
        'n_resultados': len(pares),
        'tasa_acierto': None,
        'r_medio': None,
        'expectativa': None,
        'drawdown_max': None,
        'disponible': False,
    }
    if pares:
        aciertos = sum(1 for _, r in pares if r['resultado'] == 'OBJETIVO_ALCANZADO')
        out['tasa_acierto'] = round(aciertos / len(pares), 4)
        rs = [r['r_real'] for _, r in pares if isinstance(r.get('r_real'), (int, float))]
        if rs:
            out['r_medio'] = round(sum(rs) / len(rs), 4)
            # P0-1 FIX: la expectativa ES la media de r_real. La formula anterior
            # (tasa*r_medio - (1-tasa)) descontaba dos veces los perdedores.
            out['expectativa'] = round(sum(rs) / len(rs), 4)
            out['n_r'] = len(rs)
            out['disponible'] = len(rs) >= 30
            if not out['disponible']:
                out['motivo'] = (f'muestra insuficiente: {len(rs)} resultados < 30 '
                                 f'(NO CONCLUYENTE, no se infla)')
            curva, pico, dd = 0.0, 0.0, 0.0
            for x in rs:
                curva += x
                pico = max(pico, curva)
                dd = max(dd, pico - curva)
            out['drawdown_max'] = round(dd, 4)
            if out['disponible']:
                out.pop('motivo', None)
        else:
            out['motivo'] = 'resultados sin r_real numerico'
    else:
        out['motivo'] = 'sin resultados reales registrados (NO DISPONIBLE, no se inventa)'
        rs = [x for s in senales for x in (s.get('r_multiples') or [])
              if isinstance(x, (int, float))]
        if rs:
            out['expectativa_teorica_r'] = round(sum(rs) / len(rs), 4)
            out['advertencia'] = ('expectativa derivada de R múltiplos DECLARADOS, '
                                  'no de resultados reales. No calibrada.')
    return out


if __name__ == '__main__':
    print(json.dumps(calcular(), ensure_ascii=False, indent=2))
