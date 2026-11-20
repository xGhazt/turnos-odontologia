from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func

from app.models.Patient import Patient
from app.repositories.base import BaseRepository


class PatientRepository(BaseRepository[Patient]):
    """Repositorio específico para pacientes con búsqueda y validación de DNI."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Patient, session)

    async def get_by_dni(self, dni: str) -> Optional[Patient]:
        """Obtener paciente por DNI exacto (activo o inactivo, para unicidad o consulta)."""
        stmt = select(self.model).where(self.model.dni == dni)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def search(
        self,
        query: Optional[str] = None,
        page: int = 1,
        size: int = 20,
    ) -> Tuple[List[Patient], int]:
        """Búsqueda paginada de pacientes activos con ILIKE sobre dni, apellido y nombre.

        Retorna (lista_pacientes, total_count).
        Orden predeterminado: last_name, first_name ascendente.
        """
        base_conditions = [self.model.is_active.is_(True)]

        if query:
            search_pattern = f"%{query.strip()}%"
            base_conditions.append(
                or_(
                    self.model.dni.ilike(search_pattern),
                    self.model.last_name.ilike(search_pattern),
                    self.model.first_name.ilike(search_pattern),
                )
            )

        # Contar total
        count_stmt = select(func.count(self.model.id)).where(*base_conditions)
        total_result = await self.session.execute(count_stmt)
        total: int = total_result.scalar_one()

        # Obtener página
        offset = (page - 1) * size
        items_stmt = (
            select(self.model)
            .where(*base_conditions)
            .order_by(self.model.last_name.asc(), self.model.first_name.asc())
            .offset(offset)
            .limit(size)
        )
        items_result = await self.session.execute(items_stmt)
        items: List[Patient] = list(items_result.scalars().all())

        return items, total
