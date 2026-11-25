# FILTRO POR DIA — validación par por par y cartera final

Fecha: 2026-11-25. PAPER_ONLY.

## Validación par por par (null corregido, 4 seeds)

| par | n sin filtro | n con filtro | E sin | E con | null | WF train→test |
|---|---:|---:|---:|---:|---:|---|
| **BTC** | 2413 | 1007 | +0,161 | **+0,231** | **4/4** ✅ | +0,239 → +0,211 |
| **THETA** | 1412 | 558 | +0,177 | **+0,339** | **4/4** ✅ | +0,253 → +0,540 |
| HBAR | 1255 | 533 | +0,079 | +0,081 | 0/4 ❌ | +0,130 → −0,034 |
| ETC | 1423 | 590 | +0,061 | +0,136 | 0/4 ❌ | +0,240 → −0,108 |
| ARB | 183 | 85 | +0,367 | +0,365 | 1/4 ❌ | +0,398 → +0,290 |
| XRP | 366 | 158 | +0,270 | +0,240 | 0/4 ❌ | +0,078 → +0,611 |

**Solo BTC y THETA validan el filtro** (null 4/4 y test positivo). Se aplica
el filtro Jue+Vie+Sáb solo a esos dos; los otros cuatro siguen sin filtrar.

## Cartera resultante

| | Original | **Con filtro parcial** |
|---|---:|---:|
| Señales | 7.052 | 4.792 |
| Esperanza | +0,140R | **+0,161R** |
| Acierto | — | 58,0% |
| **DD** | −98,1R | **−82,2R** |
| PF | 1,38 | **1,44** |
| DD $300 al 0,35% | −$103 | **−$86** |
| WF test | +0,086R | +0,110R |

### Últimos meses (lo bueno y lo malo)

| mes | Original | Con filtro |
|---|---:|---:|
| Ago 2026 | −5,36R | **−13,92R** ❌ |
| Sep 2026 | +8,98R | +11,53R |
| **Oct 2026** | **−1,26R** | **+6,55R** ✅ |
| Nov 2026 | +2,79R | +2,79R |

Meses malos por año: 2018 de −6,35R a **+15,03R**; 2025 de −18,78R a
**+0,51R**; 2022 de −55,48R a −37,09R.

## Veredicto

El filtro **mejora el DD y la esperanza** y arregla octubre, pero **empeora
agosto**. No es una mejora pareja: cambia qué meses son malos.

Es una opción válida, no una obligación. Para $300 al 0,35% deja el DD en
−$86 en vez de −$103. Si el objetivo es dormir tranquilo, conviene.

## Decisión pendiente

No lo aplico al tracker todavía porque el tracker ya está corriendo con la
configuración original y el forward recién empieza (0 operaciones). Cambiar
la regla ahora rompería la continuidad del registro.

Cuando haya forwards suficientes, se decide con datos reales cuál de las dos
configuraciones se queda.

PAPER_ONLY. No se ejecutaron órdenes.
