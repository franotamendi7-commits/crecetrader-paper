# Verdicto de la auditoria integral (DeepSeek) — aplicado por Hermes

Fecha: 2026-11-20 · Auditor: DeepSeek · Verificacion y arreglo: Hermes
HEAD auditado: `dd0a562` (el ancla pedido era `a3b7c0c`, ancestro; el diff era solo
`.DS_Store` + el prompt de auditoria).

## 1 · Lo que DeepSeek hallo y Hermes verifico

| ID | Severidad | Estado | Evidencia de Hermes |
|---|---|---|---|
| **P0-1** | integracion abre el store vivo | **ARREGLADO** | `anadir_temporalidad.py` usaba `sys.path.insert` absoluto; ahora es relativo a `__file__`. Guard anti-huye en `store.conectar()` probado (rechaza `/tmp/store_malo.db`) |
| **P0-2** | el playbook firmado ya no coincide | **PENDIENTE DE FIRMA** | `shasum` actual `725a1233…` vs firmado `b4db713f…`. El cambio es por los **anexos C05-A/C05-B** que Francisco valido el 2026-11-20 |
| **P0-3** | `informe_dia.py` afirmaba «propone el motor C01-C12» | **ARREGLADO** | docstring corregido |
| **P1-4** | C09: 7 tramos × 25% = 175% | **ARREGLADO** | `objetivos.py` reparte el 100% entre los N objetivos (con 4 daba 25%) |
| **P1-5** | C10: confianza 0,50 fijo | **DOCUMENTACION VIEJA** | el codigo ya dice «la confianza la asigna el trader» (`CONF_DEFECTO = 0.50`); el playbook del 18/11 queda viejo |
| **P1-6** | Manager default `1.0` (5% de riesgo) | **ARREGLADO** | default `0.50` → 2,5% sin confianza explicita |
| **P1-9** | test de capturas con falso OK | **ARREGLADO** | comparaba `mn` contra `mn`; ahora usa `z['minimo']`. Y esta en `run_all.py` |
| **P1-10** | Pine decia «sacamos request.security» y no era cierto | **ARREGLADO** | las 3 llamadas van **dentro** del `if` (no se ejecutan si estan apagadas) |
| P1-1 | C01 sin jerarquia W>D>4H | abierto | no implementado; solo etiquetas |
| P1-2 | C04 11 niveles/1000 pts vs firma «9 niveles %» | **DOCUMENTACION VIEJA** | Francisco valido el 20/11 el abanico con fibo × 1000 puntos (8/8 contra captura) |
| P1-3 | C05 4/7 vs firma 3/4 | **DOCUMENTACION VIEJA** | anexo C05-A validado con 12 niveles exactos |
| P1-7 | C12 sin TF en `liquidez.py` | abierto | |
| P1-8 | la FIRMA lista 11 reglas, falta C06 | abierto | C06 existe y testea 15/15 |
| P2-1 | el ticker del dash no dice que el precio es del video | **ARREGLADO** | ahora muestra `(dicho en EX-Rx_pnNpc)` |
| P2-2 | playbook con conteos viejos | **ARREGLADO** | 21.986 claims / 111 videos |
| P2-4 | `paper_only` faltante en 2 ramas | **ARREGLADO** | las 3 ramas lo incluyen |
| P2-5 | `PAPER_ONLY` faltante en 3 modulos | **ARREGLADO** | `model.py`, `plan_classifier.py`, `precios.py` |
| P2-6 | comentarios/code viejos | **ARREGLADO** | test_zonas |
| P2-7 | `dashboard_data.json` leftover | **ARREGLADO** | movido a `investigacion/legacy/` |
| P2-3 | correccion como regimen (firma vs playbook vs codigo) | abierto | decision de metodo |

## 2 · Suite despues de los arreglos

```
run_all.py             -> 15 OK · 0 FALLO · FUENTES INTACTAS
run_all.py --integracion -> 17 OK · 0 FALLO · FUENTES INTACTAS
verify_integrity.py    -> OK (111 videos / 128.593 cues / 21.986 claims)
test_capturas_tradingview.py -> 19/19
```

## 3 · Lo que queda abierto antes del dash

1. **P0-2 — re-firmar.** El playbook tiene los anexos C05-A (0,61) y C05-B
   (tramo por ciclo) que Francisco valido el 2026-11-20 y no estan firmados.
   **Necesita la firma de Francisco.**
2. **C01 jerarquia W>D>4H**, **C12 con TF**, **C06 en la firma**.
3. **C04 y C05 del texto firmado vs el codigo**: el codigo sigue los anexos
   validados; el texto firmado quedo viejo. Resolver al re-firmar.
4. **Dash**: precio ya etiquetado como «del video». Falta el feed real y los
   otros pares (Binance read-only, pendiente de diseño).
5. **Pine**: falta confirmar compilacion y el bug de 4H en TradingView.

## 4 · Veredicto

**No corresponde pasar el dash como «motor C01–C12 validado».** El motor
implementa C02, C03, C06, C08 fielmente; C05 esta validado contra las capturas
pero su texto firmado quedo viejo; C01, C09, C10, C11, C12 estan parciales.

**Sí corresponde mostrarlo como panel de lectura del ultimo video**, con el
precio etiquetado como precio del video (ya hecho).
