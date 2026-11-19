## Purpose

Define la estructura de autenticación y autorización para el sistema C-03, incluyendo endpoints JWT y gestión de sesiones con Redis blacklist obligatoria.

## ADDED Requirements

### Requirement: Sistema de Autenticación JWT

El sistema DEBE implementar autenticación mediante JSON Web Tokens (JWT) para identificar usuarios en endpoints protegidos.

#### Scenario: Login exitoso
- **WHEN** el usuario envía credenciales válidas (email + password) mediante POST /auth/login
- **THEN** el sistema debe responder con 200 y un token JWT firmado con SECRET_KEY y algoritmo HS256.
- **AND** el token debe incluir el claim `jti` (JWT ID) y expirar tras ACCESS_TOKEN_EXPIRE_MINUTES minutos.
- **AND** el `jti` debe agregarse a Redis blacklist con TTL igual a la vida restante del token.

#### Scenario: Credenciales incorrectas
- **WHEN** el usuario envía credenciales inválidas (email no registrado o password incorrecto) mediante POST /auth/login
- **THEN** el sistema debe responder con 401 y un mensaje de error descriptivo (sin filtrar si el email existe o no por seguridad).
- **AND** no se agrega ningun `jti` a Redis.

#### Scenario: Token ausente
- **WHEN** se solicita un endpoint protegido (GET /auth/me, POST /auth/logout) sin incluir el header Authorization
- **THEN** el sistema debe responder con 401 y el mensaje "Token ausente".

#### Scenario: Token inválido
- **WHEN** el header Authorization incluye un token que no puede ser decodificado o cuyos datos son inválidos
- **THEN** el sistema debe responder con 401 y el mensaje "Token inválido".

#### Scenario: Token expirado
- **WHEN** el header incluye un token cuya fecha de expiración (exp) es anterior a la fecha actual
- **THEN** el sistema debe responder con 401 y el mensaje "Token expirado".

#### Scenario: Usuario inactivo
- **WHEN** el usuario autenticado tiene is_active = False en la base de datos
- **THEN** el sistema debe responder con 403 y el mensaje "Usuario inactivo".

#### Scenario: Logout efectivo
- **WHEN** el usuario envía POST /auth/logout con un token válido incluido en el header Authorization
- **THEN** el sistema debe agregar el `jti` del token a Redis blacklist con TTL hasta su expiración natural y responder con 200.
- **AND** el token quedará invalido para futuras peticiones al ser consultado en get_current_user.

#### Scenario: Redis no disponible
- **WHEN** el sistema intenta hacer logout y Redis no está disponible (conexión fallada o caído)
- **THEN** el sistema debe responder con 503 y el mensaje "Servicio de sesión no disponible. Intente nuevamente más tarde."
- **AND** **NOT** informar éxito ni afirmar que el token fue invalidado. La expiración natural del JWT no equivale a una revocación inmediata.

#### Scenario: Token invalidado rechazado por get_current_user
- **WHEN** get_current_user consulta Redis blacklist y encuentra el `jti` del token
- **THEN** el sistema debe responder con 401 y el mensaje "Token invalidado. Ha sido revocado previamente."

#### Scenario: Verificación de contraseña sin bloquear event loop
- **WHEN** se verifica una contraseña usando bcrypt en una petición HTTP
- **THEN** la operación debe ejecutarse en un ThreadPoolExecutor para no bloquear el event loop de FastAPI.
- **AND** el tiempo de respuesta debe ser acceptable (bcrypt con factor de trabajo moderado).

### Requirement: Entidades de Dominio Base

El sistema DEBE permitir la autenticación de usuarios usando los campos email y password_hash del modelo User, sin necesidad de agregar nuevos campos para la versión inicial.

#### Scenario: Login con email y password_hash
- **WHEN** se verifica un usuario con email y password_hash almacenado en la base de datos
- **THEN** el sistema debe comparar el password provisto con el hash almacenado usando bcrypt en ThreadPoolExecutor.
- **AND** devolver éxito o fracaso sin exponer el hash en mensajes de error.

#### Scenario: Identificar rol del usuario
- **WHEN** el usuario se autentica exitosamente
- **THEN** el sistema debe hacer disponible el rol del usuario en el payload del token o en la respuesta del endpoint /auth/me.

