# Resumen: nuevo Hermes Agent Workspace (Juan Pe Navarro)

Video: https://www.youtube.com/watch?v=_RfLc8haMUo
Duración: 17:15. Fuente: subtítulos automáticos ES descargados con yt-dlp.
NO es un video de trading — es un tutorial de instalación y uso del workspace.

## Qué es

> "Ecosistema completo de agentes de inteligencia artificial en el nuevo
> Hermes Agent Workspace... que hagan cualquier locura que tú le pidas de
> manera completamente autónoma."

Metáfora del video: **Hermes Agent solo es un coche; el Workspace es la flota
completa**. Es el "centro de comando", similar al concepto de Paperclip
(orquestación de agentes) pero "potenciado por 1000". Trae **11 empleados**
(roles predefinidos).

## Instalación (lo que muestra)

1. **VPS Hostinger** con instalación en un clic: "one click Hermes agent".
   Planes de 12 o 24 meses (a más meses, más barato) con "agente/equipo
   ilimitado".
2. Guardar bien la **password del workspace** (acceso a la app).
3. En Workspace → **API Keys** → New API Key: nombre "Hermes Agent",
   sin límite, expiración 1 hora (por seguridad). Copiarla y pegarla en la
   configuración.
4. Usa **Open Router API Key** como "cerebro" de los agentes.

## Interfaz

- **Hermis World**: vista visual tipo juego donde agentes y personas trabajan juntas.
- **Conductor**: panel lateral con los agentes de IA.
- **Tablero Kanban**: tareas en Triage, etc.
- **Swarm**: añadir swarm; si elegís un rol, se rellena solo.

## Costos (relevante para nosotros)

- El video advierte: **"el coste de las APIs en loops es algo a tener en cuenta"**.
- Se pueden **limitar los tokens en la config** para no entrar en problemas
  económicos.

Esto coincide con lo que ya sabemos: el modelo `hy4-flash:free` se quedó sin
cuota por loops, y por eso el buscador de estrategias se mandó a un subagente.

## Otros comentarios

- Dice que Hermes está "superando bastante fuerte a OpenCode"; a OpenCode le
  quedaría su marketplace de skills, mientras Hermes ya tiene "skills validadas".
- Mentorías gratuitas los domingos; el autor es socio fundador de The Visual
  Project (agencia/academia de IA, ciberseguridad y marketing).
- Frase final: "la oportunidad no está en las herramientas, está en entender
  el orden... la herramienta es gratis, paga por entender".

## Aplicación a CreceTrader

- No aporta nada nuevo a la estrategia de trading.
- Sí confirma dos decisiones ya tomadas: **limitar tokens** y **orquestar
  agentes** (el subagente que dejé buscando estrategias es exactamente ese
  patrón de "flota" trabajando en paralelo).
