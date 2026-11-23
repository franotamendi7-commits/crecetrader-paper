# Pine — archivado como NO VIABLE (2026-11-23)

Francisco lo probo 3 veces. Lo que fallo:

| version | error |
|---|---|
| v4/v5 | `request.*()` dentro de un `if` sin `dynamic_requests` |
| v6 | sin request: andaba, pero dibujaba los niveles de OTRO timeframe en 4H |
| v7/v8 | multi-TF con `request.security`: timeframes y dibujado inestables |

**Veredicto de Francisco:** «fracaso total, olvidate del pine».

No se borra: queda como referencia de lo que no funciono. El motor Python
(`core/tramos.py`, `core/zonas.py`) sigue siendo la fuente de verdad.
