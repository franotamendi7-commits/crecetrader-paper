# AGENTE_BUSQUEDA_LOG — Exploración autónoma de nuevas estrategias
PAPER_ONLY. Sin órdenes. Sin modificaciones al repo salvo este archivo.

Protocolo aplicado a CADA idea:
- Velas leídas DIRECTO con `json` desde `daily_pilot/datos/velas/*.json` (nunca `velas()`).
- Walk-forward 70/30: optimización de parámetros SOLO en train (primer 70% de velas ordenadas por ts), evaluación en test (último 30%).
- Validación con `null_corregido` multi-seed (4 seeds: 7, 11, 23, 42; 50 permutaciones/seed sobre el test).
- VÁLIDA solo si: p<=0.05 en >=3/4 seeds Y E(test)>0 Y n(test)>=15.
- Métricas: n, señales/mes, esperanza R, win%, DD (R), PF.

---
