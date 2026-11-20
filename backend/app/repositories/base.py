from typing import TypeVar, Generic, Optional, List, Type, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import DeclarativeBase

from app.models.base import AuditMixin

ModelType = TypeVar("ModelType", bound=AuditMixin)


class BaseRepository(Generic[ModelType]):
    """Repositorio base genérico asíncrono con SQLAlchemy 2.0.

    Proporciona operaciones CRUD básicas y soporte para soft delete.
    Todos los repositorios específicos deben heredar de este clase.
    """

    def __init__(self, model: Type[ModelType], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def create(self, **kwargs) -> ModelType:
        """Crear un nuevo registro."""
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """Obtener un registro por su ID principal."""
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by(self, **kwargs) -> Optional[ModelType]:
        """Obtener un registro por filtros arbitrarios."""
        stmt = select(self.model).filter_by(**kwargs)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active(self, **kwargs) -> Optional[ModelType]:
        """Obtener un registro activo (is_active=True) por filtros."""
        stmt = (
            select(self.model)
            .where(self.model.is_active == True)
            .filter_by(**kwargs)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_active(self, **kwargs) -> List[ModelType]:
        """Listar todos los registros activos que coincidan con los filtros."""
        stmt = (
            select(self.model).where(self.model.is_active == True).filter_by(**kwargs)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """Actualizar un registro por ID."""
        instance = await self.get_by_id(id)
        if instance is None:
            return None
        for key, value in kwargs.items():
            setattr(instance, key, value)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def soft_delete(self, id: int) -> Optional[ModelType]:
        """Soft delete: marcar como inactivo sin eliminar físicamente."""
        instance = await self.get_by_id(id)
        if instance is None:
            return None
        instance.is_active = False
        instance.deleted_at = datetime.now(timezone.utc)
        await self.session.flush()
        return instance

    async def hard_delete(self, id: int) -> bool:
        """Eliminación física del registro."""
        instance = await self.get_by_id(id)
        if instance is None:
            return False
        await self.session.delete(instance)
        await self.session.flush()
        return True

    async def exists(self, **kwargs) -> bool:
        """Verificar si un registro existe con los filtros dados."""
        stmt = select(self.model).filter_by(**kwargs)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None