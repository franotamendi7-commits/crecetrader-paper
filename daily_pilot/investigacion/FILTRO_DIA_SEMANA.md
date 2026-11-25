# FILTRO POR DIA DE LA SEMANA — hallazgo fuerte, con salvedad

Fecha: 2026-11-25. Sobre la cartera validada de 6 pares. PAPER_ONLY.

## Hallazgo

Las señales del jueves y viernes son sistemáticamente mejores:

| día | E(R) en TEST (último 30%, nunca usado para elegir) |
|---|---:|
| **Vie** | **+0,270** |
| **Jue** | **+0,222** |
| Mié | +0,063 |
| Sáb | +0,057 |
| Lun | +0,046 |
| Dom | +0,050 |
| **Mar** | **−0,073** |

## Efecto en la cartera (serie ordenada, DD bien calculado)

| configuración | n | E | DD | PF |
|---|---:|---:|---:|---:|
| Todos los días | 7.052 | +0,140 | −98,1R | 1,38 |
| **Jue+Vie+Sáb** | 2.931 | **+0,209** | **−42,6R** | **1,62** |
| Jue+Vie | 1.899 | +0,245 | −34,6R | 1,76 |
| Solo Vie | 967 | +0,286 | −19,4R | 1,94 |

Años con el filtro Jue+Vie+Sáb: 2018 **+8,67R** (antes −6,35),
2022 **−11,69R** (antes −55,48), 2025 **+12,35R** (antes −18,78),
2026 **+41,57R**.

## Walk-forward (la prueba que sí discrimina)

| | train E | test E | DD train | DD test |
|---|---:|---:|---:|---:|
| Sin filtro | +0,164 | +0,086 | −98,1 | −84,5 |
| **Jue+Vie+Sáb** | +0,227 | **+0,168** | **−35,0** | **−42,6** |

El filtro **no degrada en el test**: +0,168 vs +0,086 del baseline. Y el
patrón por día se confirma en datos que no se usaron para elegirlo.

## Salvedad honesta: el null agregado NO sirve acá

```
SIN FILTRO:   real +0,140  p=0,542  RUIDO
JUE+VIE+SAB:  real +0,209  p=0,540  RUIDO
```

El null de cartera da RUIDO **incluso a la cartera que ya sabemos que valida
por par**. Es un artefacto: al agregar 6 pares se pierde la estructura que
el null por par sí conserva. **No puedo usar ese número para decidir.**

## Decisión

No lo agrego al tracker todavía. Tengo dos pruebas a favor (walk-forward
mejora y patrón confirmado en test) y una herramienta (null agregado) que no
sirve para este caso.

Lo correcto es validar el filtro **par por par con el null corregido**, que
sí discrimina. Ese es el próximo paso. Hasta entonces: candidato fuerte,
no operativo.

PAPER_ONLY. No se ejecutaron órdenes.
