"""Tests de integración para la API de pacientes (C-05).

Valida todos los endpoints en /api/v1/patients:
- POST /api/v1/patients (201, 409 por DNI duplicado, 422 por validaciones)
- GET /api/v1/patients/{id} (200, 404 por inexistente o soft-deleted)
- GET /api/v1/patients (200 paginado, búsqueda ILIKE por dni, apellido, nombre, páginas vacías)
- PUT /api/v1/patients/{id} (200 actualización de contacto/cobertura, DNI inmutable, 404)
Datos 100% ficticios según RN-06.
"""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.db import get_session
from app.main import create_app
from app.models.base import Base as BaseModel
from tests.factories import make_patient_data


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
async def api_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def api_session(api_engine):
    async with api_engine.connect() as conn:
        trans = await conn.begin()
        async_session_maker = sessionmaker(
            bind=conn, class_=AsyncSession, expire_on_commit=False
        )
        async with async_session_maker() as session:
            yield session
        await trans.rollback()


@pytest.fixture
async def test_client(api_session):
    app = create_app()

    async def override_get_session():
        yield api_session

    app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


class TestPatientsApi:
    """Tests de integración para /api/v1/patients."""

    # -------------------------------------------------------------------------
    # POST /api/v1/patients
    # -------------------------------------------------------------------------

    async def test_create_patient_success(self, test_client: AsyncClient):
        """Creación exitosa de paciente retorna 201 y los datos con ID y timestamps."""
        payload = make_patient_data(dni="11223344", first_name="Carlos", last_name="Gómez")
        # Serializar fechas para JSON
        payload["birth_date"] = payload["birth_date"].isoformat()

        response = await test_client.post("/api/v1/patients", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
        assert data["dni"] == "11223344"
        assert data["first_name"] == "Carlos"
        assert data["last_name"] == "Gómez"
        assert data["is_active"] is True
        assert "created_at" in data
        assert "updated_at" in data

    async def test_create_patient_duplicate_dni_409(self, test_client: AsyncClient):
        """DNI duplicado retorna 409 Conflict y detalle claro (RN-04)."""
        payload = make_patient_data(dni="22334455")
        payload["birth_date"] = payload["birth_date"].isoformat()

        res1 = await test_client.post("/api/v1/patients", json=payload)
        assert res1.status_code == 201

        # Segundo intento con mismo DNI
        payload2 = make_patient_data(dni="22334455", first_name="Otro", email="otro@fake.com")
        payload2["birth_date"] = payload2["birth_date"].isoformat()

        res2 = await test_client.post("/api/v1/patients", json=payload2)
        assert res2.status_code == 409
        assert res2.json()["detail"] == "DNI ya registrado"

    async def test_create_patient_invalid_email_422(self, test_client: AsyncClient):
        """Email inválido retorna 422 Unprocessable Entity."""
        payload = make_patient_data(dni="33445566", email="email-no-valido")
        payload["birth_date"] = payload["birth_date"].isoformat()

        response = await test_client.post("/api/v1/patients", json=payload)
        assert response.status_code == 422

    async def test_create_patient_invalid_dni_format_422(self, test_client: AsyncClient):
        """DNI con formato no argentino (letras o longitud errónea) retorna 422."""
        payload = make_patient_data(dni="12345")  # Menos de 7 dígitos
        payload["birth_date"] = payload["birth_date"].isoformat()

        response = await test_client.post("/api/v1/patients", json=payload)
        assert response.status_code == 422

        payload_alpha = make_patient_data(dni="ABC12345")
        payload_alpha["birth_date"] = payload_alpha["birth_date"].isoformat()
        res_alpha = await test_client.post("/api/v1/patients", json=payload_alpha)
        assert res_alpha.status_code == 422

    async def test_create_patient_missing_required_422(self, test_client: AsyncClient):
        """Falta de campo obligatorio (first_name, last_name, dni) retorna 422."""
        payload = {"phone": "123456"}
        response = await test_client.post("/api/v1/patients", json=payload)
        assert response.status_code == 422

    # -------------------------------------------------------------------------
    # GET /api/v1/patients/{id}
    # -------------------------------------------------------------------------

    async def test_get_patient_success(self, test_client: AsyncClient):
        """Consulta exitosa por ID retorna 200 con todos los datos."""
        payload = make_patient_data(dni="44556677")
        payload["birth_date"] = payload["birth_date"].isoformat()
        create_res = await test_client.post("/api/v1/patients", json=payload)
        patient_id = create_res.json()["id"]

        get_res = await test_client.get(f"/api/v1/patients/{patient_id}")
        assert get_res.status_code == 200
        data = get_res.json()
        assert data["id"] == patient_id
        assert data["dni"] == "44556677"
        assert data["insurance_provider"] == "OSDE"

    async def test_get_patient_not_found_404(self, test_client: AsyncClient):
        """ID inexistente retorna 404 Not Found."""
        response = await test_client.get("/api/v1/patients/999999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Paciente no encontrado"

    async def test_get_patient_soft_deleted_404(
        self, test_client: AsyncClient, api_session: AsyncSession
    ):
        """Paciente inactivo (soft-deleted) retorna 404."""
        from app.repositories.Patient import PatientRepository

        payload = make_patient_data(dni="55667788")
        payload["birth_date"] = payload["birth_date"].isoformat()
        create_res = await test_client.post("/api/v1/patients", json=payload)
        patient_id = create_res.json()["id"]

        # Soft delete directo en repo
        repo = PatientRepository(api_session)
        await repo.soft_delete(patient_id)

        get_res = await test_client.get(f"/api/v1/patients/{patient_id}")
        assert get_res.status_code == 404
        assert get_res.json()["detail"] == "Paciente no encontrado"

    # -------------------------------------------------------------------------
    # GET /api/v1/patients (Listado y Búsqueda)
    # -------------------------------------------------------------------------

    async def test_list_patients_paginated(self, test_client: AsyncClient):
        """Listado paginado retorna 200 con metadatos y lista ordenada."""
        for i in range(5):
            payload = make_patient_data(
                dni=f"6100000{i}",
                first_name=f"Ana{i}",
                last_name=f"Zúñiga{i}",
                email=f"ana{i}@fake.com",
            )
            payload["birth_date"] = payload["birth_date"].isoformat()
            await test_client.post("/api/v1/patients", json=payload)

        res = await test_client.get("/api/v1/patients?page=1&size=2")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 5
        assert data["page"] == 1
        assert data["size"] == 2
        assert data["total_pages"] == 3
        assert len(data["items"]) == 2

    async def test_search_by_dni_partial(self, test_client: AsyncClient):
        """Búsqueda por DNI parcial filtra correctamente."""
        p1 = make_patient_data(dni="71234588", email="a@fake.com")
        p1["birth_date"] = p1["birth_date"].isoformat()
        p2 = make_patient_data(dni="79999988", email="b@fake.com")
        p2["birth_date"] = p2["birth_date"].isoformat()
        await test_client.post("/api/v1/patients", json=p1)
        await test_client.post("/api/v1/patients", json=p2)

        res = await test_client.get("/api/v1/patients?query=12345")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 1
        assert data["items"][0]["dni"] == "71234588"

    async def test_search_by_last_name_partial_case_insensitive(
        self, test_client: AsyncClient
    ):
        """Búsqueda por apellido parcial es insensible a mayúsculas/minúsculas."""
        p1 = make_patient_data(dni="81000001", last_name="García", email="g@fake.com")
        p1["birth_date"] = p1["birth_date"].isoformat()
        p2 = make_patient_data(dni="81000002", last_name="Rodríguez", email="r@fake.com")
        p2["birth_date"] = p2["birth_date"].isoformat()
        await test_client.post("/api/v1/patients", json=p1)
        await test_client.post("/api/v1/patients", json=p2)

        res = await test_client.get("/api/v1/patients?query=garc")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 1
        assert data["items"][0]["last_name"] == "García"

    async def test_search_by_first_name_partial(self, test_client: AsyncClient):
        """Búsqueda por nombre parcial filtra correctamente."""
        p1 = make_patient_data(dni="82000001", first_name="Juan Carlos", email="jc@fake.com")
        p1["birth_date"] = p1["birth_date"].isoformat()
        p2 = make_patient_data(dni="82000002", first_name="María Elena", email="me@fake.com")
        p2["birth_date"] = p2["birth_date"].isoformat()
        await test_client.post("/api/v1/patients", json=p1)
        await test_client.post("/api/v1/patients", json=p2)

        res = await test_client.get("/api/v1/patients?query=juan")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 1
        assert data["items"][0]["first_name"] == "Juan Carlos"

    async def test_list_page_out_of_range(self, test_client: AsyncClient):
        """Página fuera de rango retorna 200 con items vacíos y total_pages correcto."""
        p = make_patient_data(dni="83000001")
        p["birth_date"] = p["birth_date"].isoformat()
        await test_client.post("/api/v1/patients", json=p)

        res = await test_client.get("/api/v1/patients?page=99&size=20")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 1
        assert data["page"] == 99
        assert data["items"] == []
        assert data["total_pages"] == 1

    # -------------------------------------------------------------------------
    # PUT /api/v1/patients/{id}
    # -------------------------------------------------------------------------

    async def test_update_contact_success(self, test_client: AsyncClient):
        """Actualización exitosa de contacto refresca updated_at y devuelve 200."""
        p = make_patient_data(dni="91000001")
        p["birth_date"] = p["birth_date"].isoformat()
        create_res = await test_client.post("/api/v1/patients", json=p)
        created = create_res.json()
        patient_id = created["id"]

        update_payload = {
            "phone": "+54 11 9999-8888",
            "email": "contacto.nuevo@fake.com",
        }
        res = await test_client.put(f"/api/v1/patients/{patient_id}", json=update_payload)
        assert res.status_code == 200
        updated = res.json()
        assert updated["phone"] == "+54 11 9999-8888"
        assert updated["email"] == "contacto.nuevo@fake.com"
        assert updated["dni"] == "91000001"

    async def test_update_insurance_success(self, test_client: AsyncClient):
        """Actualización de cobertura médica retorna 200."""
        p = make_patient_data(dni="92000001")
        p["birth_date"] = p["birth_date"].isoformat()
        create_res = await test_client.post("/api/v1/patients", json=p)
        patient_id = create_res.json()["id"]

        update_payload = {
            "insurance_provider": "Swiss Medical",
            "insurance_number": "SM-998877",
        }
        res = await test_client.put(f"/api/v1/patients/{patient_id}", json=update_payload)
        assert res.status_code == 200
        updated = res.json()
        assert updated["insurance_provider"] == "Swiss Medical"
        assert updated["insurance_number"] == "SM-998877"

    async def test_update_dni_ignored(self, test_client: AsyncClient):
        """Intento de modificación de DNI es rechazado con 422 por schema estricto (extra=forbid)."""
        p = make_patient_data(dni="93000001")
        p["birth_date"] = p["birth_date"].isoformat()
        create_res = await test_client.post("/api/v1/patients", json=p)
        patient_id = create_res.json()["id"]

        # Intentar modificar dni en PUT
        update_payload = {
            "first_name": "NuevoNombre",
            "dni": "99999999",
        }
        res = await test_client.put(f"/api/v1/patients/{patient_id}", json=update_payload)
        # extra="forbid" en PatientUpdate rechaza campos extra (como dni) con 422
        assert res.status_code == 422

        # Verificar que el paciente conserva su DNI original
        get_res = await test_client.get(f"/api/v1/patients/{patient_id}")
        assert get_res.json()["dni"] == "93000001"

    async def test_update_not_found_404(self, test_client: AsyncClient):
        """Actualización de paciente inexistente retorna 404 Not Found."""
        res = await test_client.put("/api/v1/patients/999999", json={"first_name": "NoExiste"})
        assert res.status_code == 404
        assert res.json()["detail"] == "Paciente no encontrado"
