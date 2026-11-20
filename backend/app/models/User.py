from sqlalchemy.orm import Mapped, mapped_column, Relationship
from sqlalchemy import String, Integer, ForeignKey

from app.models.base import Base, AuditMixin


class Role(Base, AuditMixin):
    """Roles del sistema: admin, odontologo, secretaria, paciente."""

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    # Relación inversa: un rol tiene muchos usuarios
    users: Mapped[list["User"]] = Relationship(back_populates="role")


class User(Base, AuditMixin):
    """Usuarios del sistema con credenciales y rol asignado."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id"), nullable=False)

    # Relación: un usuario pertenece a un rol
    role: Mapped["Role"] = Relationship(back_populates="users")
    # Relación: un usuario tiene un profesional asociado (odontólogo)
    professional: Mapped["Professional"] = Relationship(back_populates="user")