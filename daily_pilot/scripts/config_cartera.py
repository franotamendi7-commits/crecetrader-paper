#!/usr/bin/env python3
"""CONMUTADOR DE CONFIG — activar/desactivar el filtro de día SIN tocar el historial.

Cada operación del journal lleva config_version. Las viejas conservan la suya.
Así el forward nunca se reescribe: se decide con datos reales al final.

Uso:
    python3 daily_pilot/scripts/config_cartera.py --estado
    python3 daily_pilot/scripts/config_cartera.py --usar filtro_dia
    python3 daily_pilot/scripts/config_cartera.py --usar original
"""
from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
PILOT = BASE / 'daily_pilot'
sys.path.insert(0, str(PILOT / 'scripts'))
import estrategias_validadas as EV  # noqa: E402

CONFIG_FILE = PILOT / 'datos' / 'config_cartera.json'
JOURNAL = PILOT / 'datos' / 'tracker_paper.json'

VERSIONES = {
    'original': {
        'descripcion': 'Cartera mixta 6 pares sin filtro de día',
        'filtro_dias': None,
        'pares_filtrados': [],
        'esperanza_R': 0.142, 'dd_R': -98.1, 'por_mes': 63.9,
    },
    'filtro_dia': {
        'descripcion': 'Jue+Vie+Sáb solo en BTC y THETA (null 4/4)',
        'filtro_dias': [3, 4, 5],
        'pares_filtrados': ['BTCUSDT', 'THETAUSDT'],
        'esperanza_R': 0.161, 'dd_R': -82.2, 'por_mes': 50.0,
    },
}


def leer():
    if not CONFIG_FILE.exists():
        return {'version_activa': 'original', 'versiones': VERSIONES,
                'creado': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
                'nota': 'Cambiar con --usar. El journal conserva config_version por operación.'}
    try:
        return json.loads(CONFIG_FILE.read_text())
    except Exception:
        return {'version_activa': 'original', 'versiones': VERSIONES}


def escribir(d):
    CONFIG_FILE.write_text(json.dumps(d, indent=2, ensure_ascii=False) + '\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--usar', choices=list(VERSIONES), help='activar una versión')
    ap.add_argument('--estado', action='store_true')
    a = ap.parse_args()

    d = leer()
    if a.usar:
        d['version_activa'] = a.usar
        d['cambiado'] = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        escribir(d)
        print(f"ACTIVA: {a.usar} — {VERSIONES[a.usar]['descripcion']}")
        print("El journal NO se modifica. Las operaciones nuevas llevan config_version.")
    else:
        v = d['version_activa']
        print(f"CONFIGURACIÓN ACTIVA: {v}")
        print(f"  {VERSIONES[v]['descripcion']}")
        print(f"  E={VERSIONES[v]['esperanza_R']:+.3f}R DD={VERSIONES[v]['dd_R']:.1f}R "
              f"señales/mes={VERSIONES[v]['por_mes']}")
        if JOURNAL.exists():
            j = json.loads(JOURNAL.read_text())
            print(f"  journal: {len(j.get('operaciones') or [])} ops · "
                  f"forward {j.get('resumen', {}).get('forward_n', 0)}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
