# Delegacion de Modelos — YouTube Trading Agent

## Principio

Hermes evalua dinamicamente los modelos disponibles en OpenCode. No asume disponibilidad anterior.

## Modelos a evaluar

### Beam (reflection/beam-1.0-501b-a23b:free)
- Capacidades: Diseño, programacion, razonamiento
- Evaluacion: Seria para diseño y programacion
- No seleccionar automaticamente para todas las tareas

### DeepSeek
- Capacidades: Programacion, razonamiento
- Evaluacion: Alternativa fuerte para codigo

### GLM
- Capacidades: Programacion, analisis
- Evaluacion: Alternativa para tareas de analisis

### Otros modelos disponibles via OpenCode
- Evaluar dinamicamente segun disponibilidad, cuotas y capacidades

## Criterios de seleccion

Por cada tarea, Hermes debe considerar:
1. Dificultad de la tarea
2. Especializacion requerida
3. Calidad esperada
4. Disponibilidad del modelo
5. Coste (gratuito vs pago)
6. Limites gratuitos
7. Recursos del equipo (RAM, CPU)
8. Velocidad de respuesta

## Coordinacion multi-modelo (futuro)

Ejemplo de flujo:
- Modelo A diseña la solucion
- Modelo B implementa
- Modelo C audita independientemente
- Hermes compara y decide

No abrir terminales innecesarias. No saturar el equipo.

## Verificacion de disponibilidad

Antes de cada delegacion:
- Comprobar modelos disponibles en OpenCode
- Verificar cuotas y limites
- Detectar modelos bloqueados temporalmente
- Medir velocidad si es posible
