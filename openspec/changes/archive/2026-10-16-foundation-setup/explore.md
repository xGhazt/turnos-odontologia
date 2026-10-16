# Explore — foundation-setup (C-01)

> Relevamiento previo a proponer. Fase **Explore** de la Etapa 6 (ciclo OPSX).
> Fecha: 2026-10-16

## 1. Problema

El repositorio contiene únicamente **documentación** (knowledge-base, Discovery, CHANGES.md, skills). **No existe código de aplicación** (`backend/` y `frontend/` no existen). Sin cimientos no se puede implementar ningún change funcional.

## 2. Estado actual del repositorio

```
turnos-odontologia/
├── knowledge-base/          ✅ 10 docs canónicos + README
├── docs/discovery/          ✅ informe + verificación de fuentes
├── CHANGES.md               ✅ 13 changes (untracked, lo commitea Giovanna)
├── AGENTS.md / CLAUDE.md    ✅ instrucciones de agentes
├── .atl/skill-registry.md   ✅ registry de skills
├── .agents/skills/          ✅ skills locales (fastapi, react, async-python, etc.)
├── openspec/
│   ├── config.yaml          ✅ contexto del proyecto (stack, reglas duras)
│   ├── changes/             ⬜ vacío → ahora foundation-setup/
│   └── specs/               ⬜ vacío
├── backend/                 ❌ NO EXISTE
└── frontend/                ❌ NO EXISTE
```

Herramientas verificadas: `go`, `git`, `node v22.16.0`, `npm 10.9.2`, `opencode`, `openspec 1.9.0`.

## 3. Change elegido: C-01 `foundation-setup`

- **Governance**: BAJO. **Dependencias**: ninguna.
- Primer change del roadmap y de la cadena crítica (`C-01 → C-02 → …`).

### Alcance original (CHANGES.md)
Backend (FastAPI + health + Settings + CORS + Alembic) **+** Frontend (React/Vite/Tailwind/Router/HTTP) **+** docker-compose (4 servicios).

### Recorte declarado para la Etapa 6
El PDF (Etapa 6.2) autoriza implementar **solo el backend** ("puede ser una API o un módulo con su lógica de dominio, no hace falta interfaz gráfica"). Por indicación del profesor/cátedra se hace **únicamente el primer change**, **backend-only**:

- **En alcance**: `backend/` (FastAPI, `/api/health` + `/health/ready`, Pydantic Settings, CORS para Vite, logging estructurado, Alembic async), `docker-compose.yml` (backend + Postgres 16 + Redis 7), `.env.example` (raíz + backend), tests.
- **Fuera de alcance (diferido)**: scaffold `frontend/`, servicio frontend en compose, `.env.example` de frontend.

## 4. Decisiones técnicas (confirmadas por el usuario)

| Tema | Decisión |
|------|----------|
| Capability (specs) | `platform-foundation` |
| ORM/DB driver | SQLAlchemy **async** + **asyncpg** |
| Logging | `logging` estándar de Python con formato estructurado |
| DB en tests | **SQLite in-memory** (`aiosqlite`); Postgres solo en runtime vía Docker |
| Frontend | **Diferido** (no se implementa ahora) |
| Escenarios | 3 obligatorios (feliz/error/borde) **+** readiness DB/Redis |

## 5. Riesgos y unknowns

- **Healthcheck vs readiness**: el scope dice `GET /api/health → {"status":"ok"}` simple; se agrega `/api/health/ready` para cubrir dependencias sin contaminar el liveness.
- **Alembic async**: requiere plantilla async (`alembic init -t async`).
- **CORS sin frontend**: se configura igual (origen `http://localhost:5173`) para no bloquear C-04.
- **Red/disponibilidad**: la instalación de dependencias (`pip`, `npm`) requiere red.

## 6. Criterio de terminado (para Verify)

- `pytest` en verde: healthcheck, validación de Settings, CORS y readiness.
- Script/health de conexión a DB y Redis documentado.
- `docker-compose config` válido (sin necesidad de levantar contenedores).
