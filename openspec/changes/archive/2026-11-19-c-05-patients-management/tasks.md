# Tasks: C-05 Patients Management

> **Conventions**
> - [ ] = not started, [x] = done
> - Each task is independently testable
> - Tasks ordered by dependency (models → schemas → repo → service → router → tests → migration)

---

## 1. Data Model & Migration

### 1.1 Create Patient SQLAlchemy model
- [x] **File**: `backend/app/models/Patient.py`
- [x] Extend `Base` + `AuditMixin`
- [x] Fields per design: id, first_name, last_name, dni (unique), phone, email, birth_date, insurance_provider, insurance_number, medical_history
- [x] Import in `backend/app/models/__init__.py`

### 1.2 Create Alembic migration for patients table
- [x] **Command**: `alembic revision --autogenerate -m "Add patients table"`
- [x] **File**: `backend/alembic/versions/XXX_patients_table.py`
- [x] Verify: unique index on `dni`, audit columns, `is_active` default true
- [x] Run: `alembic upgrade head` (verify in dev DB)

---

## 2. Pydantic Schemas

### 2.1 Create patient schemas
- [x] **File**: `backend/app/schemas/patient.py`
- [x] `PatientBase` — shared fields with strict validation
- [x] `PatientCreate` — inherits base, all required except optional contact/insurance
- [x] `PatientUpdate` — all optional, **excludes `dni`**
- [x] `PatientResponse` — includes audit timestamps
- [x] `PatientListResponse` — paginated wrapper
- [x] Config: `extra="forbid"`, `str_strip_whitespace=True`
- [x] DNI regex: `^\d{7,8}$` (Argentina format)

---

## 3. Repository Layer

### 3.1 Create PatientRepository
- [x] **File**: `backend/app/repositories/Patient.py`
- [x] Inherit `BaseRepository[Patient]`
- [x] `get_by_dni(dni: str)` — exact lookup for duplicate check
- [x] `search(query, page, size)` — returns `(list[Patient], total_count)`
  - ILIKE on dni, last_name, first_name
  - Filter `is_active == True`
  - Order by `last_name, first_name`
  - Pagination with OFFSET/LIMIT
- [x] Import in `backend/app/repositories/__init__.py`

---

## 4. Service Layer

### 4.1 Create PatientService
- [x] **File**: `backend/app/services/patient.py`
- [x] `create(data: PatientCreate)` — check DNI uniqueness via repo, raise `ConflictException` on duplicate
- [x] `get_by_id(patient_id: int)` — raise `NotFoundException` if not found or inactive
- [x] `list(query, page, size)` — delegate to repo.search, map to `PatientListResponse`
- [x] `update(patient_id: int, data: PatientUpdate)` — exclude `dni` from update, raise `NotFoundException` if missing

### 4.2 Define custom exceptions
- [x] **File**: `backend/app/core/exceptions.py` (create if not exists)
- [x] `ConflictException(detail: str)` → HTTP 409
- [x] `NotFoundException(detail: str)` → HTTP 404
- [x] Register exception handlers in `main.py` (or verify existing)

---

## 5. API Router

### 5.1 Create patients router
- [x] **File**: `backend/app/api/v1/patients.py`
- [x] `POST /api/v1/patients` — 201, returns `PatientResponse`
- [x] `GET /api/v1/patients/{patient_id}` — 200, returns `PatientResponse`
- [x] `GET /api/v1/patients` — 200, returns `PatientListResponse` (query, page, size params)
- [x] `PUT /api/v1/patients/{patient_id}` — 200, returns `PatientResponse`
- [x] Dependency: `get_patient_service = Depends(PatientService(PatientRepository(session)))`

### 5.2 Register router in main app
- [x] **File**: `backend/app/main.py`
- [x] Import and `app.include_router(patients_router)`

---

## 6. Tests

### 6.1 Unit tests: Model
- [x] **File**: `backend/tests/test_models.py` (extend)
- [x] `test_patient_creation_sets_audit_timestamps`
- [x] `test_patient_soft_delete_marks_inactive`
- [x] `test_patient_dni_unique_constraint`

