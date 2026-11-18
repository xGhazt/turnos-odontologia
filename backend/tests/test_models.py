"""Tests para modelos de dominio y auditoría C-02.

Validan la creación de entidades, campos de auditoría,
restricciones de unicidad y operación de soft delete.
"""

import pytest

from app.models.base import Base, AuditMixin
from app.models.User import Role, User
from app.models.Professional import Professional
from app.models.Chair import Chair


class TestAuditMixin:
    """Tests para el mixin de auditoría."""

    def test_audit_mixin_has_required_fields(self):
        """Verificar que AuditMixin tiene los 4 campos requeridos."""
        assert hasattr(AuditMixin, "created_at")
        assert hasattr(AuditMixin, "updated_at")
        assert hasattr(AuditMixin, "deleted_at")
        assert hasattr(AuditMixin, "is_active")

    def test_audit_mixin_field_types(self):
        """Verificar tipos de campos en AuditMixin."""
        from sqlalchemy import DateTime, Boolean, inspect
        from sqlalchemy.orm import Mapped

        assert isinstance(inspect(User).columns.created_at.type, DateTime)
        assert isinstance(inspect(User).columns.updated_at.type, DateTime)
        assert isinstance(inspect(User).columns.deleted_at.type, DateTime)
        assert isinstance(inspect(User).columns.is_active.type, Boolean)


class TestUserModel:
    """Tests para el modelo User."""

    @pytest.fixture
    def setup_user_role(self, db_session):
        """Setup: crear un rol para asociar al usuario."""
        role = Role(name="test_role")
        db_session.add(role)
        db_session.flush()
        return role

    def test_user_creation_with_role(self, db_session, setup_user_role):
        """Test: crear usuario con rol asociado."""
        role = setup_user_role
        user = User(
            email="test@example.com",
            password_hash="hash_test",
            role_id=role.id,
        )
        db_session.add(user)
        db_session.flush()

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.role_id == role.id
        assert user.is_active == True  # Valor por defecto del mixin
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_user_email_unique(self, db_session):
        """Test: email debe ser único."""
        role = Role(name="test_role2")
        db_session.add(role)
        db_session.flush()

        user1 = User(email="duplicate@test.com", password_hash="hash1", role_id=role.id)
        db_session.add(user1)
        db_session.flush()

        user2 = User(email="duplicate@test.com", password_hash="hash2", role_id=role.id)
        db_session.add(user2)

        with pytest.raises(Exception):  # IntegrityError por único
            db_session.flush()


class TestRoleModel:
    """Tests para el modelo Role."""

    def test_role_creation(self, db_session):
        """Test: crear rol básico."""
        role = Role(name="test_role")
        db_session.add(role)
        db_session.flush()

        assert role.id is not None
        assert role.name == "test_role"
        assert role.is_active == True

    def test_role_name_unique(self, db_session):
        """Test: nombre de rol debe ser único."""
        role1 = Role(name="unique_role")
        db_session.add(role1)
        db_session.flush()

        role2 = Role(name="unique_role")
        db_session.add(role2)

        with pytest.raises(Exception):  # IntegrityError
            db_session.flush()


class TestProfessionalModel:
    """Tests para el modelo Professional."""

    def test_professional_creation(self, db_session):
        """Test: crear profesional con datos básicos."""
        role = Role(name="test_role")
        db_session.add(role)
        db_session.flush()

        user = User(
            email="prof_test@example.com",
            password_hash="hash_test",
            role_id=role.id,
        )
        db_session.add(user)
        db_session.flush()

        professional = Professional(
            registration_number="M-99999",
            specialty="Clínica General",
            user_id=user.id,
        )
        db_session.add(professional)
        db_session.flush()

        assert professional.id is not None
        assert professional.registration_number == "M-99999"
        assert professional.specialty == "Clínica General"
        assert professional.is_active == True
        assert professional.user_id == user.id


class TestChairModel:
    """Tests para el modelo Chair."""

    def test_chair_creation(self, db_session):
        """Test: crear sillón básico."""
        chair = Chair(name="Box 1")
        db_session.add(chair)
        db_session.flush()

        assert chair.id is not None
        assert chair.name == "Box 1"
        assert chair.is_active == True

    def test_chair_name_unique_when_active(self, db_session):
        """Test: nombre de sillón activo debe ser único."""
        import pytest
        from sqlalchemy.exc import IntegrityError

        chair1 = Chair(name="UniqueBox")
        db_session.add(chair1)
        db_session.flush()

        chair2 = Chair(name="UniqueBox")
        db_session.add(chair2)
        with pytest.raises(IntegrityError):
            db_session.flush()
        db_session.rollback()


def test_chair_name_not_unique_when_inactive(db_session):
    """Test: nombres de sillón inactivo pueden repetirse."""
    chair1 = Chair(name="SharedName")
    chair1.is_active = False
    db_session.add(chair1)
    db_session.flush()

    chair2 = Chair(name="SharedName")
    chair2.is_active = False
    db_session.add(chair2)
    db_session.flush()

    assert chair2.id is not None


class TestSoftDelete:
    """Tests para soft delete e is_active."""

    def test_soft_delete_sets_is_active_false(self, db_session):
        """Test: soft delete debe setear is_active=False."""
        role = Role(name="test_role")
        db_session.add(role)
        db_session.flush()

        user = User(
            email="soft_delete@test.com",
            password_hash="hash",
            role_id=role.id,
        )
        db_session.add(user)
        db_session.flush()

        # Verificar que inicialmente está activo
        assert user.is_active == True

        # Soft delete
        user.is_active = False
        db_session.flush()

        # Verificar que quedó inactivo
        refreshed = db_session.query(User).filter_by(email="soft_delete@test.com").first()
        assert refreshed.is_active == False

    def test_soft_delete_preserves_data(self, db_session):
        """Test: soft delete no debe borrar físicamente el registro."""
        role = Role(name="test_role")
        db_session.add(role)
        db_session.flush()

        user = User(
            email="preserve@test.com",
            password_hash="hash",
            role_id=role.id,
        )
        db_session.add(user)
        db_session.flush()

        user_id = user.id

        # Soft delete
        user.is_active = False
        db_session.flush()

        # Verificar que el registro sigue existiendo
        assert db_session.query(User).filter_by(id=user_id).first() is not None
        # Verificar que no está activo
        assert db_session.query(User).filter_by(id=user_id).first().is_active == False