## Requirement: Configuración Segura

El sistema DEBE configurar JWT con los siguientes parámetros obligatorios:

#### Scenario: Configuración JWT obligatoria
- **WHEN** la aplicación inicia, debe validar que las siguientes variables estén definidas y sean seguras:
  - `SECRET_KEY`: Clave secreta para firma JWT (obligatoria, sin default inseguro).
  - `ALGORITHM`: Debe ser exactamente "HS256".
  - `ACCESS_TOKEN_EXPIRE_MINUTES`: Entero positivo (>0).
- **WHEN** alguna variable crítica falta, la aplicación debe fallar al arranque (fail-fast).

#### Scenario: Variables de entorno
- `SECRET_KEY`: Generada por el desarrollador, sin valores por defecto inseguros.
- `ALGORITHM`: Fijo en "HS256".
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Entero positivo configurado (ej. 30).
- `REDIS_URL`: Heredado de C-2, obligatorio para blacklist de tokens.

### Requirement: Roles y Identificación

El sistema DEBE poder identificar el rol del usuario autenticado mediante la relación con la tabla Role existente.

#### Scenario: Identificar rol del usuario
- **WHEN** el usuario se autentica exitosamente
- **THEN** el sistema debe hacer disponible el rol del usuario en el payload del token o en la respuesta del endpoint /auth/me.
- **AND** el rol debe ser consistente con la relación `User.role` definida en el modelo.

## Requirement: Pruebas de Integración

El sistema DEBE tener pruebas de integración que eleven los siguientes escenarios:

#### Scenario: Login exitoso
- **WHEN** se envían credenciales correctas mediante POST /auth/login
- **THEN** se recibe 200 con un token JWT con `jti`, `exp` y rol del usuario.

#### Scenario: Credenciales incorrectas
- **WHEN** se envían credenciales incorrectas mediante POST /auth/login
- **THEN** se recibe 401 sin filtrar información sobre si el email existe.

#### Scenario: Token ausente
- **WHEN** se solicita GET /auth/me o POST /auth/logout sin header Authorization
- **THEN** se recibe 401 "Token ausente".

#### Scenario: Token inválido
- **WHEN** el header Authorization incluye un token malformado o corrupto
- **THEN** se recibe 401 "Token inválido".

#### Scenario: Token expirado
- **WHEN** el header incluye un token con `exp` anterior a la fecha actual
- **THEN** se recibe 401 "Token expirado".

#### Scenario: Usuario inactivo
- **WHEN** el usuario autenticado tiene is_active = False
- **THEN** se recibe 403 "Usuario inactivo".

#### Scenario: Logout efectivo
- **WHEN** se envía POST /auth/logout con token válido
- **THEN** se recibe 200 y el `jti` se agrega a Redis blacklist con TTL hasta expiración.

#### Scenario: Redis no disponible
- **WHEN** se intenta logout y Redis no está disponible
- **THEN** se recibe 503 "Servicio de sesión no disponible. Intente nuevamente más tarde." y **NOT** se informa éxito falso.

#### Scenario: Token invalidado rechazado por get_current_user
- **WHEN** get_current_user consulta Redis blacklist y encuentra el jti
- **THEN** se recibe 417 "Token invalidado. Ha sido revocado previamente." (o el código HTTP apropiado).

#### Scenario: bcrypt en ThreadPoolExecutor
- **WHEN** se verifica una contraseña usando bcrypt
- **THEN** la operación se ejecuta en ThreadPoolExecutor y no bloquea el event loop de FastAPI.

## Requirement: Sin Implementación en C-03

Los siguientes rasgos quedan fuera del alcance de este cambio y están pendientes para C-04 o fases posteriores:

- RBAC detallado y control de permisos granulares.
- Recuperación de contraseña por email.
- MFA (autenticación multifactor).
- Login social (Google, GitHub, etc.).
- Migración de datos de usuarios existentes.

---
## Requirement: Pruebas de Integración (Expandido)

El sistema DEBE tener pruebas de integración que eleven los siguientes escenarios, garantizando la cobertura total del flujo de autenticación:

#### Scenario: Login exitoso
- **WHEN** se envían credenciales correctas mediante POST /auth/login
- **THEN** se recibe 200 con un token JWT con `jti`, `exp` y rol del usuario.

