from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.User import User, Role
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repositorio específico para operaciones sobre usuarios y roles."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Obtener usuario por email (único)."""
        return await self.get_by(email=email)

    async def get_by_role(self, role_name: str) -> Optional[Role]:
        """Obtener rol por nombre."""
        result = await self.session.execute(
            select(Role).where(Role.name == role_name)
        )
        return result.scalar_one_or_none()

    async def get_users_by_role(self, role_name: str) -> List[User]:
        """Listar todos los usuarios de un rol determinado."""
        stmt = select(User).join(User.role).where(Role.name == role_name)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())