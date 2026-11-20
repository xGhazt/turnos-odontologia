from datetime import datetime, timezone
from sqlalchemy import event
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class AuditMixin:
    """Mixín que provee campos de auditoría: created_at, updated_at, deleted_at, is_active."""

    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )
    deleted_at: Mapped[datetime | None] = mapped_column(default=None)
    is_active: Mapped[bool] = mapped_column(default=True)


class Base(DeclarativeBase):
    """Base declarativa de SQLAlchemy para todos los modelos del dominio."""

    pass


@event.listens_for(Base, "before_update", dispatch_all=True)
def receive_before_update(target, connection, **kwargs):
    """Actualiza automaticamente updated_at en cada escritura."""
    if hasattr(target, "updated_at"):
        target.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
