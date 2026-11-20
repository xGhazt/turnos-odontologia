# Design: C-05 Patients Management

## Overview

Implementation of the patient registry capability (`patients-management`) with full CRUD API, strict DNI uniqueness validation (RN-04), search/pagination, and audit/soft-delete support.

---

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| **Layered architecture** (router → service → repository → model) | Consistent with existing C-02/C-03 patterns; enables testing and separation of concerns |
| **Async SQLAlchemy 2.0** | Non-blocking I/O for high concurrency; aligns with FastAPI async patterns |
| **Pydantic v2 strict mode** | Enforces RN-06 (no real patient data) via schema validation; rejects extra fields |
| **BaseRepository inheritance** | Reuses proven CRUD + soft-delete logic from C-02; reduces boilerplate |
| **Unique index on `dni` at DB level** | Defense in depth: DB constraint enforces RN-04 even if app validation bypassed |
| **DNI immutable on UPDATE** | Business rule: DNI is identity, not editable contact info |
| **Partial search via ILIKE** | Case-insensitive partial match on DNI, apellido, nombre per spec scenarios |

---

## Data Model

### Patient Entity (`backend/app/models/Patient.py`)

```python
class Patient(Base, AuditMixin):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    dni: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(150), nullable=True)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    insurance_provider: Mapped[str | None] = mapped_column(String(100), nullable=True)
    insurance_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    medical_history: Mapped[str | None] = mapped_column(Text, nullable=True)
```

**Constraints:**
- `dni` — unique index (enforces RN-04)
- All string fields have max lengths per schema
- `birth_date` uses `Date` type (no timezone)
- `medical_history` uses `Text` for unbounded clinical notes

---

## Pydantic Schemas (`backend/app/schemas/patient.py`)

| Schema | Purpose | Key Validations |
|--------|---------|-----------------|
| `PatientBase` | Shared fields | `dni` regex `^\d{7,8}$` (AR DNI), `email` EmailStr, `phone` optional |
| `PatientCreate` | POST request | Inherits `PatientBase`; all required except optional contact/insurance |
| `PatientUpdate` | PUT request | All fields optional; **excludes `dni`** (immutable) |
| `PatientResponse` | GET response | Includes all fields + audit timestamps (`created_at`, `updated_at`) |
| `PatientListResponse` | Paginated list | `items: list[PatientResponse]`, `total`, `page`, `size`, `total_pages` |

**Strict mode:** `model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)`

---

## Repository (`backend/app/repositories/Patient.py`)

```python
class PatientRepository(BaseRepository[Patient]):
    async def get_by_dni(self, dni: str) -> Optional[Patient]:
        """Exact DNI lookup (for duplicate check)."""
    
    async def search(
        self,
        query: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Patient], int]:
        """
        Paginated search with ILIKE on dni, last_name, first_name.
        Returns (items, total_count).
        """
```

**Search logic:**
- If `query` provided: `WHERE (dni ILIKE %query% OR last_name ILIKE %query% OR first_name ILIKE %query%) AND is_active = true`
- Default ordering: `last_name, first_name`
- Pagination: `OFFSET (page-1)*size LIMIT size`

---

## Service Layer (`backend/app/services/patient.py`)

```python
class PatientService:
    def __init__(self, repo: PatientRepository): ...

    async def create(self, data: PatientCreate) -> Patient:
        # Check DNI uniqueness → repo.get_by_dni()
        # Raise ConflictException if exists
        # repo.create(**data.model_dump())

    async def get_by_id(self, patient_id: int) -> Patient:
        # repo.get_by_id() → raise NotFoundException if None or not active

    async def list(self, query: str | None, page: int, size: int) -> PatientListResponse:
        # repo.search() → map to PatientListResponse

    async def update(self, patient_id: int, data: PatientUpdate) -> Patient:
        # repo.get_by_id() → validate exists
        # repo.update() with data.model_dump(exclude_unset=True, exclude={"dni"})
```

