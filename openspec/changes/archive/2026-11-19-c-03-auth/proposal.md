## Why

El sistema requiere un sistema de autenticación y autorización para soportar las funcionalidades siguientes de acceso a recursos protegidos. Sin autenticación, no se pueden asegurar los recursos de los usuarios y no se puede implementar el patrón de Repository con control de acceso.

## What Changes

- Implementación de autenticación JWT (JSON Web Tokens) para el sistema.
- Endpoints de login, verificación de usuario y logout.
- Integración con el sistema de sesiones Redis para blacklist de tokens.
- Protección de endpoints mediante dependency `get_current_user`.
- Contraseñas verificadas usando bcrypt de forma asíncrona (ThreadPoolExecutor).

## Capabilities

### New Capabilities

- **Autenticación**: Login de usuarios con generación de JWT y jti en Redis blacklist.
- **Sesión**: Gestión de tokens en Redis blacklist con TTL hasta expiración natural.
- **Protección**: Endpoints seguros con validación de token y consulta Redis en cada request.
- **Verificación**: Contraseñas verificadas usando bcrypt en ThreadPoolExecutor para no bloquear el event loop.

### Modified Capabilities

- (ninguna)

## Impact

- **Seguridad**: Implementación de autenticación segura para el sistema con invalidación de tokens.
- **API**: Nuevos endpoints `/auth/login`, `/auth/me`, `/auth/logout`.
- **Base de datos**: Sin cambios estructurales en las tablas existentes (reutilizar `User.password_hash` y `User.email`).
- **Redis**: Obligatorio para blacklist de tokens (no opcional). Sin Redis, logout retorna 503.

## Impacted Files

- `backend/app/auth/`: Nuevos módulos de autenticación.
- `backend/app/core/settings.py`: Nuevas variables de configuración (SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM).
- `backend/app/main.py`: Middleware de inyección de dependencias y validación Redis.
- `backend/app/models/user.py`: Campos existentes (email, password_hash) - sin agregar nuevos campos.
- `backend/tests/test_auth.py`: Tests de integración con escenarios completos.

## Non-Goals

- RBAC detallado y control de permisos granulares (corresponde a C-04 o fases posteriores).
- Recuperación de contraseña por email.
- MFA (autenticación multifactor).
- Login social (Google, GitHub, etc.).
- Migración de datos de usuarios existentes.