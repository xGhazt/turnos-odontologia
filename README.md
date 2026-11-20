# Turnos Odontología — Sistema de Gestión de Turnos y Agenda

**Metodología I — TUP UTN** | Grupo: Gastón Puente, Giovanna Suarez

---

## 📦 Stack Tecnológico
- **Frontend:** React 18 + TypeScript + Vite 5 + Tailwind CSS (diferido a C-04)
- **Backend:** Python 3.11+ + FastAPI 0.111 + SQLAlchemy 2.0 (async) + Alembic + Pydantic v2
- **BD / Cola:** PostgreSQL 16 + Redis 7
- **Infra:** Docker / Docker Compose
- **Metodología:** Spec-Driven Development (OpenSpec) + Active Stack

---

## 🚀 Puesta en marcha rápida

### Prerrequisitos
- Docker 24+ y Docker Compose v2
- Python 3.11+ (para pruebas locales sin Docker)

### Con Docker (recomendado)
```bash
cp .env.example .env   # Editar variables si es necesario
docker compose up --build
```
- Backend API: http://localhost:8000
- Health liveness: `GET /api/health` → `{"status":"ok"}`
- Health readiness: `GET /api/health/ready` → `200` si Postgres y Redis responden, `503` si alguno falla.

### Tests locales (sin Docker)
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -v
```
> No hace falta crear un `.env` para los tests: `tests/conftest.py` define las variables por defecto y usa **SQLite in-memory**.
> **10 tests automatizados** cubren: liveness, readiness (OK / degraded), settings fail-fast y CORS.

---

## 📁 Estructura del Repositorio
```
turnos-odontologia/
├── backend/              # API FastAPI (Change C-01 implementado)
├── docs/
│   ├── discovery/        # Informe de Discovery + verificación de fuentes + PDF
│   └── evidencias/       # Capturas de ejecución de etapas
├── knowledge-base/       # 10 archivos canónicos (fuente de verdad del dominio)
├── openspec/             # Especificaciones, config y changes archivados
├── CHANGES.md            # Roadmap operativo (13 changes / 7 fases)
├── AGENTS.md / CLAUDE.md # Instrucciones y reglas duras para agentes IA
├── docker-compose.yml    # Orquestación de servicios (backend, db, redis)
└── .env.example          # Variables de entorno canónicas
```

---

## 📋 Roadmap — Estado Actual
| Change | Nombre | Estado |
|--------|--------|--------|
| **C-01** | `foundation-setup` | ✅ Completado y archivado |
| C-02 | `core-models` | ⬜ Pendiente |
| C-03 | `auth-system` | ⬜ Pendiente |
| ... | ... | ⬜ Pendiente |
| **Camino crítico** | `C-01 → C-02 → C-03 → C-05 → C-07 → C-08 → C-11` | |

Ver `CHANGES.md` para el detalle completo, dependencias y punteros de lectura.

---

- [x] Discovery y verificación de fuentes (`docs/discovery/`)
- [x] Knowledge Base (`knowledge-base/`)
- [x] Roadmap (`CHANGES.md`)
- [x] Skills y registro (`.atl/skill-registry.md`, `AGENTS.md`)
- [x] Ciclo OPSX C-01 (`openspec/changes/archive/2026-10-16-foundation-setup/`)
- [x] README.md (este archivo)
- [x] Informe Discovery en PDF (`docs/discovery/informe-discovery.pdf`)
- [x] Reflexión escrita (`docs/conclusion met.pdf`)

---

## 🔒 Reglas Duras del Proyecto
- **Datos 100% ficticios** (RN-06) — prohibido almacenar datos reales de pacientes.
- **Sin secretos en el repo** — usar `.env` (en `.gitignore`) y versionar `.env.example`.
- **Validación estricta** — tipado estricto en Python/TS y rechazo de campos no declarados.
- **Español rioplatense** (voseo) en documentación y especificaciones.