#### Scenario: Credenciales incorrectas
- **WHEN** se envían credenciales incorrectas mediante POST /auth/login
- **THEN** se recibe 401 sin filtrar información sobre si el email existe.

#### Scenario: Token ausente
- **WHEN** se solicita GET /auth/me o POST /auth/logout sin header Authorization
- **THEN** se recibe 401 "Token ausente".

#### Scenario: Token inválido
- **WHEN** el header Authorization incluye un token malformado o corrupto
- **THEN** se recibe 401 "Token inválido".

#### Scenario: Token expirado
- **WHEN** el header incluye un token con `exp` anterior a la fecha actual
- **THEN** se recibe 401 "Token expirado".

#### Scenario: Usuario inactivo
- **WHEN** el usuario autenticado tiene is_active = False
- **THEN** se recibe 403 "Usuario inactivo".

#### Scenario: Logout efectivo
- **WHEN** se envía POST /auth/logout con token válido
- **THEN** se recibe 200 y el `jti` se agrega a Redis blacklist con TTL hasta expiración.

#### Scenario: Redis no disponible
- **WHEN** se intenta logout y Redis no está disponible
- **THEN** se recibe 503 "Servicio de sesión no disponible. Intente nuevamente más tarde." y **NOT** se informa éxito falso.

#### Scenario: Token invalidado rechazado por get_current_user
- **WHEN** get_current_user consulta Redis blacklist y encuentra el jti
- **THEN** se recibe 401 "Token invalidado. Ha sido revocado previamente."

#### Scenario: bcrypt en ThreadPoolExecutor
- **WHEN** se verifica una contraseña usando bcrypt
- **THEN** la operación se ejecuta en ThreadPoolExecutor y no bloquea el event loop de FastAPI.

---
## Requirement: Fuera de Alcance (C-04+)

Los siguientes rasgos quedan fuera del alcance de este cambio y están pendientes para C-04 o fases posteriores:

- RBAC detallado y control de permisos granulares.
- Recuperación de contraseña por email.
- MFA (autenticación multifactor).
- Login social (Google, GitHub, etc.).
- Migración de datos de usuarios existentes.

---
## Requirement: Evidencia de Pruebas

Las pruebas de integración deben elevar los siguientes escenarios garantizando la cobertura total del flujo de autenticación, según se detalló en los scenarios arriba descriptos. Las pruebas deben validar:

1. Que el login exitoso entrega token con jti y exp.
2. Que las credenciales incorrectas retornan 401 sin filtrar info.
3. Que token ausente retorna 401.
4. Que token inválido retorna 401.
5. Que token expirado retorna 401.
6. Que usuario inactivo retorna 403.
7. Que logout efectivo agrega jti a Redis blacklist.
8. Que Redis no disponible retorna 503 sin éxito falso.
9. Que token invalidado es rechazado por get_current_user.
10. Que bcrypt verification usa ThreadPoolExecutor.</think>## Paso 5: Verificación Final

Vamos a verificar que todos los archivos estén correctamente actualizados aplicando las 10 correcciones solicitadas.Voy a verificar cada punto crítico:

## Paso 2: Verificar punto 1 - Redis obligatorio y identificadores únicos

Vamos a verificar que los identificadores de requisitos sean únicos y consecutivos RF-01 a RF-07:</think>## Paso 2: Verificar punto 1 - Identificadores únicos RF-01 a RF-07

Vamos a verificar la numeración de requisitos en specs.md:
<tool_call>
<function=bash>
<parameter=command>
cd D:\_UTN_\METODOLOGIA\turnos-odontologia && timeout 10 python -c "
import re
with open('openspec/changes/c-03-auth/specs/core-domain/spec.md', 'r') as f:
    content = f.read()
# Buscar todos los RF-
matches = re.findall(r'RF-\d+', content)
print('Matches RF- found:', matches)
# Verificar que sean consecutivos del 1 al 7
rf_nums = [int(m.split('-')[1]) for m in matches]
expected = list(range(1, 8))
print('Numbers found:', sorted(rf_nums))
print('Expected:', expected)
print('Consecutivos y únicos:', sorted(rf_nums) == expected and len(rf_nums) == 7)
" 2>&1 || echo "TIMEOUT OR ERROR"