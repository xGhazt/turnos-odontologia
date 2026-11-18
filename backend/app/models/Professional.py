from sqlalchemy.orm import Mapped, mapped_column, Relationship
from sqlalchemy import String, Integer, ForeignKey

from app.models.base import Base, AuditMixin


class Professional(Base, AuditMixin):
    """Profesionales (odontólogos) con matrícula y especialidad."""

    __tablename__ = "professionals"

    id: Mapped[int] = mapped_column(primary_key=True)
    registration_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )
    specialty: Mapped[str] = mapped_column(String(100), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    # Relación: un profesional está vinculado a un usuario
    user: Mapped["User"] = Relationship(back_populates="professional")