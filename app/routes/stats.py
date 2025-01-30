from fastapi import APIRouter, Query, Depends

from . import validate_api_token
from app.services.stats import StatsService
from app.schemas.stats import StatsUserSchema

router = APIRouter(prefix="/api/stats", tags=["Stats"])


@router.get(
    "{nickname}/current",
    response_model=StatsUserSchema,
    dependencies=[Depends(validate_api_token)]
)
async def get_current_stats(
        nickname: str,
        service: StatsService = Depends()
):
    return await service.get_current(nickname)


@router.get(
    "{nickname}/increase",
    response_model=StatsUserSchema,
    dependencies=[Depends(validate_api_token)]
)
async def get_increase_stats(
        nickname: str,
        days: int = Query(),
        service: StatsService = Depends()
):
    return await service.get_increase(nickname, days)

