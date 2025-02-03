from sqlalchemy import select

from .base import BaseRepository
from app.db.tables import User


class UserRepository(BaseRepository):
    base_table = User

    async def store(self, model: User) -> User:
        return await self._create(model)

    async def list(self) -> list[User]:
        query = select(self.base_table)
        query = query.order_by(self.base_table.id.desc())
        return list(await self.session.scalars(query))

    async def update_avatar(self, nickname: str, avatar: str):
        user = await self._get_one(nickname=nickname)
        await self._update_obj(user, avatar=avatar)

