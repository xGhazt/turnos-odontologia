## Context

Ver `proposal.md` para la motivación. El repositorio no tiene código de aplicación; este change introduce el primer código ejecutable. Las especificaciones de comportamiento están en `specs/platform-foundation/spec.md`.

Restricciones vigentes:
- Stack fijado en `knowledge-base/02_descripcion_general.md` y `openspec/config.yaml`: Python + FastAPI, SQLAlchemy + Alembic, PostgreSQL, Redis, Docker Compose.
- Arquitectura objetivo: monolito modular en capas (routers → services → repositories → models), ver `knowledge-base/08_arquitectura_propuesta.md`.
- Reglas duras: sin datos reales de personas; sin secretos/credenciales en el repo.

## Goals / Non-Goals

**Goals:**
- Dejar un esqueleto de backend ejecutable y testeable localmente **sin** depender de Docker encendido (tests con SQLite in-memory).
- Definir el contrato de salud (liveness/readiness) y la configuración por entorno como base reutilizable por los módulos posteriores.
- Preparar Alembic (async) para que `C-02` solo agregue su migración.

**Non-Goals:**
- Modelos de dominio, migraciones de negocio, autenticación y endpoints funcionales (pertenecen a `C-02`+).
- Frontend y su servicio en Compose (diferidos).
- Observabilidad avanzada (métricas, tracing) y CI/CD.

## Decisions

1. **Estructura en capas bajo `backend/app/`**
   - `api/` (routers), `core/` (settings, logging, dependencias), `models/`, `schemas/`, `services/`, `repositories/`, `main.py`.
   - *Alternativa*: estructura plana. Se descarta para no reescribir cuando lleguen los módulos de dominio y por trazabilidad con KB-08.

2. **Acceso a datos asíncrono: SQLAlchemy async + `asyncpg`**
   - Motor `create_async_engine`. *Alternativa*: driver síncrono `psycopg` con adaptadores: descartado por coherencia con el stack async de FastAPI (el usuario confirmó asyncpg).
   - Para tests, `aiosqlite` (SQLite in-memory). *Alternativa*: Testcontainers/Postgres: descartado por requerir Docker en cada corrida.

3. **Salud separada: liveness vs readiness**
   - `GET /api/health`: liveness puro (no toca dependencias) → estable para orquestadores.
   - `GET /api/health/ready`: readiness que chequea Postgres (SELECT 1) y Redis (PING); `503 degraded` si falla alguna.
   - *Alternativa*: un solo `/health` con checks: descartado porque un fallo de DB reiniciaría el contenedor innecesariamente.

4. **Configuración con `pydantic-settings` (fail-fast)**
   - Clase `Settings` que valida variables requeridas (`DATABASE_URL`, `REDIS_URL`, `CORS_ORIGINS`, etc.) al importar/arrancar.
   - *Alternativa*: leer `os.environ` a mano: descartado, sin validación ni tipado.
   - Los secretos se inyectan por entorno; `.env.example` solo documenta claves sin valores reales.

5. **CORS con lista configurable**
   - `CORSMiddleware` con `allow_origins` tomado de settings (por defecto `http://localhost:5173`).
   - *Alternativa*: `allow_origins=["*"]`: descartado por seguridad.

6. **Logging estructurado con `logging` estándar**
   - Formatter JSON propio sobre `logging`. *Alternativa*: `structlog`: descartado (dependencia extra innecesaria para el alcance).

7. **Alembic async preconfigurado, sin migraciones**
   - `alembic init -t async`; `env.py` apuntando a `Base.metadata`. Sin tablas todavía.

8. **Compose con healthchecks**
   - `db` (postgres:16) y `redis` (redis:7) con healthcheck; `backend` depende de ambos con `condition: service_healthy`; volumen persistente para Postgres. Sin servicio frontend.

## Risks / Trade-offs

- **Readiness en tests sin DB/Redis reales** → los tests usan *dependency overrides*/mocks de los checks; se prueba el branch de éxito y el de falla sin infraestructura.
- **Alembic async mal configurado** → se valida generando el árbol y verificando que `env.py` importa `Base` sin error.
- **Diferencias SQLite vs Postgres en tests** → aceptable porque `C-01` no define tablas; cuando aparezcan (C-02), los tests de constraints podrán requerir Postgres (se decidirá entonces).
- **CORS configurado sin frontend** → riesgo de origen mal fijado; se deja parametrizable y documentado en `.env.example`.

## Migration Plan

Proyecto nuevo: no hay migración de datos. Despliegue local con `docker compose up`. Rollback = eliminar `backend/`, `docker-compose.yml` y los `.env.example` (no afecta documentación previa). Alembic queda inicializado pero sin revisiones.

## Open Questions

- Nombres exactos de variables y valores por defecto de puertos (`APP_PORT`, `POSTGRES_PORT`) — diferible, no cambia specs ni tareas.
- Si más adelante se quiere readiness con timeout/retry configurable — diferible a un change de hardening.
