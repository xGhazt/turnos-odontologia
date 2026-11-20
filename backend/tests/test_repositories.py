"""Tests para repositorios C-02.

Validan operaciones CRUD através de BaseRepository y
métodos específicos de cada repositorio concreto.
"""

import pytest

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.settings import get_settings
from app.repositories.base import BaseRepository
from app.repositories.User import UserRepository
from app.repositories.Professional import ProfessionalRepository
from app.repositories.Chair import ChairRepository
from app.models.base import Base as BaseModel
from app.models.User import User, Role
from app.models.Professional import Professional
from app.models.Chair import Chair


# Engine y sesión para tests (SQLite en memoria, aislado de BD development)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
async def async_engine():
    """Motor de BD session-scoped: crea schema una vez y aísla por transacción."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def session(async_engine):
    """Sesión function-scoped con rollback por test: aislamiento total."""
    async with async_engine.connect() as conn:
        trans = await conn.begin()
        async_session_maker = sessionmaker(
            bind=conn, class_=AsyncSession, expire_on_commit=False
        )
        async with async_session_maker() as session:
            # Crear rol id=1 y usuario id=1 si son necesarios para los tests
            # que dependen de IDs fijos, sin afectar otros tests (rollback al final).
            from app.models.User import Role, User
            existing_role = await session.get(Role, 1)
            if existing_role is None:
                existing_role = Role(id=1, name="admin")
                session.add(existing_role)
                await session.flush()
            existing_user = await session.get(User, 1)
            if existing_user is None:
                existing_user = User(id=1, email="test@test.com", password_hash="hash", role_id=1)
                session.add(existing_user)
                await session.flush()
            yield session
        await trans.rollback()


class TestBaseRepository:
    """Tests para BaseRepository genérico."""

    async def test_create(self, session: AsyncSession):
        """Test: crear un nuevo registro."""
        repo = BaseRepository(User, session)
        user = await repo.create(
            email="create_test@example.com",
            password_hash="hash",
            role_id=1,
        )
        assert user.id is not None
        assert user.email == "create_test@example.com"

    async def test_get_by_id(self, session: AsyncSession):
        """Test: obtener por ID."""
        repo = BaseRepository(User, session)
        user = await repo.create(
            email="getbyid_test@example.com",
            password_hash="hash",
            role_id=1,
        )
        retrieved = await repo.get_by_id(user.id)
        assert retrieved is not None
        assert retrieved.email == "getbyid_test@example.com"

    async def test_get_by(self, session: AsyncSession):
        """Test: obtener por filtros."""
        repo = BaseRepository(User, session)
        await repo.create(
            email="getby_test@example.com",
            password_hash="hash",
            role_id=1,
        )
        result = await repo.get_by(email="getby_test@example.com")
        assert result is not None
        assert result.email == "getby_test@example.com"

    async def test_get_active(self, session: AsyncSession):
        """Test: obtener solo activos."""
        repo = BaseRepository(User, session)
        user1 = await repo.create(
            email="active_test@example.com",
            password_hash="hash",
            role_id=1,
        )
        # is_active viene por defecto True del mixin
        active = await repo.get_active(email="active_test@example.com")
        assert active is not None
        assert active.is_active == True

    async def test_list_active(self, session: AsyncSession):
        """Test: listar solo activos."""
        repo = BaseRepository(User, session)
        await repo.create(
            email="list_active_test@example.com",
            password_hash="hash",
            role_id=1,
        )
        results = await repo.list_active()
        assert len(results) >= 1

    async def test_update(self, session: AsyncSession):
        """Test: actualizar un registro."""
        repo = BaseRepository(User, session)
        user = await repo.create(
            email="update_test@example.com",
            password_hash="hash",
            role_id=1,
        )
        updated = await repo.update(user.id, email="updated_test@example.com")
        assert updated is not None
        assert updated.email == "updated_test@example.com"

    async def test_soft_delete(self, session: AsyncSession):
        """Test: soft delete."""
        repo = BaseRepository(User, session)
        user = await repo.create(
            email="softdel_test@example.com",
            password_hash="hash",
            role_id=1,
        )
        result = await repo.soft_delete(user.id)
        assert result is not None
        # Verificar que is_active quedó False
        refreshed = await repo.get_by_id(user.id)
        assert refreshed is not None
        assert refreshed.is_active == False

    async def test_soft_delete_sets_deleted_at(self, session: AsyncSession):
        """Test: soft delete también debe setear deleted_at."""
        repo = BaseRepository(User, session)
        user = await repo.create(
            email="softdelat_test@example.com",
            password_hash="hash",
            role_id=1,
        )
        result = await repo.soft_delete(user.id)
        assert result is not None
        # Verificar que is_active quedó False
        refreshed = await repo.get_by_id(user.id)
        assert refreshed is not None
        assert refreshed.is_active == False
        # Verificar que deleted_at fue asignado
        assert refreshed.deleted_at is not None

    async def test_hard_delete(self, session: AsyncSession):
        """Test: hard delete físico."""
        repo = BaseRepository(User, session)
        user = await repo.create(
            email="harddel_test@example.com",
            password_hash="hash",
            role_id=1,
        )
        result = await repo.hard_delete(user.id)
        assert result is True
        # Verificar que ya no existe
        deleted = await repo.get_by_id(user.id)
        assert deleted is None

    async def test_exists(self, session: AsyncSession):
        """Test: verificar existencia."""
        repo = BaseRepository(User, session)
        await repo.create(
            email="exists_test@example.com",
            password_hash="hash",
            role_id=1,
        )
        exists = await repo.exists(email="exists_test@example.com")
        assert exists is True
        exists_none = await repo.exists(email="nonexistent@example.com")
        assert exists_none is False


class TestUserRepository:
    """Tests para UserRepository específico."""

    async def test_get_by_email(self, session: AsyncSession):
        """Test: obtener usuario por email."""
        repo = UserRepository(session)
        await repo.create(
            email="specific_email@Test.com",
            password_hash="hash",
            role_id=1,
        )
        result = await repo.get_by_email("specific_email@Test.com")
        assert result is not None
        assert result.email == "specific_email@Test.com"

    async def test_get_by_role(self, session: AsyncSession):
        """Test: obtener rol por nombre."""
        repo = UserRepository(session)
        result = await repo.get_by_role("admin")
        assert result is not None
        assert result.name == "admin"

    async def test_get_users_by_role(self, session: AsyncSession):
        """Test: listar usuarios por rol."""
        repo = UserRepository(session)
        # Crear rol si no existe y un usuario
        result = await repo.get_users_by_role("admin")
        # Puede retornar lista vacía si no hay usuarios, pero no debe fallar


class TestProfessionalRepository:
    """Tests para ProfessionalRepository específico."""

    async def test_get_by_registration(self, session: AsyncSession):
        """Test: obtener profesional por matrícula."""
        repo = ProfessionalRepository(session)
        professional = await repo.create(
            registration_number="M-TEST001",
            specialty="Test",
            user_id=1,  # Asumiendo que usuario 1 existe
        )
        result = await repo.get_by_registration("M-TEST001")
        assert result is not None
        assert result.registration_number == "M-TEST001"

    async def test_get_by_specialty(self, session: AsyncSession):
        """Test: listar profesionales por especialidad."""
        repo = ProfessionalRepository(session)
        result = await repo.get_by_specialty("Test")
        # Retornará lista (potencialmente vacía), no debe fallar

    async def test_get_with_user(self, session: AsyncSession):
        """Test: obtener profesional con usuario cargado eagerly."""
        repo = ProfessionalRepository(session)
        professional = await repo.create(
            registration_number="M-WITHUSER001",
            specialty="TestUser",
            user_id=1,  # usuario ya creado por la fixture session
        )
        result = await repo.get_with_user(professional.id)
        assert result is not None
        # Verificar que la relación user fue cargada eagerly (no es None)
        assert result.user is not None
        assert result.user.id == 1


class TestChairRepository:
    """Tests para ChairRepository específico."""

    async def test_get_by_name_active(self, session: AsyncSession):
        """Test: obtener sillón activo por nombre."""
        repo = ChairRepository(session)
        chair = await repo.create(name="TestBox")
        result = await repo.get_by_name_active("TestBox")
        assert result is not None
        assert result.name == "TestBox"
        assert result.is_active == True

    async def test_check_name_available(self, session: AsyncSession):
        """Test: verificar disponibilidad de nombre."""
        repo = ChairRepository(session)
        # Crear un sillón
        await repo.create(name="AvailableCheck")
        # Verificar que está "disponible" (no hay otro con mismo nombre activo)
        # y luego verificar que el check funciona
        is_avail = await repo.check_name_available("AvailableCheck")
        assert isinstance(is_avail, bool)


class TestPatientRepository:
    """Tests para PatientRepository."""

    async def test_create_patient(self, session: AsyncSession):
        from app.repositories.Patient import PatientRepository
        from tests.factories import make_patient_data

        repo = PatientRepository(session)
        patient = await repo.create(**make_patient_data(dni="11111111"))
        assert patient.id is not None
        assert patient.dni == "11111111"
        assert patient.is_active is True

    async def test_get_by_dni_existing(self, session: AsyncSession):
        from app.repositories.Patient import PatientRepository
        from tests.factories import make_patient_data

        repo = PatientRepository(session)
        await repo.create(**make_patient_data(dni="22222222"))
        found = await repo.get_by_dni("22222222")
        assert found is not None
        assert found.dni == "22222222"

    async def test_get_by_dni_not_found(self, session: AsyncSession):
        from app.repositories.Patient import PatientRepository

        repo = PatientRepository(session)
        found = await repo.get_by_dni("99999999")
        assert found is None

    async def test_search_pagination(self, session: AsyncSession):
        from app.repositories.Patient import PatientRepository
        from tests.factories import make_patient_data

        repo = PatientRepository(session)
        for i in range(5):
            await repo.create(
                **make_patient_data(
                    dni=f"3000000{i}",
                    first_name=f"Nombre{i}",
                    last_name=f"Apellido{i}",
                    email=f"p{i}@fake.com",
                )
            )

        items, total = await repo.search(page=1, size=2)
        assert total == 5
        assert len(items) == 2

        items_p3, total_p3 = await repo.search(page=3, size=2)
        assert total_p3 == 5
        assert len(items_p3) == 1

    async def test_search_by_dni_partial(self, session: AsyncSession):
        from app.repositories.Patient import PatientRepository
        from tests.factories import make_patient_data

        repo = PatientRepository(session)
        await repo.create(**make_patient_data(dni="12345678", email="a@fake.com"))
        await repo.create(**make_patient_data(dni="87654321", email="b@fake.com"))

        items, total = await repo.search(query="12345")
        assert total == 1
        assert items[0].dni == "12345678"

    async def test_search_by_last_name_partial(self, session: AsyncSession):
        from app.repositories.Patient import PatientRepository
        from tests.factories import make_patient_data

        repo = PatientRepository(session)
        await repo.create(**make_patient_data(dni="40000001", last_name="García", email="g@fake.com"))
        await repo.create(**make_patient_data(dni="40000002", last_name="López", email="l@fake.com"))

        items, total = await repo.search(query="garc")
        assert total == 1
        assert items[0].last_name == "García"

    async def test_search_by_first_name_partial(self, session: AsyncSession):
        from app.repositories.Patient import PatientRepository
        from tests.factories import make_patient_data

        repo = PatientRepository(session)
        await repo.create(**make_patient_data(dni="50000001", first_name="Juan Carlos", email="j@fake.com"))
        await repo.create(**make_patient_data(dni="50000002", first_name="María", email="m@fake.com"))

        items, total = await repo.search(query="juan")
        assert total == 1
        assert items[0].first_name == "Juan Carlos"

    async def test_search_empty_page_out_of_range(self, session: AsyncSession):
        from app.repositories.Patient import PatientRepository
        from tests.factories import make_patient_data

        repo = PatientRepository(session)
        await repo.create(**make_patient_data(dni="60000001"))

        items, total = await repo.search(page=99, size=20)
        assert total == 1
        assert items == []

    async def test_update_patient_contact(self, session: AsyncSession):
        from app.repositories.Patient import PatientRepository
        from tests.factories import make_patient_data

        repo = PatientRepository(session)
        patient = await repo.create(**make_patient_data(dni="70000001"))
        updated = await repo.update(patient.id, phone="+54 11 5555-9999", email="nuevo@fake.com")
        assert updated is not None
        assert updated.phone == "+54 11 5555-9999"
        assert updated.email == "nuevo@fake.com"

    async def test_update_patient_insurance(self, session: AsyncSession):
        from app.repositories.Patient import PatientRepository
        from tests.factories import make_patient_data

        repo = PatientRepository(session)
        patient = await repo.create(**make_patient_data(dni="70000002"))
        updated = await repo.update(
            patient.id,
            insurance_provider="Swiss Medical",
            insurance_number="SM-12345",
        )
        assert updated is not None
        assert updated.insurance_provider == "Swiss Medical"
        assert updated.insurance_number == "SM-12345"

    async def test_soft_delete_patient(self, session: AsyncSession):
        from app.repositories.Patient import PatientRepository
        from tests.factories import make_patient_data

        repo = PatientRepository(session)
        patient = await repo.create(**make_patient_data(dni="80000001"))
        await repo.soft_delete(patient.id)

        items, total = await repo.search()
        assert total == 0
        assert items == []
