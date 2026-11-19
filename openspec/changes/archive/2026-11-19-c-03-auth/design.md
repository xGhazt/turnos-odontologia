## Goals / Non-Goals

### Goals
- Implementar autenticación JWT sobre los modelos y repositorios existentes.
- Proveer endpoints `/auth/login`, `/auth/me`, `/auth/logout`.
- Integrarse con Redis para blacklist de tokens (obligatoria).
- Verificar contraseñas usando bcrypt en ThreadPoolExecutor (no bloquear event loop).
- Aprovechar la configuración existente de `settings.py`.

### Non-Goals
- Implementar RBAC detallado (corresponde a C-04).
- Recuperación de contraseña por email.
- MFA o login social.
- Nuevos campos en el modelo User (usar `email` y `password_hash` existentes).

### Risks / Trade-offs

- **[Riesgo] Contraseñas async**: bcrypt es síncrono por naturaleza. La solución es ejecutar la verificación en un `ThreadPoolExecutor` inyectado por FastAPI, manteniendo el event loop libre.
- **[Riesgo] Redis obligatorio**: Si Redis cae, logout retorna 503 y no invalida el token. Mitigación: fallback a expiración natural del JWT, pero la invalidación inmediata falla.
- **[Riesgo] Configuración**: Falta `SECRET_KEY` en .env. Mitigación: `fastapi.security.HTTPBearer` con validación estricta y fallo en arranque si falta.

## Technical Design

### 1. JWT Authentication Flow
- `POST /auth/login`: Recibe `email` + `password`, verifica contra BD usando bcrypt (ThreadPoolExecutor), genera JWT con `jti` (ID único) y `exp`, agrega `jti` a Redis blacklist con TTL igual a la vida del token.
- `GET /auth/me`: Consulta Redis blacklist primero; si `jti` está blacklistado, retorna 401. Si no, consulta BD por usuario y retorna datos.
- `POST /auth/logout`: Agrega `jti` a Redis blacklist con TTL igual a lo que queda de vida del token. Si Redis falla, retorna 503 y no informa éxito.

### 2. Password Verification (async)
- Usar `fastapi.concurrency.run_in_threadpool` para ejecutar `bcrypt.checkpw()`.
- Esto mantiene el event loop libre mientras se verifica la contraseña.
- No se debe usar bcrypt de forma síncrona directa en handlers async.

### 3. Settings Configuration
- `SECRET_KEY`: Obligatorio, sin default. `fastapi.security.HTTPBearer` falla al arranque si no está definido.
- `ALGORITHM`: Fijo en "HS256".
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Entero positivo > 0. Validado en `get_settings()` con fail-fast.
- `REDIS_URL`: Heredado de C-02, obligatorio para blacklist.

### 4. User Model Reuse
- `User.email`: Único, usado para login.
- `User.password_hash`: Almacenado con bcrypt (factor de trabajo configurable).
- Sin campos adicionales. La relación `User.role` trae el rol asociado.

### 5. get_current_user Dependency
1. Leer header `Authorization: Bearer <token>`
2. Decodificar JWT con `SECRET_KEY` y `ALGORITHM=HS256`.
3. Si falla → 401 "Token inválido o ausente".
4. Extraer `jti` del payload.
5. Consultar Redis blacklist: si `jti` está → retorna 401 "Token invalidado".
6. Consultar BD por usuario con `user.email`.
7. Si usuario es `None` → retorna 401 "Usuario no encontrado".
8. Si `usuario.is_active` es `False` → retorna 403 "Usuario inactivo".
9. Retorna objeto usuario con `id`, `email`, `rol`.

### 5. Error Responses Estándar
- 401: "Token ausente", "Token inválido", "Token expirado", "Usuario no encontrado", "Usuario inactivo", "Token invalidado"
- 403: "Usuario inactivo"
- 503: "Servicio de sesión no disponible" (solo logout cuando Redis cae)

## Trade-offs
- **Complejidad added**: Redis dependency para blacklist, pero permite invalidación inmediata vs expirar natural.
- **Performance**: ThreadPoolExecutor para bcrypt tiene costo menor vs bloquear todo el event loop.
- **Seguridad**: Invalidación inmediata vs expirar natural. Elegimos invalidación inmediata con Redis como requisito obligatorio.
"""