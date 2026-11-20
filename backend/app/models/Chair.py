from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Index, text

from app.models.base import Base, AuditMixin


class Chair(Base, AuditMixin):
    """Sillones / boxes de atención física."""

    __tablename__ = "chairs"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    __table_args__ = (
        Index(
            "uq_active_chair_name",
            "name",
            unique=True,
            postgresql_where=text("is_active = true"),
            sqlite_where=text("is_active = 1"),
        ),
    )