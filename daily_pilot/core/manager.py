#!/usr/bin/env python3
"""Manager — evalua escenarios del YouTube Analyst (contrato v1.1).

Dimensiones separadas: calidad del analisis, completitud del plan, viabilidad
tecnica y riesgo/gestion de capital. Propone calculos propios (procedencia D).
No convierte escenarios en operaciones.

Devuelve uno de: APTO_PARA_EVALUACION, ESPERAR_CONFIRMACION, FALTA_INFORMACION,
RIESGO_INADECUADO, NO_OPERABLE, ESCENARIO_INVALIDADO.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plan_classifier import clasificar_escenario  # noqa: E402

PAPER_ONLY = True
# C11 (aprobado por Francisco, 2026-11-18): tope duro de riesgo por operacion.
TOPE_RIESGO_PCT = 0.05
VEREDICTOS = ('APTO_PARA_EVALUACION', 'ESPERAR_CONFIRMACION', 'FALTA_INFORMACION',
              'RIESGO_INADECUADO', 'NO_OPERABLE', 'ESCENARIO_INVALIDADO')


class Manager:
    def __init__(self, capital: float = 10000.0, riesgo_pct: float = 0.01,
                 min_rb: float = 1.0, max_exposicion_pct: float = 0.05,
                 stop_method: str = 'por debajo del minimo de la zona de entrada (0.5%)'):
        self.capital = capital
        self.riesgo_pct = riesgo_pct
        self.min_rb = min_rb
        self.max_exposicion_pct = max_exposicion_pct
        self.stop_method = stop_method
        self.confianza = 1.0      # default conservador: se pisa con e['confianza']

    # --- dimensiones --------------------------------------------------
    def _calidad(self, e):
        ev = e.get('evidencia') or []
        cal = e.get('calidad_evidencia') or ('alta' if len(ev) >= 2 else 'media')
        return cal

    def _completitud(self, cls, faltante):
        campos = {'PLAN_OPERATIVO_COMPLETO': [], 'PLAN_OPERATIVO_INCOMPLETO': ['invalidacion'],
                  'ESCENARIO_CONDICIONAL': ['entrada', 'invalidacion', 'objetivos'],
                  'ZONA_DE_INTERES': ['condicion', 'entrada', 'invalidacion', 'objetivos'],
                  'NIVEL_REFERENCIADO': ['condicion', 'entrada', 'invalidacion', 'objetivos']}
        base = campos.get(cls, [])
        return sorted(set(base + list(faltante or [])))

    def _viabilidad(self, entrada, stop, objetivos, direccion):
        """Contradicciones tecnicas. Devuelve lista de contradicciones."""
        c = []
        if entrada is None or stop is None:
            return c
        if direccion == 'alcista' and entrada <= stop:
            c.append('alcista con entrada <= invalidacion')
        if direccion == 'bajista' and entrada >= stop:
            c.append('bajista con entrada >= invalidacion')
        for o in objetivos:
            v = o.get('valor') if isinstance(o, dict) else o
            if direccion == 'alcista' and v is not None and v <= entrada:
                c.append(f'alcista con objetivo {v} <= entrada')
            if direccion == 'bajista' and v is not None and v >= entrada:
                c.append(f'bajista con objetivo {v} >= entrada')
        return c

    def _proponer_stop(self, e, entrada):
        """Propuesta D: 0.5% por debajo (alcista) o encima (bajista) de la entrada."""
        if entrada is None:
            return None
        delta = abs(entrada) * 0.005
        direccion = e.get('direccion')
        valor = round(entrada + delta if direccion == 'bajista' else entrada - delta, 4)
        return {'valor': valor, 'procedencia': 'D', 'metodo': self.stop_method}

    def evaluar(self, escenario: dict) -> dict:
        # P0 FIX: acepta el wrapper {'escenario': {...}} o el dict plano.
        e = escenario.get('escenario') or escenario
        ev = escenario.get('evaluacion') or {}
        cl = clasificar_escenario(e)
        cls = cl['clasificacion']
        faltante = cl['info_faltante']
        motivos = []
        rb = (e.get('risk_reward') or {}).get('valor') or (ev.get('risk_reward') or {}).get('valor')
        stop = (e.get('stop') or {}).get('valor')
        entrada = (e.get('entrada') or {}).get('valor')
        direccion = e.get('direccion', 'neutral')
        objetivos = e.get('objetivos', [])

        # invalidez declarada por el seguimiento
        if (escenario.get('seguimiento') or e.get('seguimiento')) in ('INVALIDADO', 'EXPIRADO'):
            cls = 'DESCARTADO'
            faltante = []

        contradicciones = self._viabilidad(entrada, stop, objetivos, direccion)
        propuesta_stop = None
        if cls in ('PLAN_OPERATIVO_INCOMPLETO', 'ESCENARIO_CONDICIONAL') and stop is None and entrada is not None:
            propuesta_stop = self._proponer_stop(e, entrada)

        # P0 FIX: R:R se calcula si hay entrada y un stop (del Analyst o propuesto).
        if rb is None and entrada is not None:
            stop_efectivo = stop if stop is not None else (propuesta_stop or {}).get('valor')
            if stop_efectivo is not None:
                rb = self._calcular_rb(entrada, stop_efectivo, objetivos)
                if rb is not None:
                    motivos.append(f'R/B {rb} con stop '
                                   f'{"del analista" if stop is not None else "propuesto"}')

        # veredicto
        if cls == 'DESCARTADO':
            veredicto = 'ESCENARIO_INVALIDADO'
            motivos.append('escenario invalidado por la evolucion del precio')
        elif contradicciones:
            veredicto = 'NO_OPERABLE'
            motivos += contradicciones
        elif cls == 'NO_OPERABLE':
            veredicto = 'NO_OPERABLE'
            motivos.append('escenario no operable')
        elif cls == 'INDETERMINADO':
            veredicto = 'FALTA_INFORMACION'
            motivos += faltante or ['informacion insuficiente']
        elif cls in ('NIVEL_REFERENCIADO', 'ZONA_DE_INTERES'):
            veredicto = 'FALTA_INFORMACION'
            motivos.append(f'{cls}: no es un plan operativo')
        elif cls == 'ESCENARIO_CONDICIONAL':
            veredicto = 'ESPERAR_CONFIRMACION'
            motivos.append('plan condicionado; falta entrada/invalidacion/objetivos')
        elif cls == 'PLAN_OPERATIVO_INCOMPLETO':
            veredicto = 'ESPERAR_CONFIRMACION'
            motivos.append('plan incompleto; se propone invalidacion (D)')
        elif cls in ('PLAN_OPERATIVO_COMPLETO', 'OPORTUNIDAD_VALIDABLE'):
            if rb is not None and rb < self.min_rb:
                veredicto = 'RIESGO_INADECUADO'
                motivos.append(f'R/B {rb} < {self.min_rb}')
            else:
                veredicto = 'APTO_PARA_EVALUACION'
                motivos.append('condicion, entrada, invalidacion y objetivos presentes')
        else:
            veredicto = 'FALTA_INFORMACION'

        if propuesta_stop:
            motivos.append(f"propuesta de invalidacion (D): {propuesta_stop['valor']} — "
                           f"metodo: {propuesta_stop['metodo']}")

        # que se necesita para habilitar la evaluacion
        que_necesita = self._completitud(cls, faltante) if veredicto != 'APTO_PARA_EVALUACION' else []

        capital = self._capital(entrada, stop if stop is not None else (propuesta_stop or {}).get('valor'),
                                objetivos, e.get('confianza'))
        return {
            'escenario_id': e.get('id') or escenario.get('id'),
            'clasificacion': cls,
            'dimensiones': {
                'calidad_analisis': self._calidad(e),
                'completitud_plan': 'completo' if cls == 'PLAN_OPERATIVO_COMPLETO' else 'incompleto',
                'viabilidad_tecnica': 'con contradicciones' if contradicciones else 'sin contradicciones',
                'riesgo_y_capital': {'risk_reward': rb, 'veredicto': veredicto},
            },
            'veredicto': veredicto,
            'motivos': motivos,
            'condiciones_faltantes': faltante,
            'que_se_necesita': que_necesita,
            'propuesta_stop': propuesta_stop,
            'risk_reward': rb,
            'capital': capital,
            'paper_only': PAPER_ONLY,
            'decision_usuario': 'pendiente',
        }

    def _calcular_rb(self, entrada, stop, objetivos):
        try:
            riesgo = abs(entrada - stop)
            if riesgo <= 0 or not objetivos:
                return None
            beneficio = abs(objetivos[0].get('valor', objetivos[0]) - entrada)
            return round(beneficio / riesgo, 2)
        except Exception:
            return None

    def _capital(self, entrada, stop, objetivos, confianza=None):
        # P1-4 FIX: sin stop no hay riesgo medible; no usar la entrada como riesgo.
        if entrada is None or stop is None:
            return {'disponible': self.capital, 'riesgo_pct': self.riesgo_pct,
                    'tamano_propuesto': None, 'perdida_potencial': None,
                    'exposicion_maxima': round(self.capital * self.max_exposicion_pct, 2)}
        riesgo = abs(entrada - stop)
        size = perdida = None
        # C11 (H-07): riesgo = confianza x tope, con tope duro del 5%.
        conf = float(confianza if confianza is not None else getattr(self, 'confianza', 1.0))
        conf = min(max(conf, 0.0), 1.0)
        riesgo_pct = round(conf * TOPE_RIESGO_PCT, 4)
        if riesgo > 0:
            perdida = round(self.capital * riesgo_pct, 2)
            size = round(perdida / riesgo, 6)
            # H-02 FIX: exposicion_maxima es NOTIONAL máximo (no pérdida).
            max_notional = round(self.capital * self.max_exposicion_pct, 2)
            tope = max_notional / entrada
            if size > tope:
                size = round(tope, 6)
                perdida = round(size * riesgo, 2)
        return {'disponible': self.capital, 'riesgo_pct': riesgo_pct,
                'tamano_propuesto': size, 'perdida_potencial': perdida,
                'exposicion_maxima': round(self.capital * self.max_exposicion_pct, 2),
                'exposicion_maxima_tipo': 'notional'}

    def evaluar_lista(self, escenarios: list) -> list:
        return [self.evaluar(e) for e in escenarios]


def cargar_escenarios(path: str) -> list:
    d = json.load(open(path))
    return d.get('escenarios', d if isinstance(d, list) else [])
