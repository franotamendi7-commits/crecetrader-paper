#!/usr/bin/env python3
"""Risk Manager — componente aislado del YouTube Analyst.

PAPER_ONLY=true. Ninguna ejecucion automatica. Ninguna conexion con permisos
de trading. No envia ordenes. Solo valida y cuantifica riesgo de senales.

Interfaz:
    rm = RiskManager(account_balance=10000.0, max_risk_pct=0.01, max_exposure=0.05)
    res = rm.evaluar(signals)   # lista de dicts
    # res: {'decision': 'ACEPTAR'|'RECHAZAR'|'REVISION MANUAL',
    #       'razones': [...], 'senales': [{'id':..., 'decision':..., 'razones':..., 'risk': {...}}]}
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

PAPER_ONLY = True

# C11 (aprobado por Francisco, 2026-11-18): el riesgo por operacion depende de la
# confiabilidad del escenario y del TIPO DE OPERACION (C01), con TOPE duro del 5%.
#   long       -> 5% del total, distribuido en 2-3 entradas (1.667-2.5% por entrada)
#   correccion -> 1-2% por operacion
TOPE_RIESGO_PCT = 0.05

DIRECCIONES = {'compra', 'venta', 'sin_operacion'}

# Tipos que el Manager cuantifica (tienen direccion y niveles).
# SIN_OPERACION / NIVEL_MENCIONADO / NO_DETERMINABLE no se cuantifican.
TIPOS_EVALUABLES = ('ZONA_DE_INTERES', 'ESCENARIO_CONDICIONAL', 'SENAL_EXPLICITA')

# Nivel de cada tipo para el tablero: informativo | escenario | candidata | no_operable
NIVEL_POR_TIPO = {
    'NIVEL_MENCIONADO': 'nivel_informativo',
    'ZONA_DE_INTERES': 'escenario',
    'ESCENARIO_CONDICIONAL': 'escenario',
    'SENAL_EXPLICITA': 'candidata',
    'SIN_OPERACION': 'no_operable',
    'NO_DETERMINABLE': 'no_operable',
}


@dataclass
class Config:
    account_balance: float = 10000.0
    max_risk_pct: float = 0.01        # max riesgo por operacion (fraccion del capital)
    max_exposure_pct: float = 0.05    # max exposicion agregada
    max_senales_por_instrumento: int = 2
    min_confianza: float = 0.5
    requerir_evidencia: bool = True
    tipos_evaluables: tuple = TIPOS_EVALUABLES
    # C01 (Francisco): la tendencia la determina el semanal.
    riesgo_correccion_pct: float = 0.02   # correccion: 1-2%
    riesgo_long_pct: float = 0.05        # long: 5% total
    entradas_long: int = 2               # long: distribuido en 2-3 entradas


@dataclass
class Signal:
    id: str
    instrument: str = ''
    direction: str = ''
    entry_low: float | None = None
    entry_high: float | None = None
    invalidation: float | None = None
    targets: list = field(default_factory=list)
    evidence: list = field(default_factory=list)
    confidence: float = 0.0
    status: str = 'EXPERIMENTAL'
    tipo: str = 'SENAL_EXPLICITA'   # SENAL_EXPLICITA unica candidata operativa
    tipo_operacion: str = 'long'   # C01: 'long' (a favor del semanal) | 'correccion' (contra el diario)

    @property
    def entry(self):
        if self.entry_low is None:
            return None
        if self.entry_high in (None, self.entry_low):
            return self.entry_low
        return (self.entry_low + self.entry_high) / 2


class RiskManager:
    def __init__(self, config: Config | None = None):
        self.cfg = config or Config()
        self.history: list = []

    # --- validaciones -------------------------------------------------
    def _completitud(self, s: Signal):
        falta = []
        if not s.instrument:
            falta.append('instrumento ausente')
        if s.direction not in DIRECCIONES:
            falta.append(f'direccion invalida: {s.direction!r}')
        if s.direction != 'sin_operacion' and s.entry is None:
            falta.append('zona de entrada ausente')
        if s.direction != 'sin_operacion' and s.invalidation is None:
            falta.append('invalidacion ausente')
        if s.direction != 'sin_operacion' and isinstance(s.invalidation, (int, float)) and s.invalidation <= 0:
            falta.append(f'invalidacion invalida: {s.invalidation!r} (debe ser > 0)')
        if s.direction != 'sin_operacion' and isinstance(s.entry, (int, float)) and s.entry <= 0:
            falta.append(f'entrada invalida: {s.entry!r} (debe ser > 0)')
        if s.direction != 'sin_operacion' and not s.targets:
            falta.append('objetivos ausentes')
        if s.direction != 'sin_operacion' and any(
                (not isinstance(t, (int, float)) or t <= 0) for t in s.targets):
            falta.append('objetivos invalidos (<=0 o no numericos)')
        if self.cfg.requerir_evidencia and not s.evidence:
            falta.append('evidencia ausente')
        return falta

    def _contradicciones(self, s: Signal):
        r = []
        if s.direction == 'compra':
            if s.entry is not None and s.invalidation is not None and s.entry <= s.invalidation:
                r.append('compra: entrada <= invalidacion')
            for t in s.targets:
                if s.entry is not None and t <= s.entry:
                    r.append(f'compra: objetivo {t} <= entrada')
        elif s.direction == 'venta':
            if s.entry is not None and s.invalidation is not None and s.entry >= s.invalidation:
                r.append('venta: entrada >= invalidacion')
            for t in s.targets:
                if s.entry is not None and t >= s.entry:
                    r.append(f'venta: objetivo {t} >= entrada')
        return r

    def _riesgo(self, s: Signal):
        out = {'risk_per_unit': None, 'position_size': None, 'perdida_potencial': None,
               'r_multiples': []}
        if s.direction == 'sin_operacion' or s.entry is None or s.invalidation is None:
            return out
        risk = abs(s.entry - s.invalidation)
        if risk <= 0:
            out['risk_per_unit'] = 0.0
            return out
        conf = s.confidence if isinstance(s.confidence, (int, float)) else 0.0
        # C01/C11: el riesgo depende del TIPO DE OPERACION y de la confianza.
        if s.tipo_operacion == 'correccion':
            tope = self.cfg.riesgo_correccion_pct          # 1-2%
        else:
            tope = min(self.cfg.riesgo_long_pct / max(self.cfg.entradas_long, 1), TOPE_RIESGO_PCT)
        riesgo_pct = round(min(max(conf, 0.0), tope), 4)
        risk_money = self.cfg.account_balance * riesgo_pct
        size = risk_money / risk
        out['riesgo_pct_efectivo'] = riesgo_pct
        out['riesgo_pct_tope'] = tope
        out['tipo_operacion'] = s.tipo_operacion
        if s.tipo_operacion == 'long':
            out['riesgo_total_long'] = self.cfg.riesgo_long_pct
            out['entradas_long'] = self.cfg.entradas_long
        out['risk_per_unit'] = round(risk, 4)
        out['position_size'] = round(size, 6)
        out['perdida_potencial'] = round(size * risk, 2)
        for t in s.targets:
            out['r_multiples'].append(round((t - s.entry) / risk * (1 if s.direction == 'compra' else -1), 2))
        return out

    # --- evaluacion ---------------------------------------------------
    def evaluar(self, signals: list):
        razones_globales = []
        resultados = []
        instrumentos = {}
        exposicion = 0.0
        for raw in signals:
            es_dict = isinstance(raw, dict)
            s = raw if isinstance(raw, Signal) else Signal(**raw)
            if es_dict and 'tipo' not in raw:
                try:
                    from importlib import import_module
                    cl = import_module('signal_classifier')
                    s.tipo = cl.clasificar({'nivel': s.instrument,
                                            'texto': ' '.join(s.evidence or [])}).get('tipo', 'SENAL_EXPLICITA')
                except Exception:
                    pass
            if s.tipo not in self.cfg.tipos_evaluables:
                resultados.append({'id': s.id, 'instrument': s.instrument, 'direction': s.direction,
                                   'tipo': s.tipo, 'nivel': NIVEL_POR_TIPO.get(s.tipo, 'no_operable'),
                                   'decision': 'NO_EVALUABLE',
                                   'razones': [f'tipo {s.tipo}: no es candidata operativa'],
                                   'risk': {}, 'paper_only': PAPER_ONLY})
                continue
            falta = self._completitud(s)
            contra = self._contradicciones(s)
            riesgo = self._riesgo(s)
            razones = list(falta) + list(contra)
            decision = 'ACEPTAR'
            if falta:
                decision = 'RECHAZAR'
            elif contra:
                decision = 'RECHAZAR'
            elif s.confidence < self.cfg.min_confianza:
                decision = 'REVISION MANUAL'
                razones.append(f'confianza {s.confidence} < {self.cfg.min_confianza}')
            if s.direction != 'sin_operacion':
                instrumentos[s.instrument] = instrumentos.get(s.instrument, 0) + 1
                if instrumentos[s.instrument] > self.cfg.max_senales_por_instrumento:
                    decision = 'REVISION MANUAL'
                    razones.append(f'exceso de senales para {s.instrument}')
                if riesgo['perdida_potencial']:
                    exposicion += riesgo['perdida_potencial']
            resultados.append({'id': s.id, 'instrument': s.instrument, 'direction': s.direction,
                               'nivel': NIVEL_POR_TIPO.get(s.tipo, 'no_operable'),
                               'decision': decision, 'razones': razones, 'risk': riesgo,
                               'paper_only': PAPER_ONLY})
        if exposicion > self.cfg.account_balance * self.cfg.max_exposure_pct:
            razones_globales.append(
                f'exposicion {exposicion:.2f} > limite {self.cfg.account_balance * self.cfg.max_exposure_pct:.2f}')
            for r in resultados:
                if r['decision'] == 'ACEPTAR':
                    r['decision'] = 'REVISION MANUAL'
        decision_global = 'ACEPTAR'
        evaluables = [r for r in resultados if r['decision'] != 'NO_EVALUABLE']
        if any(r['decision'] == 'RECHAZAR' for r in evaluables):
            decision_global = 'RECHAZAR'
        elif any(r['decision'] == 'REVISION MANUAL' for r in evaluables):
            decision_global = 'REVISION MANUAL'
        if not evaluables:
            decision_global = 'REVISION MANUAL'
            razones_globales.append('no hay senales candidatas operativas (SENAL_EXPLICITA)')
        salida = {'paper_only': PAPER_ONLY, 'decision': decision_global,
                  'razones': razones_globales, 'exposicion_total': round(exposicion, 2),
                  # P0 FIX: 'exposicion_total' sumaba perdida_potencial, no exposicion.
                  'perdida_potencial_total': round(exposicion, 2),
                  'por_nivel': {n: sum(1 for r in resultados if r.get('nivel') == n)
                                for n in ('nivel_informativo', 'escenario', 'candidata', 'no_operable')},
                  'senales': resultados}
        self.history.append(salida)
        return salida


def evaluar_json(path: str) -> dict:
    data = json.load(open(path))
    rm = RiskManager(Config(**data.get('config', {})))
    return rm.evaluar(data.get('senales', []))
