from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.base import AuditMixin
from app.models.Chair import Chair
from app.repositories.base import BaseRepository


class ChairRepository(BaseRepository[Chair]):
    """Repositorio específico para operaciones sobre sillones/boxes de atención."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Chair, session)

    async def get_by_name_active(self, name: str) -> Optional[Chair]:
        """Obtener sillón activo por nombre.

        Retorna None si no existe o si está inactivo.
        Utiliza la UniqueConstraint(name, is_active) de la tabla.
        """
        return await self.get_active(name=name)

    async def get_inactive_by_name(self, name: str) -> Optional[Chair]:
        """Obtener sillón inactivo por nombre (aún existe en BD)."""
        stmt = select(Chair).where(
            Chair.name == name, Chair.is_active == False
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_active_all(self) -> List[Chair]:
        """Listar todos los sillones activos."""
        return await self.list_active()

    async def check_name_available(self, name: str, exclude_id: int | None = None) -> bool:
        """Verificar si un nombre de sillón está disponible para ser usado.

        Returns True si no existe ningún sillón activo con ese nombre.
        Si exclude_id se provee, omite ese sillón en la verificación
        (útil para actualizaciones).
        """
        if exclude_id is None:
            stmt = select(Chair).where(
                Chair.name == name, Chair.is_active == True
            )
        else:
            stmt = select(Chair).where(
                Chair.name == name,
                Chair.is_active == True,
                Chair.id != exclude_id,
            )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is None