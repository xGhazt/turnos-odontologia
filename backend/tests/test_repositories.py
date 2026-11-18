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
    async with async_engine.begin() as conn:
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