**Exceptions:** Custom `ConflictException` (409), `NotFoundException` (404) mapped via FastAPI exception handlers.

---

## API Router (`backend/app/api/v1/patients.py`)

```python
router = APIRouter(prefix="/api/v1/patients", tags=["patients"])

@router.post("", response_model=PatientResponse, status_code=201)
async def create_patient(
    data: PatientCreate,
    service: PatientService = Depends(get_patient_service),
) -> PatientResponse: ...

@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: int,
    service: PatientService = Depends(get_patient_service),
) -> PatientResponse: ...

@router.get("", response_model=PatientListResponse)
async def list_patients(
    query: str | None = Query(None, description="Búsqueda por DNI, apellido o nombre"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    service: PatientService = Depends(get_patient_service),
) -> PatientListResponse: ...

@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int,
    data: PatientUpdate,
    service: PatientService = Depends(get_patient_service),
) -> PatientResponse: ...
```

**Dependencies:** `get_patient_service` provides `PatientService(PatientRepository(session))` with `session` from `get_session`.

---

## Alembic Migration (`backend/alembic/versions/XXX_patients_table.py`)

```python
def upgrade():
    op.create_table(
        "patients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("dni", sa.String(20), nullable=False),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("email", sa.String(150), nullable=True),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("insurance_provider", sa.String(100), nullable=True),
        sa.Column("insurance_number", sa.String(50), nullable=True),
        sa.Column("medical_history", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_patients_dni", "patients", ["dni"], unique=True)
    # Partial index not needed; dni is globally unique per RN-04
```

---

## Testing Strategy

| Test File | Coverage |
|-----------|----------|
| `tests/test_models.py` | Patient model creation, audit timestamps, soft delete |
| `tests/test_repositories.py` | `PatientRepository`: create, get_by_dni, search pagination, update, soft_delete |
| `tests/test_patients_api.py` | **Integration**: all 4 endpoints, 409 Conflict on duplicate DNI, 404 on missing, 422 validation, pagination edge cases |

**Test data:** 100% fictitious (RN-06) — generated via factory functions (e.g., `make_patient_data()`).

---

## Integration Points

| Component | Dependency |
|-----------|------------|
| Auth (C-03) | Endpoints protected via `get_current_user` dependency; RBAC checked at router level |
| Appointments (C-07) | Foreign key `patient_id` → `patients.id`; soft delete preserves referential integrity |
| Clinical Records (C-10) | Same FK pattern; `is_active` filter excludes deleted patients from active lookups |

---

## Configuration

No new environment variables required. Uses existing:
- `DATABASE_URL` (PostgreSQL)
- `SECRET_KEY` (JWT, already in C-03)

---

## Rollout / Migration Plan

1. Run migration `alembic upgrade head` → creates `patients` table
2. Deploy backend with new router registered in `main.py`
3. Verify health endpoint + manual smoke test of CRUD endpoints
4. Run test suite: `pytest tests/test_patients_api.py -v`

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| DNI format varies by country | Regex `^\d{7,8}$` covers Argentina (7-8 digits); extensible via config if needed |
| Race condition on DNI check | DB unique index is source of truth; catch `IntegrityError` → map to 409 |
| Search performance on large datasets | Add trigram index (pg_trgm) if `ILIKE` becomes slow; not needed for MVP |

---

## Open Questions (from PA-01 in KB)

- **PA-01**: ¿Se permite que un paciente tenga múltiples obras sociales simultáneas?
  - **Decision for C-05**: Single `insurance_provider` + `insurance_number` per patient. Multi-coverage deferred to C-10 if needed.

- **PA-01**: ¿El campo `medical_history` es texto libre o estructurado?
  - **Decision for C-05**: Texto libre (`Text`). Estructura (alergias, medicamentos, etc.) se modelará en C-10 (Historia Clínica).

---