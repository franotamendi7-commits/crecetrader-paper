# Roadmap — YouTube Trading Agent

## Fase 0: Base tecnica y documental (ACTUAL)

- Crear directorio independiente
- Crear documentacion inicial (10 archivos)
- Investigar repositorios GitHub para agente YouTube
- Evaluar modelos disponibles
- Proponer stack tecnologico
- Entregar plan de implementacion

**NO programar el agente todavia.**

## Fase 1: Agente YouTube (audio + vision + comprension)

- Extraer audio de videos (yt-dlp, ffmpeg)
- Transcribir con timestamps (Whisper o similar)
- Analizar fotogramas (modelo de vision)
- Detectar cambios de graficos (scene detection)
- Identificar instrumentos, temporalidades, velas
- Reconocer niveles, zonas, indicadores
- Clasificar conclusiones: [DICE], [OBSERVADO], [INFERIDO]
- Comparar videos anteriores

## Fase 2: Market Data + Analytics Manager

- Integrar fuentes de datos reales (OHLCV)
- Estructura de mercado
- Temporalidades
- Niveles y escenarios
- Probabilidades estadisticas

## Fase 3: Risk Manager + Dashboard + Discord

- Gestion de capital y exposicion
- Dashboard de presentacion
- Alertas via Discord
- Canales separados por funcion

## Fase 4: Memoria selectiva + integracion

- Memoria de evidencia y metodologia
- Reglas aprobadas
- Estadisticas
- Integracion completa del sistema
