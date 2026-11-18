#!/usr/bin/env python3
"""B4 — Comparador completo (v2). NO conectado a produccion.

Metricas con numerador/denominador/excluidos. Valida el formato de entrada.
Una alucinacion NO se declara automaticamente: se marca como
`pendiente_de_verificacion_visual` (requiere comprobar la imagen).
"""
import argparse
import csv
import json
import re
import sys

COLS_REQUERIDAS = ['frame_id', 'frame', 'instrument', 'timeframe',
                   'price_labels', 'horizontal_levels', 'trendlines',
                   'market_structure', 'liquidity_zones', 'indicators',
                   'unreadable_information', 'abstentions']
LEGS = {'legibility_instrument', 'legibility_timeframe', 'legibility_prices',
        'legibility_horizontal_levels', 'legibility_trendlines',
        'legibility_indicators', 'legibility_structure', 'legibility_liquidity'}
NO_VALOR = {'', 'unknown', 'no legible', 'no presente', 'n/a', 'na'}


def norm(v):
    return (v or '').strip().lower()


def lista(v, sep=';'):
    return [x.strip() for x in (v or '').split(sep) if x.strip()]


def extraer_json(txt):
    if not txt:
        return {}
    m = re.search(r'\{.*\}', txt, re.S)
    if not m:
        return {}
    try:
        return json.loads(m.group(0))
    except Exception:
        return {}


def validar_referencia(path):
    errores = []
    with open(path, newline='') as fh:
        rd = csv.reader(fh)
        filas_brutas = list(rd)
    if not filas_brutas:
        return ['referencia vacia'], []
    cols = filas_brutas[0]
    ncols = len(cols)
    faltan = [c for c in COLS_REQUERIDAS if c not in cols]
    if faltan:
        errores.append('columnas faltantes: ' + ','.join(faltan))
    for i, row in enumerate(filas_brutas[1:], start=2):
        if len(row) != ncols:
            errores.append(f'fila {i}: {len(row)} campos, se esperaban {ncols}')
    with open(path, newline='') as fh:
        filas = list(csv.DictReader(fh))
    if not filas:
        errores.append('referencia vacia')
    for i, r in enumerate(filas, start=2):
        for c in cols:
            if c in LEGS:
                v = (r.get(c) or '').strip()
                if v and v not in ('1', '2', '3', '4'):
                    errores.append(f'fila {i}: {c} invalido={v!r}')
        pl = r.get('price_labels') or ''
        if norm(pl) not in NO_VALOR and ';' not in pl and ',' in pl:
            errores.append(f'fila {i}: price_labels con "," (use ";")')
    return errores, filas


def metrica(nombre, num, den):
    return {
        'metrica': nombre,
        'numerador': num,
        'denominador': den,
        'resultado': round(100 * num / den, 2) if den else None,
        'excluidos': 0,
        'no_evaluables': (den - num) if den else 0,
    }


