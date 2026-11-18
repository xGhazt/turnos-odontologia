from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.base import AuditMixin
from app.models.Professional import Professional
from app.repositories.base import BaseRepository


class ProfessionalRepository(BaseRepository[Professional]):
    """Repositorio específico para operaciones sobre profesionales."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Professional, session)

    async def get_by_registration(self, registration_number: str) -> Optional[Professional]:
        """Obtener profesional por número de matrícula (único)."""
        return await self.get_by(registration_number=registration_number)

    async def get_by_specialty(self, specialty: str) -> List[Professional]:
        """Listar profesionales por especialidad."""
        stmt = select(Professional).where(
            Professional.specialty == specialty, Professional.is_active == True
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_with_user(self, professional_id: int) -> Optional[Professional]:
        """Obtener profesional con su usuario asociado (carga anticipada)."""
        stmt = select(Professional).options(selectinload(Professional.user)).where(
            Professional.id == professional_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()