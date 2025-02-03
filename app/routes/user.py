from fastapi import APIRouter, Depends, BackgroundTasks

from . import validate_api_token
from app.services.user import UserService
from app.services.stats import StatsService
from app.schemas.user import UserSchema, UserCreateSchema

router = APIRouter(prefix="/api/user", tags=["User"])


@router.post(
    "",
    response_model=UserSchema,
    dependencies=[Depends(validate_api_token)]
)
async def store_user(
        schema: UserCreateSchema,
        background_tasks: BackgroundTasks,
        service: UserService = Depends()
):
    user = await service.create(**schema.model_dump())
    background_tasks.add_task(StatsService.load_user_stats, schema.nickname)
    return user


@router.get(
    "/{nickname}",
    response_model=UserSchema,
    dependencies=[Depends(validate_api_token)]
)
async def get_user(
        nickname: str,
        service: UserService = Depends()
):
    return await service.get(nickname)
