from fastapi import Depends, HTTPException
import asyncio
import datetime as dt
from loguru import logger

from app.repositories.external import ExternalRepository
from app.repositories.stats import StatsRepository
from app.repositories.user import UserRepository
from app.schemas.stats import StatsUserSchema, StatsSchema
from app.schemas.external import ExternalDataSchema
from app.db.base import get_session
from app.db.tables import UserStats, VideoStats


class StatsService:
    def __init__(
            self,
            external_repository: ExternalRepository = Depends(),
            stats_repository: StatsRepository = Depends()
    ):
        self.external_repository = external_repository
        self.stats_repository = stats_repository

    async def get_current(self, nickname: str) -> StatsUserSchema:
        stats = await self.stats_repository.get_latest(nickname)
        if stats is None:
            raise HTTPException(404)
        return StatsSchema.model_validate(stats)

    async def get_increase(self, nickname: str, days: int) -> StatsUserSchema:
        model = await self.stats_repository.get_increase(nickname, days)
        return StatsUserSchema.model_validate(model)

    async def _save_stats(self, stats: ExternalDataSchema):
        now = dt.datetime.now()
        user_stats = UserStats(
            followers=stats.followers,
            following=stats.following,
            likes=stats.likes,
            diggs=stats.digg_count,
            nickname=stats.account_id,
            created_at=now
        )
        await self.stats_repository.store_user(user_stats, do_commit=False)
        videos = [
            VideoStats(video_id=schema.video_id, views=schema.playcount, comments=schema.commentcount,
                       diggs=schema.diggcount, shares=schema.share_count, nickname=stats.account_id,
                       created_at=now)
            for schema in stats.top_videos
        ]
        [await self.stats_repository.store_video(video, do_commit=False) for video in videos]
        await self.stats_repository.commit()

    @classmethod
    async def update_stats(cls):
        session_getter = get_session()
        db_session = await anext(session_getter)
        user_repository = UserRepository(session=db_session)
        self = cls(external_repository=ExternalRepository(), stats_repository=StatsRepository(session=db_session))

        users = await user_repository.list()
        if users:
            nicknames = [user.nickname for user in users]
            task_id = await self.external_repository.trigger_data_collect(nicknames)

            while (data := await self.external_repository.get_collected_data(task_id)) == None:
                await asyncio.sleep(10)
            [await self._save_stats(stats) for stats in data]
            logger.debug(f"Add {len(data)} stats")

        try:
            await anext(session_getter)
        except StopAsyncIteration:
            pass

