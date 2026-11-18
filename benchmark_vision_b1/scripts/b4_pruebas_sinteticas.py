#!/usr/bin/env python3
"""B4 — Pruebas sinteticas del comparador. NO llama a ningun modelo."""
import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path

COMP = Path(__file__).parent / 'b4_comparar.py'
TMP = Path(tempfile.mkdtemp(prefix='b4_tests_'))
COLS = ['frame_id', 'video_id', 'frame', 'idx', 'pts_time', 'instrument', 'exchange',
        'timeframe', 'price_labels', 'horizontal_levels', 'trendlines',
        'market_structure', 'liquidity_zones', 'indicators', 'candlestick_info',
        'unreadable_information', 'abstentions', 'confidence',
        'legibility_instrument', 'legibility_timeframe', 'legibility_prices',
        'legibility_horizontal_levels', 'legibility_trendlines',
        'legibility_indicators', 'legibility_structure', 'legibility_liquidity', 'notes']


def fila(**kw):
    d = {c: '' for c in COLS}
    d.update({k: str(v) for k, v in kw.items()})
    return ','.join(d[c] for c in COLS)


def ref_csv(filas):
    p = TMP / 'ref.csv'
    with open(p, 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(COLS)
        for f in filas:
            w.writerow(f.split(','))
    return p


def ref_csv_bruto(lineas):
    p = TMP / 'ref_bruto.csv'
    p.write_text(','.join(COLS) + '\n' + '\n'.join(lineas) + '\n')
    return p


def mod_json(respuestas):
    p = TMP / 'modelo.json'
    p.write_text(json.dumps(respuestas, ensure_ascii=False))
    return p


def correr(ref, mod, ref2=None):
    cmd = [sys.executable, str(COMP), '--modelo', str(mod), '--referencia', str(ref)]
    if ref2:
        cmd += ['--referencia2', str(ref2)]
    return subprocess.run(cmd, capture_output=True, text=True)


def resp(inst='BTCUSD', tf='Daily', prices=None, ind=None, struct='range',
         horiz='', trend='', liq=''):
    return {'instrument': inst, 'timeframe': tf, 'market_structure': struct,
            'visible_price_labels': [{'value': str(v)} for v in (prices or [])],
            'indicators': ind or [],
            'horizontal_levels': [x for x in horiz.split(';') if x],
            'trendlines': [x for x in trend.split(';') if x],
            'liquidity_zones': [x for x in liq.split(';') if x]}


RESULTADOS = []


def caso(nombre, condicion, detalle):
    RESULTADOS.append((nombre, bool(condicion), detalle))
    print(('OK   ' if condicion else 'FALLO') + f' | {nombre} | {detalle}')


def m(salida, nombre):
    for x in salida['metricas']:
        if x['metrica'] == nombre:
            return x
    raise KeyError(nombre)


BASE = dict(frame_id='LFH__f1', video_id='x', frame='frame_1.jpg', idx=1, pts_time=0.0,
            instrument='BTCUSD', exchange='Coinbase', timeframe='Daily',
            price_labels='87496;83833', market_structure='range',
            indicators='MA;Fibonacci', confidence=4,
            legibility_instrument=1, legibility_timeframe=1, legibility_prices=1,
            legibility_horizontal_levels=1, legibility_trendlines=1,
            legibility_indicators=1, legibility_structure=1, legibility_liquidity=4)


def main():
    ref = ref_csv([fila(**BASE)])

    # 1
    mod = mod_json([{'frame': 'frame_1.jpg', 'respuesta_cruda': json.dumps(resp(prices=[87496, 83833], ind=['MA', 'Fibonacci']))}])
    r = correr(ref, mod); s = json.loads(r.stdout)
    caso('coincidencia_exacta', r.returncode == 0 and m(s, 'instrument_accuracy')['resultado'] == 100.0
         and m(s, 'prices_recall')['resultado'] == 100.0, f"rc={r.returncode}")

    # 2
    mod = mod_json([{'frame': 'frame_1.jpg', 'respuesta_cruda': json.dumps(resp(prices=[87496]))}])
    s = json.loads(correr(ref, mod).stdout)
    caso('precio_omitido', m(s, 'prices_recall')['resultado'] == 50.0
         and m(s, 'prices_precision')['resultado'] == 100.0,
         f"recall={m(s,'prices_recall')['resultado']} precision={m(s,'prices_precision')['resultado']}")

    # 3
    mod = mod_json([{'frame': 'frame_1.jpg', 'respuesta_cruda': json.dumps(resp(prices=[87496, 99999]))}])
    s = json.loads(correr(ref, mod).stdout)
    al = s['alucinaciones']['pendientes_de_verificacion_visual']
    caso('precio_inventado', m(s, 'prices_precision')['resultado'] == 50.0
         and m(s, 'posibles_alucinaciones_precios')['numerador'] == 1
         and len(al) == 1 and al[0]['estado'] == 'pendiente_de_verificacion_visual',
         f"precision={m(s,'prices_precision')['resultado']} aluc={al}")

    # 4
    b4 = dict(BASE); b4['price_labels'] = 'NO LEGIBLE'; b4['legibility_prices'] = 3
    ref_ileg = ref_csv([fila(**b4)])
    mod = mod_json([{'frame': 'frame_1.jpg', 'respuesta_cruda': json.dumps(resp(prices=[87496]))}])
    s = json.loads(correr(ref_ileg, mod).stdout)
    caso('precio_ilegible_referencia', m(s, 'prices_recall')['denominador'] == 0
         and m(s, 'prices_recall')['resultado'] is None, f"den={m(s,'prices_recall')['denominador']}")

    # 5
    mod = mod_json([{'frame': 'frame_1.jpg', 'respuesta_cruda': json.dumps(resp(inst='ETHUSD', prices=[87496, 83833]))}])
    s = json.loads(correr(ref, mod).stdout)
    caso('instrumento_incorrecto', m(s, 'instrument_accuracy')['resultado'] == 0.0,
         f"acc={m(s,'instrument_accuracy')['resultado']}")

    # 6
    mod = mod_json([{'frame': 'frame_1.jpg', 'respuesta_cruda': json.dumps(resp(tf='4H', prices=[87496, 83833]))}])
    s = json.loads(correr(ref, mod).stdout)
    caso('temporalidad_incorrecta', m(s, 'timeframe_accuracy')['resultado'] == 0.0,
         f"acc={m(s,'timeframe_accuracy')['resultado']}")

    # 7
    mod = mod_json([{'frame': 'frame_1.jpg', 'respuesta_cruda': json.dumps(resp(prices=[87496, 83833], ind=['Volume']))}])
    s = json.loads(correr(ref, mod).stdout)
    caso('indicador_incorrecto', m(s, 'indicators_f1_approx')['resultado'] == 0.0,
         f"f1={m(s,'indicators_f1_approx')['resultado']}")

    # 8
    b8 = dict(BASE); b8['instrument'] = 'NO LEGIBLE'; b8['legibility_instrument'] = 3
    ref_abst = ref_csv([fila(**b8)])
    mod = mod_json([{'frame': 'frame_1.jpg', 'respuesta_cruda': json.dumps(resp(inst='UNKNOWN'))}])
    s = json.loads(correr(ref_abst, mod).stdout)
    caso('abstencion_correcta', m(s, 'abstencion_correcta')['resultado'] == 100.0,
         f"abst={m(s,'abstencion_correcta')['resultado']}")

    # 9
    mod = mod_json([{'frame': 'frame_1.jpg', 'respuesta_cruda': json.dumps(resp(inst='BTCUSD'))}])
    s = json.loads(correr(ref_abst, mod).stdout)
    caso('abstencion_incorrecta', m(s, 'abstencion_correcta')['resultado'] == 0.0,
         f"abst={m(s,'abstencion_correcta')['resultado']}")

    # 10
    b10 = dict(BASE); b10['price_labels'] = '87496,83833'
    ref_mal = ref_csv([fila(**b10)])
    r = correr(ref_mal, mod)
    caso('formato_csv_invalido', r.returncode == 2 and 'ERRORES DE FORMATO' in r.stderr, f"rc={r.returncode}")

    # 11
    b11 = dict(BASE); b11['instrument'] = ''
    ref_vac = ref_csv([fila(**b11)])
    mod = mod_json([{'frame': 'frame_1.jpg', 'respuesta_cruda': json.dumps(resp())}])
    s = json.loads(correr(ref_vac, mod).stdout)
    caso('campos_vacios', m(s, 'instrument_accuracy')['denominador'] == 0,
         f"den={m(s,'instrument_accuracy')['denominador']}")

    # 12
    mod = mod_json([{'frame': 'frame_1.jpg', 'respuesta_cruda': json.dumps(resp(prices=[87496, 87496, 83833]))}])
    s = json.loads(correr(ref, mod).stdout)
    caso('datos_duplicados', m(s, 'prices_recall')['resultado'] == 100.0
         and m(s, 'prices_precision')['resultado'] == 100.0, 'set() elimina duplicados')

    # 13
    refA = ref_csv([fila(**BASE)])
    refB = ref_csv([fila(**BASE)])
    mod = mod_json([{'frame': 'frame_1.jpg', 'respuesta_cruda': json.dumps(resp())}])
    s = json.loads(correr(refA, mod, refB).stdout)
    caso('acuerdo_entre_anotadores', s['acuerdo_entre_anotadores']['tasa_acuerdo'] == 100.0,
         f"tasa={s['acuerdo_entre_anotadores']['tasa_acuerdo']}")

    fallos = [x for x in RESULTADOS if not x[1]]
    print(f"\n{len(RESULTADOS) - len(fallos)}/{len(RESULTADOS)} pruebas OK")
    print('scratch:', TMP)
    return 1 if fallos else 0


if __name__ == '__main__':
    sys.exit(main())
