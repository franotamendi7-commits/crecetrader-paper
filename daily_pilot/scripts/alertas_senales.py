#!/usr/bin/env python3
"""ALERTAS DE SEÑALES — prepara y envía avisos de Discord.

Lee los trackers (tracker_paper.json y tracker_scalein.json) y detecta:
  · señales NUEVAS (forward) → aviso de entrada con stop, target y sizing
  · señales CERCA de un nivel o con resultado → aviso de cierre

El webhook se lee SOLO de ~/.hermes/.env (DISCORD_WEBHOOK_URL) o del
entorno. Nunca se pide ni se guarda en el repo.

PAPER_ONLY: avisa, NUNCA manda órdenes.

Uso:
    python3 daily_pilot/scripts/alertas_senales.py --preview   # ver sin enviar
    python3 daily_pilot/scripts/alertas_senales.py             # enviar si hay webhook
    python3 daily_pilot/scripts/alertas_senales.py --estado
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
D = BASE / 'daily_pilot' / 'datos'
ENV = Path.home() / '.hermes' / '.env'
ESTADO = D / 'alertas_senales_estado.json'


def webhook() -> str | None:
    if os.environ.get('DISCORD_WEBHOOK_URL'):
        return os.environ['DISCORD_WEBHOOK_URL']
    if ENV.exists():
        for line in ENV.read_text().splitlines():
            if line.startswith('DISCORD_WEBHOOK_URL='):
                return line.split('=', 1)[1].strip().strip('"\'')
    return None


def leer(nombre: str) -> dict:
    p = D / nombre
    try:
        return json.loads(p.read_text()) if p.exists() else {}
    except Exception:
        return {}


def stamps(j: dict) -> set:
    return {f"{o.get('par')}-{o.get('senal_ts')}" for o in j.get('operaciones') or []}


def construir() -> list[str]:
    msgs = []
    estado = leer_estado()
    for nombre, titulo in (('tracker_scalein.json', 'SCALE-IN FIBO'),
                           ('tracker_bos.json', 'BOS 4H+1H'),
                           ('tracker_paper.json', 'PULLBACK 4H')):
        j = leer(nombre)
        ops = j.get('operaciones') or []
        vistos = set(estado.get(nombre, []))
        for o in ops:
            key = f"{o.get('par')}-{o.get('senal_ts')}"
            if key in vistos:
                continue
            vistos.add(key)
            if o.get('origen') != 'forward':
                continue
            par = (o.get('par') or '').replace('USDT', '')
            fecha = o.get('senal_fecha') or ''
            entry = o.get('entrada') or o.get('stop_inicial')
            stop = o.get('stop') or o.get('stop_inicial')
            target = o.get('target')
            riesgo = o.get('riesgo_usd') or 0
            und = o.get('unidades')
            msg = (
                f"🚨 **NUEVA SEÑAL · {titulo}**\n"
                f"**{par}** · {fecha} UTC\n"
                f"Entrada: {entry} · Stop: {stop} · Target: {target}\n"
                f"Riesgo: ${riesgo} · Unidades: {und}\n"
                f"*PAPER ONLY — no se ejecutaron órdenes*"
            )
            msgs.append(msg)
        estado[nombre] = sorted(vistos)
    escribir_estado(estado)
    return msgs


def leer_estado() -> dict:
    try:
        return json.loads(ESTADO.read_text()) if ESTADO.exists() else {}
    except Exception:
        return {}


def escribir_estado(d: dict):
    ESTADO.write_text(json.dumps(d, indent=2))


def enviar(msg: str, url: str) -> bool:
    data = json.dumps({'content': msg}).encode()
    req = urllib.request.Request(
        url, data=data,
        headers={'Content-Type': 'application/json',
                 'User-Agent': 'CreceTrader-Paper/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status == 204
    except Exception as e:
        print(f"  ERROR Discord: {type(e).__name__}: {e}")
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--preview', action='store_true', help='mostrar sin enviar')
    ap.add_argument('--estado', action='store_true')
    a = ap.parse_args()

    if a.estado:
        print('webhook:', 'CONFIGURADO' if webhook() else 'NO CONFIGURADO')
        print('estado:', json.dumps(leer_estado(), indent=2)[:500])
        return 0

    msgs = construir()
    if not msgs:
        print('sin señales nuevas')
        return 0
    url = webhook()
    print(f"{len(msgs)} señales nuevas · webhook {'sí' if url else 'no'}")
    for m in msgs:
        print('\n' + '-' * 60 + '\n' + m)
        if not a.preview and url:
            enviar(m, url)
    if not url and not a.preview:
        print('\nPara activar: DISCORD_WEBHOOK_URL=... en ~/.hermes/.env')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
