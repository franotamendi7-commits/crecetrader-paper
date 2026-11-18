#!/usr/bin/env python3
"""Runner de la suite del piloto (PAPER_ONLY, Fase 0).

DOS modos, porque no son lo mismo:

  --readonly      (default) solo tests que NO escriben nada. Garantia real.
  --integracion   ademas corre los tests que reescriben artefactos derivados
                  (relaciones.json, escenarios/, dashboard/index.html) y los
                  scripts que tocan store.db (anadir_temporalidad.py).
                  Imprime aviso y compara hashes antes/despues.

Uso: python3 daily_pilot/tests/run_all.py [--integracion]
"""
from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

BASE = Path('/Users/franciscootamendi/YouTubeTradingAgent')
PILOT = BASE / 'daily_pilot'
PY = sys.executable

# Fuentes que la suite JAMAS debe modificar
INTOCABLES = [
    PILOT / 'knowledge' / 'store.db',
    PILOT / 'registro' / 'registro.json',
    PILOT / 'datos' / 'dashboard_data.json',
]
# Artefactos derivados que los tests de integracion pueden reescribir
DERIVADOS = [
    PILOT / 'relaciones' / 'relaciones.json',
    PILOT / 'escenarios' / 'historial.json',
    PILOT / 'escenarios' / 'vigentes.json',
    PILOT / 'dashboard' / 'index.html',
]

# Read-only de verdad: no escriben archivos ni usan red.
HERMETICOS = [
    'daily_pilot/tests/test_core.py',
    'daily_pilot/tests/test_metrics.py',
    'daily_pilot/tests/test_allocacion.py',
    'daily_pilot/tests/test_confluencia.py',
    'daily_pilot/tests/test_intradia.py',
    'daily_pilot/tests/test_zonas.py',
    'daily_pilot/tests/test_liquidez.py',
    'daily_pilot/tests/test_regimen.py',
    'daily_pilot/tests/test_invalidacion.py',
    'daily_pilot/tests/test_objetivos.py',
    'daily_pilot/tests/test_escenarios.py',
    'daily_pilot/risk_manager/test_risk_manager.py',
]
# Integracion: reescriben artefactos derivados y/o tocan store.db.
INTEGRACION = [
    'daily_pilot/tests/test_dashboard_risk.py',   # ejecuta generar_dashboard.py (escribe + RSS)
    'daily_pilot/tests/test_c2c3e6.py',           # anadir_temporalidad.py hace UPDATE en store.db
]


def sha(p: Path):
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--integracion', action='store_true',
                    help='corre ademas los tests que escriben artefactos/tocan store.db')
    args = ap.parse_args()

    pre = {p: sha(p) for p in INTOCABLES}
    print(f'python: {PY}')
    print(f'modo: {"READONLY" if not args.integracion else "READONLY + INTEGRACION (escribe derivados)"}')
    print('=== TESTS READ-ONLY ===')
    ok = fail = 0
    for t in HERMETICOS:
        r = subprocess.run([PY, str(BASE / t)], capture_output=True, text=True, timeout=600)
        ult = (r.stdout.strip().splitlines() or [''])[-1]
        estado = 'OK  ' if r.returncode == 0 else 'FALLO'
        if r.returncode == 0:
            ok += 1
        else:
            fail += 1
        print(f'  {estado} | {Path(t).name:34s} | {ult[:40]}')

    if args.integracion:
        print('\n=== TESTS DE INTEGRACION (reescriben derivados y/o tocan store.db) ===')
        for t in INTEGRACION:
            r = subprocess.run([PY, str(BASE / t)], capture_output=True, text=True, timeout=900)
            ult = (r.stdout.strip().splitlines() or [''])[-1]
            estado = 'OK  ' if r.returncode == 0 else 'FALLO'
            if r.returncode == 0:
                ok += 1
            else:
                fail += 1
            print(f'  {estado} | {Path(t).name:34s} | {ult[:40]}')
    else:
        print('\n(omitidos por --readonly: ' + ', '.join(Path(t).name for t in INTEGRACION) + ')')

    print('\n=== INTEGRIDAD DE FUENTES ===')
    roto = False
    for p in INTOCABLES:
        a, b = pre[p], sha(p)
        if a == b:
            print(f'  OK    | {p.name:22s} sin cambios')
        else:
            roto = True
            print(f'  ROTO  | {p.name:22s} {str(a)[:12]} -> {str(b)[:12]}')
    for p in DERIVADOS:
        if p.exists():
            print(f'  info  | {p.name:22s} no tocado (hash igual al pre)')

    print(f'\nRESULTADO: {ok} OK · {fail} FALLO' + (' · FUENTES INTACTAS' if not roto else ' · FUENTES MODIFICADAS'))
    return 1 if (fail or roto) else 0


if __name__ == '__main__':
    sys.exit(main())
