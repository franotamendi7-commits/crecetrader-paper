"""Modelo de escenario del YouTube Analyst (contrato v1.0)."""

PAPER_ONLY = True   # no ejecuta; solo describe/clasifica
from __future__ import annotations

from dataclasses import dataclass, field

CLASIFICACIONES = ('NIVEL_REFERENCIADO', 'ZONA_DE_INTERES', 'ESCENARIO_CONDICIONAL',
                   'PLAN_OPERATIVO', 'OPORTUNIDAD_VALIDABLE', 'NO_OPERABLE',
                   'DESCARTADO', 'INDETERMINADO')
VEREDICTOS = ('APTO_PARA_EVALUACION', 'ESPERAR_CONFIRMACION', 'FALTA_INFORMACION',
              'RIESGO_INADECUADO', 'NO_OPERABLE', 'ESCENARIO_INVALIDADO')
SEGUIMIENTO = ('EN_OBSERVACION', 'ESPERANDO_ACTIVACION', 'ACTIVADO', 'EN_SEGUIMIENTO',
               'OBJETIVO_ALCANZADO', 'INVALIDADO', 'EXPIRADO')
PROCEDENCIAS = ('A', 'B', 'C', 'D')


def campo(valor, procedencia=None, **extra):
    d = {'valor': valor, 'procedencia': procedencia}
    d.update(extra)
    return d


@dataclass
class Escenario:
    id: str
    video_id: str
    instrumento: str
    timestamp_explicacion: str = ''
    temporalidades: list = field(default_factory=list)
    direccion: str = 'neutral'
    nivel: dict = field(default_factory=dict)
    justificacion: str = ''
    evidencia: list = field(default_factory=list)
    relacion_temporalidades: str = ''
    condicion_activacion: dict = field(default_factory=dict)
    entrada: dict = field(default_factory=dict)
    stop: dict = field(default_factory=dict)
    objetivos: list = field(default_factory=list)
    risk_reward: dict = field(default_factory=dict)
    clasificacion: str = 'INDETERMINADO'
    info_faltante: list = field(default_factory=list)
    confianza: float = 0.0
    calidad_evidencia: str = 'media'
    mercado: str = 'NO_DETERMINADO'
    timestamp_video: str = ''
    fuente: str = 'transcripcion'
    demo: bool = False
    seguimiento: str = 'EN_OBSERVACION'
    veredicto: str = ''
    motivos_manager: list = field(default_factory=list)

    def to_dict(self):
        from dataclasses import asdict
        return asdict(self)
