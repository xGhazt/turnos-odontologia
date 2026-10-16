# Verify — foundation-setup (C-01)

> Fase **Verify** de la Etapa 6. Resultados de la verificación del change.

## 1. Tests automatizados (`pytest`)

Comando: `backend/.venv/bin/pytest -v` (desde `backend/`)

Resultado: **10 passed** en 0.25s.

| Escenario del spec | Test |
|--------------------|------|
| Liveness → `200 {"status":"ok"}` | `test_health.py::test_liveness_returns_ok` |
| Ruta inexistente → `404` | `test_health.py::test_unknown_route_returns_404` |
| Readiness con dependencias OK → `200` | `test_readiness.py::test_readiness_all_dependencies_ok` |
| Readiness con Redis caído → `503 degraded` | `test_readiness.py::test_readiness_degraded_when_redis_down` |
| Readiness con todo caído → `503 degraded` | `test_readiness.py::test_readiness_degraded_when_all_down` |
| Config válida | `test_settings.py::test_valid_configuration` |
| `DATABASE_URL` ausente → error | `test_settings.py::test_missing_database_url_raises` |
| Valor inválido de tipo → error | `test_settings.py::test_invalid_port_type_raises` |
| CORS origen permitido | `test_cors.py::test_cors_preflight_from_allowed_origin` |
| CORS origen no autorizado | `test_cors.py::test_cors_preflight_from_disallowed_origin` |

## 2. Smoke test de la aplicación (uvicorn, sin Docker)

```
GET /api/health        → HTTP 200  {"status":"ok"}
GET /api/health/ready  → HTTP 503  {"status":"degraded","dependencies":{"database":"ok","redis":"unavailable"}}
```

El `503` es el comportamiento esperado: Redis no estaba corriendo y no hay dependencias en este test.

## 3. Alembic

`alembic history` ejecuta `env.py` (que importa `Settings` y `Base.metadata`) **sin errores**. Sin revisiones todavía (la migración 001 pertenece a `C-02`).

## 4. Docker Compose

`docker compose config` → **válido** (servicios `backend`, `db`, `redis` con healthchecks y volumen).

## 5. Conclusión

Todos los escenarios del spec quedan cubiertos por tests en verde. **No hay nada en rojo.** Listo para Archive.
