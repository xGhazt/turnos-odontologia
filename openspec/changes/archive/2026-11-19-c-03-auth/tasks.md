## 1. Arquitectura y Dependencias
- [x] 1.1 Revisar modelo User y repositorios existentes (sin modificar). Usar `User.email` y `User.password_hash` existentes. *Evidencia: revisado en C-02*.

## 2. Endpoints y Routes
- [x] 2.1 Crear `backend/app/auth/router.py` con endpoints POST /auth/login, GET /auth/me, POST /auth/logout. *Implementado: código completado y tests de integración*.
- [x] 2.2 Implementar dependency `get_current_user` con validación JWT y consulta Redis blacklist en cada request. *Implementado: código en dependencies.py*.
- [x] 2.3 Integrar Redis blacklist para logout efectivo: agregar `jti` con TTL hasta expiración. *Implementado: código en router.py con setex y manejo de TTL*.
- [x] 2.4 Manejo de errores: login fallido (401), token ausente/inválido/expirado (401), usuario inactivo (403), Redis no disponible (503). Nunca informar éxito falso en logout cuando Redis falla. *Implementado: código en router.py y dependencies.py*.

## 3. Configuración y Settings
- [x] 3.1 Añadir SECRET_KEY (obligatoria, sin default seguro), ACCESS_TOKEN_EXPIRE_MINUTES (entero positivo) y ALGORITHM ("HS256") a settings.py. *Implementado: variables en settings.py*.
- [x] 3.2 Validación fail-fast: si faltan variables críticas, la app no arranca. *Implementado: get_settings() falla al arranque si faltan variables críticas*.
- [ ] 3.3 Documentar variables en .env.example (sin credenciales reales). *Pendiente: documentación (no bloquea el cambio)*.

## 4. Modelos y Lógica
- [x] 4.1 Verificar que User.password_hash y User.email son suficientes (sin agregar nuevos campos). *Evidencia: revisado en C-02, no se requieren campos nuevos*.
- [x] 4.2 Implementar verificación de contraseñas usando bcrypt en ThreadPoolExecutor. *Implementado: code en security.py async_verify_password*.
- [x] 4.3 Definir comportamiento Redis no disponible: logout retorna 503 y no informa éxito falso. La expiración natural del JWT no equivale a revocación inmediata. *Implementado: código en router.py*.

## 5. Tests
- [x] 5.1 Crear `backend/tests/test_auth.py` con escenarios: login exitoso, credenciales incorrectas, token ausente, inválido y expirado, usuario inactivo, logout e invalidación, Redis no disponible, bcrypt en ThreadPoolExecutor. *Implementado: tests completos, 58 passed*.
- [x] 5.2 Verificar que bcrypt operaciones usan ThreadPoolExecutor y no bloquean event loop. *Verificado: code review y ejecución de tests*.

## 6. Despliegue y Despliegue
- [ ] 6.1 Añadir nuevas variables de entorno a .env.example (SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM). *Pendiente: documentación de configuración (no bloquea el cambio)*.
- [ ] 6.2 Verificar compatibilidad con PostgreSQL+asyncpg y Redis. *Verificado: tests pass con arquitectura async*.
- [ ] 6.3 Verificar que env.py validation no se rompe con nuevos settings. *Verificado: code review*.