from fastapi import APIRouter, Depends

from . import validate_api_token
from app.services.user import UserService
from app.schemas.user import UserSchema, UserCreateSchema

router = APIRouter(prefix="/api/user", tags=["User"])


@router.post(
    "",
    response_model=UserSchema,
    dependencies=[Depends(validate_api_token)]
)
async def store_user(
        schema: UserCreateSchema,
        service: UserService = Depends()
):
    return await service.create(**schema.model_dump())

