#!/usr/bin/env python3
"""Tramo por timeframe + confluencia (C05, Francisco, 2026-11-20).

Metodo:
  - Cada TF tiene su **propia tendencia** -> su **propio tramo** (minimo -> maximo).
  - Sobre ese tramo: retrocesos 50/61/78 y extensiones 50/100/150/200.
  - Donde coinciden varios TF -> **confluencia** (zona de compra).

PAPER_ONLY: describe y calcula, no ejecuta.
"""
from __future__ import annotations

PAPER_ONLY = True
from zonas import zonas, RETROCESOS, EXTENSIONES, tf_para   # noqa: E402
from regimen import (detectar, es_cambio, TENDENCIA_ALCISTA,  # noqa: E402
                     TENDENCIA_BAJISTA, RANGO, NO_DETERMINADO)

PLAZOS = ('largo', 'media', 'corto')


def swing(velas: list[dict], n: int = 5) -> dict:
    """Swing highs/lows: un punto es extremo si es el mayor/menor de n velas a cada lado.

    n = fuerza del swing (cuantas velas tiene que superar).
    Devuelve {'altos': [(i, precio)], 'bajos': [(i, precio)]}
    """
    altos, bajos = [], []
    for i in range(len(velas)):
        v = velas[i]
        izq = velas[max(0, i - n):i]
        der = velas[i + 1:i + 1 + n]
        if len(izq) + len(der) < 2:
            continue
        if all(v['high'] >= x['high'] for x in izq + der) and len(der) == n:
            altos.append((i, v['high']))
        if all(v['low'] <= x['low'] for x in izq + der) and len(der) == n:
            bajos.append((i, v['low']))
    return {'altos': altos, 'bajos': bajos}


def tramo_ultimo_swing(velas: list[dict], n: int = 5) -> dict:
    """El tramo de la tendencia = ultimo swing (maximo y minimo relevantes).

    Orden temporal: el punto de arranque es el ANTERIOR en el tiempo.
      alcista  -> desde el minimo (piso) hasta el maximo (techo)
      bajista  -> desde el maximo (techo) hasta el minimo (piso)
    """
    if len(velas) < n * 2 + 1:
        return {'error': 'faltan velas'}
    s = swing(velas, n)
    if not s['altos'] or not s['bajos']:
        return {'error': 'sin swing'}
    ult_alto = s['altos'][-1]
    ult_bajo = s['bajos'][-1]
    if ult_bajo[0] < ult_alto[0]:
        direccion, ini, fin = 'alcista', ult_bajo, ult_alto
    else:
        direccion, ini, fin = 'bajista', ult_alto, ult_bajo
    return {'direccion': direccion,
            'desde': ini, 'hasta': fin,
            'puntos': {
                'desde': {'i': ini[0], 'precio': ini[1], 'fecha': velas[ini[0]]['ts']},
                'hasta': {'i': fin[0], 'precio': fin[1], 'fecha': velas[fin[0]]['ts']}}}


def tramo(velas: list[dict]) -> dict:
    """Minimo y maximo de la tendencia, a partir de velas {high, low}.

    velas: lista ordenada en el tiempo (las mas viejas primero).
    """
    if not velas:
        return {'error': 'sin velas'}
    altos = [v['high'] for v in velas]
    bajos = [v['low'] for v in velas]
    return {'minimo': min(bajos), 'maximo': max(altos),
            'n_velas': len(velas), 'ultimo_cierre': velas[-1].get('close')}


def regimen_de(velas: list[dict], n: int = 5, k: int = 3) -> dict:
    """Regimen (C07) sobre los ultimos k SWINGS (maximos y minimos relevantes).

    Antes usaba los maximos/minimos globales y casi siempre caia en rango o
    correccion. Con swings es la estructura real de la tendencia.
    """
    if len(velas) < n * 2 + 1:
        return {'regimen': NO_DETERMINADO, 'motivo': 'faltan velas'}
    s = swing(velas, n)
    if len(s['altos']) < k or len(s['bajos']) < k:
        return {'regimen': NO_DETERMINADO, 'motivo': 'faltan swings'}
    maxs = [p for _, p in s['altos'][-k:]]
    mins = [p for _, p in s['bajos'][-k:]]
    return detectar(maxs, mins)


