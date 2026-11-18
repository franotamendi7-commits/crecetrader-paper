# Adjudicación de desacuerdos — Benchmark A.7.4

## Mecanismo

1. Dos anotadores independientes completan `anotador1.csv` y `anotador2.csv` **sin verse**.
2. Se ejecuta `scripts/b1_adjudicacion.py anotador1.csv anotador2.csv`.
3. El script compara campo a campo y genera:
   - `annotations/adjudicacion.csv` con una fila por frame y columna `estado`.
   - `annotations/desacuerdos.json` con el detalle.
4. Estados por campo:
   - `agreement` — ambos coinciden.
   - `disagreement` — difieren; requiere **adjudicación humana**.
   - `one_abstain` — uno marcó `NO LEGIBLE` y el otro no.
5. Los campos `disagreement` y `one_abstain` **no forman parte de la referencia validada** hasta que un tercero decida.
6. El tercero (adjudicador) completa la columna `adjudicado_<campo>` en `adjudicacion.csv` y registra `adjudicador` y `motivo`.

## Reglas

- La referencia validada = campos `agreement` + campos adjudicados.
- Los campos no resueltos se declaran `NO VERIFICABLE` y se excluyen de las métricas (nunca se asumen correctos).
- Se registra la tasa de acuerdo por campo (acuerdo / (acuerdo + desacuerdo)).

## Reproducción

```
.venv/bin/python3 benchmark_vision_b1/scripts/b1_adjudicacion.py \
    benchmark_vision_b1/annotations/anotador1.csv \
    benchmark_vision_b1/annotations/anotador2.csv
```