def comparar(modelo, ref, ref2=None):
    m_aci = m_tot = t_aci = t_tot = e_aci = e_tot = 0
    p_mod = p_aci = p_ref = 0
    inv = 0
    h_mod = h_aci = h_ref = 0
    tr_mod = tr_aci = tr_ref = 0
    lz_mod = lz_aci = lz_ref = 0
    ind_mod = ind_aci = ind_ref = 0
    abst_total = abst_ok = 0
    ilegibles = []
    por_frame = []

    for r in modelo:
        fid = norm(r.get('frame'))
        h = extraer_json(r.get('respuesta_cruda', ''))
        g = ref.get(fid)
        row = {'frame': fid}
        if not g:
            row['estado'] = 'sinReferencia'
            por_frame.append(row)
            continue

        for campo, kind in (('instrument', 'i'), ('timeframe', 't'), ('market_structure', 'e')):
            mv, gv = norm(h.get(campo)), norm(g.get(campo))
            if gv in NO_VALOR:
                row[campo] = 'no_evaluable'
                continue
            ok = (mv == gv)
            if kind == 'i':
                m_tot += 1; m_aci += int(ok)
            elif kind == 't':
                t_tot += 1; t_aci += int(ok)
            else:
                e_tot += 1; e_aci += int(ok)
            row[campo] = 'ok' if ok else f'error(modelo={mv},ref={gv})'

        gp = {x for x in (norm(v) for v in lista(g.get('price_labels'))) if x not in NO_VALOR}
        mp = set()
        for p in (h.get('visible_price_labels') or []):
            if isinstance(p, dict):
                v = norm(p.get('value'))
                if v and v not in NO_VALOR:
                    mp.add(v)
        p_ref += len(gp); p_mod += len(mp)
        inter = len(gp & mp); p_aci += inter
        if gp:
            inventados = mp - gp
            inv += len(inventados)
            if inventados:
                ilegibles.append({'frame': fid, 'posibles_inventados': sorted(inventados),
                                  'estado': 'pendiente_de_verificacion_visual'})
        row['precios'] = f'{inter}/{len(gp)} ref, {len(mp)} modelo'

        gh = {x for x in (norm(v) for v in lista(g.get('horizontal_levels'))) if x not in NO_VALOR}
        mh = {x for x in (norm(v) for v in lista(h.get('horizontal_levels'))) if x not in NO_VALOR}
        h_ref += len(gh); h_mod += len(mh); h_aci += len(gh & mh)
        row['horizontales'] = f'{len(gh & mh)}/{len(gh)}'

        gt = {x for x in (norm(v) for v in lista(g.get('trendlines'))) if x not in NO_VALOR}
        mt = {x for x in (norm(v) for v in lista(h.get('trendlines'))) if x not in NO_VALOR}
        tr_ref += len(gt); tr_mod += len(mt); tr_aci += len(gt & mt)
        row['directrices'] = f'{len(gt & mt)}/{len(gt)}'

        gl = {x for x in (norm(v) for v in lista(g.get('liquidity_zones'))) if x not in NO_VALOR}
        ml = {x for x in (norm(v) for v in lista(h.get('liquidity_zones'))) if x not in NO_VALOR}
        lz_ref += len(gl); lz_mod += len(ml); lz_aci += len(gl & ml)
        row['liquidez'] = f'{len(gl & ml)}/{len(gl)}'

        gi = {x for x in (norm(v) for v in lista(g.get('indicators'))) if x not in NO_VALOR}
        mi = {x for x in (norm(v) for v in (h.get('indicators') or [])) if x not in NO_VALOR}
        ind_ref += len(gi); ind_mod += len(mi); ind_aci += len(gi & mi)
        row['indicadores'] = f'{len(gi & mi)}/{len(gi)}'

        ref_no = [k for k in ('instrument', 'timeframe', 'market_structure')
                  if norm(g.get(k)) in ('no legible', 'no presente')]
        for k in ref_no:
            abst_total += 1
            if norm(h.get(k)) in ('unknown', ''):
                abst_ok += 1
        row['abstencion'] = f'{abst_ok}/{abst_total}' if abst_total else '-'
        por_frame.append(row)

    metricas = [
        metrica('instrument_accuracy', m_aci, m_tot),
        metrica('timeframe_accuracy', t_aci, t_tot),
        metrica('market_structure_accuracy', e_aci, e_tot),
        metrica('prices_recall', p_aci, p_ref),
        metrica('prices_precision', p_aci, p_mod),
        metrica('horizontal_levels_recall', h_aci, h_ref),
        metrica('horizontal_levels_precision', h_aci, h_mod),
        metrica('trendlines_recall', tr_aci, tr_ref),
        metrica('trendlines_precision', tr_aci, tr_mod),
        metrica('liquidity_zones_recall', lz_aci, lz_ref),
        metrica('liquidity_zones_precision', lz_aci, lz_mod),
        metrica('indicators_f1_approx', ind_aci * 2, ind_ref + ind_mod),
        metrica('abstencion_correcta', abst_ok, abst_total),
        metrica('posibles_alucinaciones_precios', inv, p_mod),
    ]
    salida = {
        'frames_modelo': len(modelo),
        'frames_con_referencia': sum(1 for x in por_frame if x.get('estado') != 'sinReferencia'),
        'metricas': metricas,
        'alucinaciones': {
            'nota': 'un numero ausente en la referencia NO es automaticamente inventado; '
                    'debe verificarse si esta impreso y legible en la imagen',
            'pendientes_de_verificacion_visual': ilegibles,
        },
        'por_frame': por_frame,
    }
    if ref2 is not None:
        salida['acuerdo_entre_anotadores'] = acuerdo(ref, ref2)
    return salida


def acuerdo(refA, refB):
    comunes = set(refA) & set(refB)
    ag = des = 0
    for fid in comunes:
        for c in ('instrument', 'timeframe', 'market_structure'):
            a, b = norm(refA[fid].get(c)), norm(refB[fid].get(c))
            if a in NO_VALOR or b in NO_VALOR:
                continue
            if a == b:
                ag += 1
            else:
                des += 1
    tot = ag + des
    return {'comunes': len(comunes), 'agreement': ag, 'disagreement': des,
            'tasa_acuerdo': round(100 * ag / tot, 2) if tot else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--modelo', required=True)
    ap.add_argument('--referencia', required=True)
    ap.add_argument('--referencia2', default=None)
    ap.add_argument('--out', default=None)
    a = ap.parse_args()
    errores, filas = validar_referencia(a.referencia)
    if errores:
        print('ERRORES DE FORMATO EN LA REFERENCIA:', file=sys.stderr)
        for e in errores:
            print('  -', e, file=sys.stderr)
        print('NO SE CALCULARON METRICAS (formato invalido).', file=sys.stderr)
        sys.exit(2)
    ref = {norm(r['frame']): r for r in filas}
    ref2 = None
    if a.referencia2:
        er2, f2 = validar_referencia(a.referencia2)
        if er2:
            print('ERRORES EN REFERENCIA2:', er2, file=sys.stderr)
            sys.exit(2)
        ref2 = {norm(r['frame']): r for r in f2}
    modelo = json.load(open(a.modelo))
    salida = comparar(modelo, ref, ref2)
    txt = json.dumps(salida, ensure_ascii=False, indent=2)
    if a.out:
        open(a.out, 'w').write(txt)
    print(txt)


if __name__ == '__main__':
    main()
