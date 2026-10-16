# platform-foundation Specification

## Purpose
Define el comportamiento observable de los cimientos del backend: expone endpoints de salud (liveness y readiness), carga y valida la configuración por entorno, y habilita el acceso del cliente web mediante CORS. Es la base sobre la que se apoyan todos los módulos funcionales posteriores.

## Requirements

### Requirement: Endpoint de liveness

El sistema DEBE (MUST) exponer un endpoint de liveness en `GET /api/health` que responda `200 OK` con el cuerpo `{"status": "ok"}` cuando el proceso del backend está en ejecución. Este endpoint NO DEBE depender de servicios externos (base de datos o colas).

#### Scenario: Servicio saludable

- **WHEN** un cliente realiza `GET /api/health` contra un backend en ejecución
- **THEN** el sistema responde `200 OK` con cuerpo `{"status": "ok"}`

#### Scenario: Ruta de salud inexistente

- **WHEN** un cliente realiza `GET /api/healthz` (ruta no declarada)
- **THEN** el sistema responde `404 Not Found`

### Requirement: Endpoint de readiness de dependencias

El sistema DEBE (MUST) exponer un endpoint de readiness en `GET /api/health/ready` que verifique la conectividad con PostgreSQL y Redis. Si TODAS las dependencias responden, DEBE responder `200 OK` con `{"status": "ok", "dependencies": {...}}`; si al menos una falla, DEBE responder `503 Service Unavailable` con `{"status": "degraded"}` y el detalle de la dependencia caída.

#### Scenario: Todas las dependencias disponibles

- **WHEN** un cliente realiza `GET /api/health/ready` y PostgreSQL y Redis responden
- **THEN** el sistema responde `200 OK` con `status` = `ok`

#### Scenario: Dependencia caída

- **WHEN** un cliente realiza `GET /api/health/ready` estando Redis inaccesible
- **THEN** el sistema responde `503 Service Unavailable` con `status` = `degraded` y Redis marcado como no disponible

#### Scenario: Ambas dependencias caídas

- **WHEN** un cliente realiza `GET /api/health/ready` y tanto PostgreSQL como Redis están inaccesibles
- **THEN** el sistema responde `503 Service Unavailable` con `status` = `degraded`

### Requirement: Configuración por entorno validada

El sistema DEBE (MUST) cargar su configuración desde variables de entorno y/o archivo `.env`, y DEBE validarla al arrancar. Si falta una variable requerida o su valor es inválido, el arranque DEBE fallar (fail-fast) con un error de validación explícito que indique la variable afectada. Las credenciales NUNCA DEBEN tener valores por defecto reales ni estar hardcodeadas.

#### Scenario: Configuración válida

- **WHEN** el proceso arranca con todas las variables requeridas definidas y con formato válido
- **THEN** la configuración carga sin errores y el servicio queda operativo

#### Scenario: Variable requerida ausente

- **WHEN** el proceso arranca sin la variable `DATABASE_URL`
- **THEN** el arranque falla con un error de validación que menciona `DATABASE_URL`

#### Scenario: Valor con formato inválido

- **WHEN** el proceso arranca con una variable numérica requerida (por ejemplo un puerto) con un valor no numérico
- **THEN** el arranque falla con un error de validación de tipo para esa variable

### Requirement: Política de CORS para el cliente web

El sistema DEBE (MUST) aplicar una política CORS que permita solicitudes desde el origen de desarrollo del frontend (`http://localhost:5173`). Las solicitudes cross-origin desde ese origen DEBEN recibir la cabecera `Access-Control-Allow-Origin` correspondiente; los orígenes no autorizados NO DEBEN recibirla.

#### Scenario: Preflight desde el origen permitido

- **WHEN** un navegador envía una solicitud `OPTIONS` (preflight) con `Origin: http://localhost:5173`
- **THEN** el sistema responde con `Access-Control-Allow-Origin: http://localhost:5173`

#### Scenario: Origen no autorizado

- **WHEN** un navegador envía una solicitud con `Origin: http://evil.example`
- **THEN** el sistema NO incluye la cabecera `Access-Control-Allow-Origin` para ese origen
