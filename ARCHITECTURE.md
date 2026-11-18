# Arquitectura — YouTube Trading Agent

## Vision general

```
HERMES (orquestador)
  ├── YOUTUBE AGENT (analisis audiovisual)
  ├── MARKET DATA (precios, OHLCV, volumen)
  ├── ANALYTICS MANAGER (estructura, niveles, escenarios)
  ├── RISK MANAGER (capital, exposicion, stops)
  ├── DASHBOARD + DISCORD (presentacion, alertas)
  └── MEMORIA SELECTIVA (evidencia, metodologia, decisiones)
```

## Responsabilidades por componente

### HERMES
- Comprender objetivos
- Diseñar arquitectura
- Dividir trabajo en tareas
- Elegir herramientas y modelos
- Delegar implementacion a OpenCode
- Coordinar agentes y terminales
- Supervisar desarrollo
- Revisar resultados
- Solicitar auditorias independientes
- Validar pruebas
- Registrar decisiones

### YOUTUBE AGENT (prioridad 1)
- Extraer audio de videos
- Transcribir con timestamps
- Analizar fotogramas (vision)
- Detectar cambios de graficos
- Identificar instrumentos, temporalidades, velas
- Reconocer niveles, zonas, indicadores
- Reconstruir graficos TradingView
- Comparar videos anteriores
- Clasificar conclusiones: [DICE], [OBSERVADO], [INFERIDO]

### MARKET DATA (fase futura)
- Precios reales (OHLCV, volumen)
- Datos historicos
- Calidad y trazabilidad de fuentes

### ANALYTICS MANAGER (fase futura)
- Estructura de mercado
- Temporalidades
- Fases de mercado
- Niveles
- Escenarios
- Probabilidades estadisticas

### RISK MANAGER (fase futura)
- Capital
- Exposicion
- Tamaño de posicion
- Stops
- Perdida potencial
- Limites de riesgo

### DASHBOARD + DISCORD (fase futura)
- Presentacion de analisis
- Escenarios
- Niveles
- Riesgo
- Alertas y comunicaciones

### MEMORIA SELECTIVA (fase futura)
- Evidencia
- Metodologia
- Decisiones
- Observaciones
- Estadisticas
- Reglas aprobadas

## Principio de aislamiento

Este proyecto NO hereda nada de CHIEF/Harness. Arquitectura, codigo, dependencias y memoria son independientes.

## Fases de implementacion

1. Fase 0: Base documental + investigacion GitHub (ACTUAL)
2. Fase 1: Agente YouTube (audio + vision + comprension)
3. Fase 2: Market Data + Analytics Manager
4. Fase 3: Risk Manager + Dashboard + Discord
5. Fase 4: Memoria selectiva + integracion