### 6.2 Unit tests: Repository
- [x] **File**: `backend/tests/test_repositories.py` (extend with `TestPatientRepository`)
- [x] `test_create_patient`
- [x] `test_get_by_dni_existing`
- [x] `test_get_by_dni_not_found`
- [x] `test_search_pagination`
- [x] `test_search_by_dni_partial`
- [x] `test_search_by_last_name_partial`
- [x] `test_search_by_first_name_partial`
- [x] `test_search_empty_page_out_of_range`
- [x] `test_update_patient_contact`
- [x] `test_update_patient_insurance`
- [x] `test_update_ignores_dni`
- [x] `test_soft_delete_patient`

### 6.3 Integration tests: API endpoints
- [x] **File**: `backend/tests/test_patients_api.py` (new)
- [x] **POST /api/v1/patients**
  - [x] `test_create_patient_success` — 201, returns patient with ID
  - [x] `test_create_patient_duplicate_dni_409` — 409 Conflict, "DNI ya registrado"
  - [x] `test_create_patient_invalid_email_422` — 422 validation error
  - [x] `test_create_patient_invalid_dni_format_422` — 422 validation error
  - [x] `test_create_patient_missing_required_422` — 422 validation error
- [x] **GET /api/v1/patients/{id}**
  - [x] `test_get_patient_success` — 200, all fields present
  - [x] `test_get_patient_not_found_404` — 404
  - [x] `test_get_patient_soft_deleted_404` — 404
- [x] **GET /api/v1/patients**
  - [x] `test_list_patients_paginated` — 200, metadata correct
  - [x] `test_search_by_dni_partial` — 200, filtered results
  - [x] `test_search_by_last_name_partial_case_insensitive` — 200
  - [x] `test_search_by_first_name_partial` — 200
  - [x] `test_list_page_out_of_range` — 200, empty items, correct metadata
- [x] **PUT /api/v1/patients/{id}**
  - [x] `test_update_contact_success` — 200, updated_at refreshed
  - [x] `test_update_insurance_success` — 200
  - [x] `test_update_dni_ignored` — 200, DNI unchanged
  - [x] `test_update_not_found_404` — 404

### 6.4 Test data factories
- [x] **File**: `backend/tests/factories.py` (create if not exists)
- [x] `make_patient_data(**overrides)` — returns dict with fictitious data (RN-06)
  - Use Faker or static fake data: "Juan Pérez", DNI "12345678", email "juan.perez@fake.com"

---

## 7. Verification & Cleanup

### 7.1 Run full test suite
- [x] `pytest tests/test_patients_api.py -v`
- [x] `pytest tests/test_repositories.py::TestPatientRepository -v`
- [x] `pytest tests/test_models.py -k patient -v`
- [x] All tests pass

### 7.2 Manual smoke test
- [x] Start backend: `uvicorn app.main:app --reload`
- [x] `curl -X POST /api/v1/patients` with valid JSON → 201
- [x] `curl -X POST /api/v1/patients` with same DNI → 409
- [x] `curl /api/v1/patients` → 200 with pagination
- [x] `curl /api/v1/patients?query=123` → 200 filtered
- [x] `curl -X PUT /api/v1/patients/{id}` → 200

### 7.3 Update documentation
- [x] Verify OpenAPI/Swagger at `/docs` shows new endpoints
- [x] Check `backend/app/api/__init__.py` exports if needed

---

## Dependencies & Ordering

```
1.1 → 1.2 → 2.1 → 3.1 → 4.1 → 5.1 → 5.2 → 6.1/6.2/6.3 → 7.1 → 7.2
      ↓
   (migration runs after model exists)
```

**Parallelizable:** 6.1, 6.2, 6.3 can run independently after 5.2

---

## Definition of Done

- [x] All tasks checked
- [x] `pytest` passes (no regressions in existing tests)
- [x] New endpoints documented in Swagger
- [x] Migration applies cleanly to fresh DB
- [x] No real patient data in tests/seeds (RN-06)
- [x] DNI uniqueness enforced at DB + API level (RN-04)
- [x] Soft delete preserves referential integrity for future C-07/C-10