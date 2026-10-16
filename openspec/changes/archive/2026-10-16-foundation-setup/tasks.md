## 1. Estructura y dependencias del backend

- [x] 1.1 Crear el árbol `backend/app/{api,core,models,schemas,services,repositories}` con `__init__.py` en cada paquete y `backend/tests/`
- [x] 1.2 Crear `backend/requirements.txt` con `fastapi`, `uvicorn[standard]`, `pydantic-settings`, `SQLAlchemy[asyncio]`, `asyncpg`, `alembic`, `redis`, `pytest`, `pytest-asyncio`, `httpx`, `aiosqlite`
- [x] 1.3 Crear y activar un venv local en `backend/.venv` e instalar las dependencias
- [x] 1.4 Crear `.env.example` en la raíz y en `backend/` (sin valores reales), documentando `DATABASE_URL`, `REDIS_URL`, `CORS_ORIGINS` y puertos
- [x] 1.5 Ampliar `.gitignore` con artefactos Python (`.venv/`, `__pycache__/`, `.pytest_cache/`)

## 2. Núcleo (core)

- [x] 2.1 Implementar `core/settings.py` con `pydantic-settings` (tipado estricto, validación fail-fast de variables requeridas)
- [x] 2.2 Implementar `core/logging.py` con formatter JSON sobre el módulo `logging` estándar y función de setup
- [x] 2.3 Implementar `core/db.py` con `create_async_engine` y factory de sesión async
- [x] 2.4 Implementar `core/cache.py` con cliente Redis async (conexión desde settings)

## 3. Aplicación y endpoints de salud

- [x] 3.1 Implementar `main.py` con app factory FastAPI, setup de logging y `CORSMiddleware` con orígenes desde settings
- [x] 3.2 Implementar router de salud en `api/health.py`: `GET /api/health` (liveness)
- [x] 3.3 Implementar `GET /api/health/ready` con chequeos de Postgres (SELECT 1) y Redis (PING) y respuesta `200/503`

## 4. Alembic (async)

- [x] 4.1 Inicializar Alembic en modo async (`alembic init -t async alembic`) dentro de `backend/`
- [x] 4.2 Configurar `alembic/env.py` para leer `DATABASE_URL` de settings e importar `Base.metadata`

## 5. Docker e infraestructura

- [x] 5.1 Crear `Dockerfile` del backend (imagen Python, install de requirements, comando uvicorn)
- [x] 5.2 Crear `docker-compose.yml` con servicios `backend`, `db` (postgres:16) y `redis` (redis:7), healthchecks, `depends_on: service_healthy` y volumen persistente

## 6. Tests

- [x] 6.1 Configurar `pytest` (`pytest.ini`/`pyproject`) + `conftest.py` con `httpx.AsyncClient` y overrides de dependencias
- [x] 6.2 Test de liveness: `GET /api/health` → `200 {"status":"ok"}` y ruta inexistente → `404`
- [x] 6.3 Test de Settings: configuración válida; `DATABASE_URL` ausente → error que la menciona; valor inválido de tipo → error de validación
- [x] 6.4 Test de CORS: preflight desde `http://localhost:5173` incluye `Access-Control-Allow-Origin`; origen no autorizado no la incluye
- [x] 6.5 Test de readiness: ambas dependencias OK → `200`; Redis caído → `503 degraded`

## 7. Verificación

- [x] 7.1 Correr `pytest` y verificar que todos los escenarios del spec pasan
- [x] 7.2 Validar `docker compose config` y (si hay Docker) levantar `docker compose up` y verificar `/api/health` y `/api/health/ready` con `curl`
