from fastapi import Depends

from app.repositories.external import ExternalRepository
from app.repositories.user import UserRepository
from app.schemas.user import UserSchema
from app.db.tables import User


class UserService:
    def __init__(
            self,
            user_repository: UserRepository = Depends()
    ):
        self.user_repository = user_repository

    async def create(self, nickname: str, app_id: str, app_bundle: str) -> UserSchema:
        model = User(nickname=nickname, app_id=app_id, app_bundle=app_bundle)
        model = await self.user_repository.store(model)
        return UserSchema.model_validate(model)

    async def get(self, nickname: str) -> UserSchema:
        model = await self.user_repository.get_by_nickname(nickname)
        return UserSchema.model_validate(model)

