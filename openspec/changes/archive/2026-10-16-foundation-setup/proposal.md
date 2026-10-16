## Why

El repositorio contiene hoy únicamente documentación (knowledge-base, Discovery, roadmap) y **no tiene código de aplicación**: sin cimientos no se puede implementar ningún change funcional del roadmap. Este change crea la base ejecutable del backend y la infraestructura de desarrollo, habilitando todos los changes posteriores (el camino crítico arranca en `C-01`).

**Justificación de la elección (Etapa 6):** se elige `C-01` porque es el primer change del roadmap, es atómico y sin dependencias, y pertenece al MVP. Se recorta su alcance a **backend-only** porque el PDF (Etapa 6.2) autoriza implementar solo una API o módulo de dominio, sin interfaz gráfica.

## What Changes

- **Scaffolding del backend** `backend/` con estructura en capas (routers → services → repositories → models) según `knowledge-base/08_arquitectura_propuesta.md`.
- **Aplicación FastAPI** con:
  - `GET /api/health` (liveness) → `{"status": "ok"}`.
  - `GET /api/health/ready` (readiness) → verifica conexión a PostgreSQL y Redis; `503` si alguna dependencia está caída.
  - **Pydantic Settings** que carga y valida `.env` (arranque *fail-fast* si falta configuración requerida).
  - **CORS** configurado para el origen de Vite (`http://localhost:5173`).
  - **Logging estructurado** con el módulo `logging` estándar de Python (formato JSON).
- **Alembic** inicializado en modo **asíncrono** (`alembic init -t async`), sin migraciones de dominio todavía (la migración 001 pertenece a `C-02`).
- **`docker-compose.yml`** con servicios `backend`, `db` (PostgreSQL 16) y `redis` (Redis 7), con `healthcheck`s y volumen persistente.
- **`.env.example`** en la raíz y en `backend/` (sin secretos reales).
- **Tests** con `pytest`: liveness, validación de Settings, CORS y readiness.
- Ajustes a `.gitignore` para artefactos Python (`.venv/`, `__pycache__/`, `.pytest_cache/`).

### Fuera de alcance (diferido)
- Scaffold del **frontend** (React + Vite + Tailwind + React Router + cliente HTTP) y su servicio en `docker-compose`.
- Migraciones de dominio, modelos de negocio, autenticación y cualquier endpoint funcional (pertenecen a `C-02`+).

## Capabilities

### New Capabilities
- `platform-foundation`: comportamiento verificable de los cimientos backend: endpoint de liveness, endpoint de readiness con dependencias, carga/validación de configuración por entorno y política de CORS para el cliente web.

### Modified Capabilities
<!-- Sin changes previos; no hay capabilities existentes que modificar. -->

## Impact

- **Código nuevo**: `backend/` (app FastAPI, `core/settings.py`, `core/logging.py`, `api/` con health, `alembic/`, `tests/`), `docker-compose.yml`, `.env.example` (raíz y backend).
- **Dependencias nuevas** (backend): `fastapi`, `uvicorn[standard]`, `pydantic-settings`, `SQLAlchemy[asyncio]`, `asyncpg`, `aiosqlite` (tests), `alembic`, `redis`, `pytest`, `pytest-asyncio`, `httpx`.
- **Infraestructura**: Docker Compose (backend, PostgreSQL 16, Redis 7).
- **Sistemas afectados**: habilita la cadena crítica (`C-01 → C-02 → C-03 → …`); no rompe nada existente (repo sin código).
- **No afecta** documentación ni specs existentes (no había).