def calcular(velas: list[dict], plazo: str = 'corto') -> dict:
    """Fibos sobre el tramo de la tendencia en ese plazo."""
    t = tramo(velas)
    if 'error' in t:
        return t
    r = regimen_de(velas)
    z = zonas(t['minimo'], t['maximo'], plazo=plazo)
    return {'tramo': t, 'regimen': r, 'zonas': z, 'tf': tf_para(plazo)}


def confluencia(por_plazo: dict, tolerancia_pct: float = 0.005) -> list[dict]:
    """Niveles donde coinciden 2+ plazos (misma zona).

    tolerancia: 0.005 = 0,5% de tolerancia en el precio.
    """
    bolsas = []
    for plazo, res in (por_plazo or {}).items():
        z = (res or {}).get('zonas') or {}
        for lista in ('zonas_compra', 'extensiones'):
            for k, v in (z.get(lista) or {}).items():
                bolsas.append({'plazo': plazo, 'tipo': lista, 'nivel': k, 'precio': float(v)})
    out = []
    for b in bolsas:
        grupo = [o for o in bolsas
                 if abs(o['precio'] - b['precio']) <= max(1.0, abs(b['precio']) * tolerancia_pct)]
        plazos = sorted({g['plazo'] for g in grupo})
        if len(plazos) >= 2:
            out.append({'precio': round(b['precio'], 2), 'plazos': plazos,
                        'n_confluencias': len(plazos), 'detalle': grupo})
    # dedup por precio cercano
    out.sort(key=lambda x: -x['n_confluencias'])
    seen, limpia = [], []
    for o in out:
   	    if any(abs(o['precio'] - s) <= 1.0 for s in seen):
   	        continue
   	    seen.append(o['precio']); limpia.append(o)
    return limpia


if __name__ == '__main__':
    # validacion con las 3 capturas de BNB (2026-11-20)
    semanal = [{'high': 1371.90, 'low': 537.21, 'close': 533.82}] * 20
    diario = [{'high': 808.24, 'low': 537.81, 'close': 534.82}] * 20
    h4 = [{'high': 809.57, 'low': 530.54, 'close': 534.68}] * 20
    r = confluencia({'largo': calcular(semanal, 'largo'),
                     'media': calcular(diario, 'media'),
                     'corto': calcular(h4, 'corto')})
    print('confluencias BNB:', [(x['precio'], x['n_confluencias']) for x in r[:8]])


def nivel_anual(par: str, anio: int = None) -> dict:
    """Nivel del 1 de enero: cierre de la vela diaria del 1/01 00:00 UTC.

    Francisco, 2026-11-20: "el nivel del 1 de enero es un nivel calculado que se
    calcula una vez por anio" -> es el cierre del 1/01.
    """
    import datetime
    if anio is None:
        anio = datetime.datetime.utcnow().year
    try:
        from velas import velas as _velas
        r = _velas(par, '1d', limite=600)
        if 'error' in r:
            return {'error': r['error']}
        for v in r['velas']:
            f = datetime.datetime.utcfromtimestamp(v['ts'] / 1000)
            if f.year == anio and f.month == 1 and f.day == 1:
                return {'par': par, 'anio': anio, 'fecha': f.strftime('%Y-%m-%d'),
                        'precio': v['close'], 'fuente': r['fuente']}
        return {'error': f'no hay vela del 1/01/{anio} ({len(r["velas"])} velas)'}
    except Exception as e:
        return {'error': f'{type(e).__name__}: {e}'}


