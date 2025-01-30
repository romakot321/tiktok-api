from sqlalchemy import select
import datetime as dt

from .base import BaseRepository
from app.db.tables import UserStats, VideoStats


class StatsRepository(BaseRepository):
    base_table = UserStats

    async def get_latest(self, nickname: str) -> UserStats | None:
        query = select(UserStats).order_by(UserStats.created_at.desc()).filter_by(nickname=nickname).limit(1)
        return await self.session.scalar(query)

    async def get_increase(self, nickname: str, days: int) -> dict:
        ago = (dt.datetime.now() - dt.timedelta(days=days))
        ago = ago.replace(hour=0, minute=0, second=0)

        query = select(UserStats).order_by(UserStats.created_at).where(UserStats.created_at >= ago).filter_by(nickname=nickname).limit(1)
        first_stats = await self.session.scalar(query)
        if first_stats is None:
            return {"followers": 0, "following": 0, "likes": 0, "diggs": 0, "created_at": ago, "nickname": nickname}
            return UserStats(followers=0, following=0, likes=0, diggs=0)
        second_stats = await self.get_latest(nickname)

        return {
            "followers": second_stats.followers - first_stats.followers,
            "following": second_stats.following - first_stats.following,
            "likes": second_stats.likes - first_stats.likes,
            "diggs": second_stats.diggs - first_stats.diggs,
            "created_at": first_stats.created_at,
            "nickname": nickname
        }

    async def store_user(self, model: UserStats, do_commit=True):
        self.session.add(model)
        if do_commit:
            await self.commit()

    async def store_video(self, model: VideoStats, do_commit=True):
        self.session.add(model)
        if do_commit:
            await self.commit()

