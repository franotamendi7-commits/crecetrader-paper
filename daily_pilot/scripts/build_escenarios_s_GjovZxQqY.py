#!/usr/bin/env python3
"""Construye escenarios reales del video s_GjovZxQqY y los evalua con el Manager.

Procedencias: A = dicho por CreceTrader. Sin inferencia propia ni datos de grafico.
"""
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / 'daily_pilot'))
from core.manager import Manager  # noqa: E402

ESC = [
    dict(id='ESC-sG-01-weekly', instrumento='BTCUSD', timestamp_explicacion='06:26',
         temporalidades=['Weekly', 'Daily'], direccion='alcista',
         nivel={'valor': 71509, 'procedencia': 'A'},
         justificacion='precios objetivos de largo plazo; soporte 69.000',
         evidencia=['transcripcion 00:59-01:05', '06:26-07:01'],
         condicion_activacion={'valor': 'recuperacion hacia 69.000', 'procedencia': 'A'},
         entrada={'valor': 69000, 'procedencia': 'A'},
         objetivos=[{'valor': 71509, 'procedencia': 'A'}, {'valor': 72554, 'procedencia': 'A'},
                    {'valor': 75518, 'procedencia': 'A'}],
         info_faltante=['stop no declarado']),
    dict(id='ESC-sG-02-4h', instrumento='BTCUSD', timestamp_explicacion='12:48',
         temporalidades=['4H'], direccion='bajista',
         nivel={'valor': 56750, 'procedencia': 'A'},
         justificacion='maximos y minimos decrecientes; sin reversión en 4H el precio puede seguir cayendo',
         evidencia=['transcripcion 12:48-12:57'],
         condicion_activacion={'valor': 'que no haya reversal en 4H', 'procedencia': 'A'},
         entrada={'valor': None, 'procedencia': None},
         objetivos=[{'valor': 56750, 'procedencia': 'A'}],
         info_faltante=['entrada no declarada', 'stop no declarado']),
    dict(id='ESC-sG-03-intradia', instrumento='BTCUSD', timestamp_explicacion='14:47',
         temporalidades=['Intradia'], direccion='neutral',
         nivel={'valor': 66617, 'procedencia': 'A'},
         justificacion='horquilla intradia entre 66.617 y 64.004; partida 65.310',
         evidencia=['transcripcion 13:49-14:58'],
         entrada={'valor': 66617, 'procedencia': 'A'},
         objetivos=[{'valor': 64004, 'procedencia': 'A'}],
         info_faltante=['stop no declarado', 'condicion de activacion no explicita']),
    dict(id='ESC-sG-04-vigilar', instrumento='BTCUSD', timestamp_explicacion='02:01',
         temporalidades=['4H'], direccion='neutral',
         nivel={'valor': 65520, 'procedencia': 'A'},
         justificacion='habia que vigilar el precio en 65.520; tambien en futuros CME',
         evidencia=['transcripcion 02:01-03:11', '10:48-11:21'],
         info_faltante=['condicion de activacion', 'entrada', 'stop']),
    dict(id='ESC-sG-05-eth', instrumento='ETHUSD', timestamp_explicacion='16:49',
         temporalidades=['Daily'], direccion='alcista',
         nivel={'valor': 1780, 'procedencia': 'A'},
         justificacion='1.780 sirve de freno; zona de compra 1.890-2.286',
         evidencia=['transcripcion 16:49-17:14'],
         condicion_activacion={'valor': 'si 1.780 junto con 1.890 hace que haya reversal',
                                'procedencia': 'A'},
         entrada={'valor': 1780, 'procedencia': 'A'},
         objetivos=[{'valor': 2025, 'procedencia': 'A'}, {'valor': 2286, 'procedencia': 'A'}],
         info_faltante=['stop no declarado']),
    dict(id='ESC-sG-06-oro', instrumento='XAUUSD', timestamp_explicacion='17:36',
         temporalidades=['Daily'], direccion='bajista',
         nivel={'valor': 3906, 'procedencia': 'A'},
         justificacion='el oro seguira corrigiendo; 3.906 cierra el paso; objetivo 3.623',
         evidencia=['transcripcion 17:36-17:53'],
         condicion_activacion={'valor': 'correccion en curso', 'procedencia': 'A'},
         entrada={'valor': 3906, 'procedencia': 'A'},
         objetivos=[{'valor': 3623, 'procedencia': 'A'}],
         info_faltante=['stop no declarado']),
    dict(id='ESC-sG-07-sp500', instrumento='SPX', timestamp_explicacion='18:16',
         temporalidades=['Daily'], direccion='bajista',
         nivel={'valor': 7592, 'procedencia': 'A'},
         justificacion='SP500 aguanta en 7.592; correccion posible a 6.612',
         evidencia=['transcripcion 18:16-18:38'],
         objetivos=[{'valor': 6612, 'procedencia': 'A'}],
         info_faltante=['condicion de activacion', 'entrada', 'stop']),
    dict(id='ESC-sG-08-nq', instrumento='NQ', timestamp_explicacion='18:43',
         temporalidades=['Daily'], direccion='bajista',
         nivel={'valor': 28026, 'procedencia': 'A'},
         justificacion='Nasdaq 28.026; 28.400 precio vendedor; objetivos 25.479/25.400',
         evidencia=['transcripcion 18:43-19:21'],
         entrada={'valor': 28400, 'procedencia': 'A'},
         objetivos=[{'valor': 25479, 'procedencia': 'A'}, {'valor': 25400, 'procedencia': 'A'},
                    {'valor': 22931, 'procedencia': 'A'}],
         info_faltante=['stop no declarado', 'condicion de activacion no explicita']),
]


def main():
    m = Manager()
    evaluados = []
    for e in ESC:
        v = m.evaluar(e)
        e2 = dict(e)
        e2['video_id'] = 's_GjovZxQqY'
        e2['fuente'] = 'transcripcion'
        e2['temporalidad_origen'] = (e.get('temporalidades') or ['NO_DETERMINADO'])[0]
        e2['metodo_calculo'] = e.get('metodo_calculo')
        e2['clasificacion'] = v['clasificacion']
        e2['veredicto'] = v['veredicto']
        e2['motivos_manager'] = v['motivos']
        e2['demo'] = False
        evaluados.append({'escenario': e2, 'evaluacion': v})
    out = BASE / 'daily_pilot' / 'datos' / 'escenarios_s_GjovZxQqY.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({'video_id': 's_GjovZxQqY', 'escenarios': evaluados},
                              ensure_ascii=False, indent=2))
    for x in evaluados:
        print(f"{x['escenario']['id']:18} {x['escenario']['clasificacion']:22} "
              f"{x['evaluacion']['veredicto']:24} faltante={x['escenario']['info_faltante']}")
    print('salida:', out)


if __name__ == '__main__':
    main()