def cambios_de_tendencia(velas: list[dict], n: int = 5, k: int = 3) -> list[dict]:
    """Puntos donde la tendencia cambia (C07 + Francisco 2026-11-20).

    Regla de Francisco: "si venimos todos maximos mayores y cambia a minimos
    menores, ahi esta el cambio de tendencia". Se evalua sobre los ultimos k
    swings (maximos y minimos relevantes).
    """
    s = swing(velas, n)
    maximos = [p for _, p in s['altos']]
    minimos = [p for _, p in s['bajos']]
    if len(maximos) < k + 1 or len(minimos) < k + 1:
        return []

    def regimen(j):
        """Regimen segun los ultimos k swings (hasta el swing j)."""
        ms = maximos[max(0, j - k + 1):j + 1]
        ns = minimos[max(0, j - k + 1):j + 1]
        if len(ms) < k or len(ns) < k:
            return NO_DETERMINADO
        if all(b > a for a, b in zip(ms, ms[1:])) and all(b > a for a, b in zip(ns, ns[1:])):
            return TENDENCIA_ALCISTA
        if all(b < a for a, b in zip(ms, ms[1:])) and all(b < a for a, b in zip(ns, ns[1:])):
            return TENDENCIA_BAJISTA
        return RANGO

    cambios, prev = [], None
    # recorrer los swings en orden temporal
    puntos = sorted([(i, 'max', p) for i, p in s['altos']] +
                    [(i, 'min', p) for i, p in s['bajos']])
    idx_max = [j for j, (_, t, _) in enumerate(puntos) if t == 'max']
    for pos in range(k, len(puntos)):
        j_max = sum(1 for j in idx_max if j <= pos)
        if j_max < k + 1:
            continue
        r = regimen(j_max - 1)
        if prev and r != prev and r in (TENDENCIA_ALCISTA, TENDENCIA_BAJISTA):
            cambios.append({'i': puntos[pos][0], 'de': prev, 'a': r,
                            'fecha': velas[puntos[pos][0]]['ts'],
                            'precio': puntos[pos][2]})
        if r in (TENDENCIA_ALCISTA, TENDENCIA_BAJISTA):
            prev = r
    return cambios


def tramo_tendencia(velas: list[dict], n: int = 5, ultimo: bool = True, k: int = 3) -> dict:
    """El tramo de la tendencia = entre dos cambios de tendencia.

    ultimo=True  -> el tramo VIVO (desde el ultimo cambio hasta hoy)
    ultimo=False -> el ultimo tramo COMPLETO (entre los dos ultimos cambios)
    """
    c = cambios_de_tendencia(velas, n, k)
    if not c:
        return {'error': 'sin cambios de tendencia', 'n': n, 'k': k}
    elegido = c[-1] if (ultimo or len(c) < 2) else c[-2]
    fin = len(velas) - 1 if ultimo or len(c) < 2 else c[-1]['i']
    trozo = velas[elegido['i']:fin + 1]
    if not trozo:
        return {'error': 'tramo vacio'}
    return {'desde': elegido['i'], 'hasta': fin, 'direccion': elegido['a'],
            'desde_fecha': elegido['fecha'], 'hasta_fecha': velas[fin]['ts'],
            'minimo': min(x['low'] for x in trozo), 'maximo': max(x['high'] for x in trozo),
            'cambios': c}


def tramo_ciclo(velas: list[dict], n: int = 3, ventana: int = 60) -> dict:
    """Tramo del ciclo: del maximo mas alto al minimo mas bajo posterior.

    Cada TF tiene SU swing (Francisco: macro = semanal, micro = diario y 4h).
    Validado contra las capturas BNB 2026-11-20:
      1w -> 1.375,11 (oct 2025) -> 537,25 (jun 2026)   [captura 537,21 -> 1.371,90]
      1d ->   809,99 (oct 2026) -> 530,00 (nov 2026)   [captura 536,58 -> 808,24]
      4h ->   809,99 (oct 2026) -> 530,00 (nov 2026)   [captura 530,54 -> 809,57]
    """
    if len(velas) < n * 2 + 1:
        return {'error': 'faltan velas'}
    s = swing(velas, n)
    pts = sorted([(i, 'max', p) for i, p in s['altos']] +
                 [(i, 'min', p) for i, p in s['bajos']], key=lambda x: x[0])
    if len(pts) < 2:
        return {'error': 'sin swings'}
    rec = pts[-ventana:]
    alto = max((x for x in rec if x[1] == 'max'), key=lambda x: x[2], default=None)
    if alto is None:
        return {'error': 'sin maximo en la ventana'}
    post = [x for x in pts if x[0] >= alto[0]]
    bajos = [x for x in post if x[1] == 'min']
    # el piso de HOY puede no estar confirmado como swing (le faltan velas);
    # se incluye el minimo de las velas posteriores al maximo
    # el piso del ciclo = el minimo de TODAS las velas posteriores al maximo
    # (incluye el piso de hoy, que aun no esta confirmado como swing)
    seg = velas[alto[0]:]
    bajo = min(seg, key=lambda x: x['low']) if seg else alto
    return {'direccion': 'bajista' if bajo['ts'] > velas[alto[0]]['ts'] else 'alcista',
            'maximo': alto[2], 'maximo_fecha': velas[alto[0]]['ts'],
            'minimo': bajo['low'], 'minimo_fecha': bajo['ts'],
            'n_velas': len(seg)}
