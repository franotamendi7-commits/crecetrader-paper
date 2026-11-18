# Seguridad — YouTube Trading Agent

## Principios

1. No conectar cuentas financieras con permisos de ejecucion
2. No incorporar permisos de retiro ni transferencia
3. No almacenar credenciales financieras en repositorios
4. No desarrollar ejecucion automatica
5. No asumir capitales ni asignaciones no autorizados
6. El usuario conserva siempre la decision y ejecucion de cada operacion

## Proteccion de datos

- No almacenar API keys en codigo o repositorios
- Usar variables de entorno para credenciales
- No incluir archivos .env en git
- No registrar secretos en logs ni manifiestos

## YouTube y licencias

- Respetar los terminos de servicio de YouTube
- No descargar videos de forma masiva sin verificar licencias
- Verificar licencias de herramientas y repositorios antes de usar
- Documentar licencias de todas las dependencias

## Aislamiento

- Proyecto completamente independiente del sistema anterior
- No modificar ni eliminar nada del sistema anterior
- No importar memoria del sistema anterior
- No auditar el sistema anterior

## Trading

- Manual unicamente
- Sin ejecucion automatica
- Capital y estrategias requieren autorizacion explicita
- Separar Binance Spot de Quantfury
