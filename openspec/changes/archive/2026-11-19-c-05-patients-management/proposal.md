# Proposal

## Why

El sistema necesita un padrón de pacientes completo y validado para soportar la reserva de turnos (C-07) y la gestión clínica (C-10). La regla de negocio **RN-04** exige identificación única por DNI, y la **RN-06** prohíbe datos reales de pacientes. Este change implementa el modelo, API REST y validaciones estrictas para el CRUD de pacientes, desbloqueando las funcionalidades F-04 (Gestión de Pacientes) y F-05 (Historia Clínica) de la Épica 2.

## What Changes

- Nuevo modelo SQLAlchemy `Patient` con campos: nombres, apellidos, DNI (único), teléfono, email, fecha de nacimiento, obra social/prepaga, número de afiliado, antecedentes médicos, más campos de auditoría heredados
- Migración Alembic 002: tabla `patients` con índice único sobre `dni`
- Endpoints REST en `app/api/v1/patients.py`:
  - `GET /api/v1/patients` — listado paginado con búsqueda por DNI, apellido o nombre
  - `POST /api/v1/patients` — alta de nuevo paciente con validación de DNI duplicado (409 Conflict)
  - `GET /api/v1/patients/{id}` — detalle completo de ficha del paciente
  - `PUT /api/v1/patients/{id}` — modificación de datos de contacto y cobertura médica
- Esquemas Pydantic para request/response con validación estricta
- Repositorio `PatientRepository` heredando de `BaseRepository`
- Tests: creación exitosa, error 409 por DNI duplicado, paginación y búsqueda por término parcial
- Datos 100% ficticios en seeds y tests (RN-06)

## Capabilities

### New Capabilities

- `patients-management`: Gestión integral del padrón de pacientes — modelo, validaciones de negocio (DNI único), API REST CRUD, búsqueda y paginación. Esta capability cubre la entidad Patient y sus operaciones, y servirá como base para C-07 (appointments-engine), C-10 (clinical-records-odontogram) y C-13 (cash-register-dashboard).

### Modified Capabilities

- `core-domain`: Se extiende la capacidad "Entidades de Dominio Base" para incluir la entidad Patient con su restricción de DNI único. Esto requiere actualizar el spec existente con la nueva entidad y su regla de unicidad.

## Impact

**Código afectado:**
- `backend/app/models/` — nuevo `Patient.py` y actualización de `__init__.py`
- `backend/app/schemas/` — nuevos esquemas Pydantic para Patient
- `backend/app/repositories/` — nuevo `PatientRepository.py`
- `backend/app/api/v1/` — nuevo `patients.py` router
- `backend/alembic/versions/` — migración 002
- `backend/tests/` — nuevos tests de integración y unidad

**APIs nuevas:**
- `GET /api/v1/patients`
- `POST /api/v1/patients`
- `GET /api/v1/patients/{id}`
- `PUT /api/v1/patients/{id}`

**Dependencias:**
- Requiere C-03 (auth-system) completado para autenticación y autorización RBAC
- Desbloquea C-07 (appointments-engine) y C-10 (clinical-records-odontogram)

**Base de datos:**
- Nueva tabla `patients` con índice único en `dni`