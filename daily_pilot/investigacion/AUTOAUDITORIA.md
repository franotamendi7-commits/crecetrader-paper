# Autoauditoria fija

```bash
cd /Users/franciscootamendi/YouTubeTradingAgent
~/.hermes/hermes-agent/venv/bin/python3 daily_pilot/scripts/autoauditoria.py
```

**Read-only**: no escribe en el repo vivo. La suite de integracion corre en una
copia temporal.

## 7 bloques

| # | Que verifica |
|---|---|
| 1 | ancla: HEAD, rama, working tree limpio |
| 2 | store.db: integridad + conteos |
| 3 | suites: read-only (15) y integracion (17, en copia) |
| 4 | `PAPER_ONLY` + sin llamadas de ejecucion + sin claves |
| 5 | dash: paneles, avisos, autocontenido |
| 6 | metodo: hash del playbook anclado en la firma + 12 reglas |
| 7 | pares de Quantfury: que todos tengan datos |

## Hallazgos de la 1ª corrida (2026-11-22)

| Hallazgo | Estado |
|---|---|
| el script se auditaba a si mismo (`PAPER_ONLY=False` falso) | corregido (se excluye) |
| `gen.velas` no existia | corregido (import aparte) |
| hash del playbook desactualizado por el anexo C14 | anclado |
| `test_dashboard_v5` intermitente | precios vivos (no es bug) |

**Pares:** 33 de Quantfury (Binance). FTM ya no existe -> S (Sonic). TON en BREAK.
