from sqlalchemy import select, delete
from pydantic import BaseModel, ConfigDict
import datetime as dt

from .base import BaseRepository
from app.db.tables import UserStats, VideoStats
from app.db.tables import TrendVideo, TrendHashtag, TrendSong


class Stats(BaseModel):
    user_stats: UserStats
    video_stats: list[VideoStats]

    model_config = ConfigDict(arbitrary_types_allowed=True)


class StatsRepository(BaseRepository):
    base_table = UserStats

    async def get_latest(self, nickname: str) -> Stats | None:
        query = select(UserStats).order_by(UserStats.created_at.desc()).filter_by(nickname=nickname).limit(1)
        user_stats = await self.session.scalar(query)
        if user_stats is None:
            return None
        query = select(VideoStats).filter_by(nickname=nickname, created_at=user_stats.created_at)
        video_stats = await self.session.scalars(query)
        return Stats(user_stats=user_stats, video_stats=list(video_stats))

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

    async def store_trend_video(self, model: TrendVideo, do_commit=True):
        self.session.add(model)
        if do_commit:
            await self.commit()

    async def store_trend_hashtag(self, model: TrendHashtag, do_commit=True):
        self.session.add(model)
        if do_commit:
            await self.commit()

    async def store_trend_song(self, model: TrendSong, do_commit=True):
        self.session.add(model)
        if do_commit:
            await self.commit()

    async def clear_trend_videos(self):
        query = delete(TrendVideo)
        await self.session.execute(query)

    async def clear_trend_hashtags(self):
        query = delete(TrendHashtag)
        await self.session.execute(query)

    async def clear_trend_songs(self):
        query = delete(TrendSong)
        await self.session.execute(query)

    async def get_trend_videos(self) -> list[TrendVideo]:
        query = select(TrendVideo)
        return list(await self.session.scalars(query))

    async def get_trend_hashtags(self) -> list[TrendHashtag]:
        query = select(TrendHashtag)
        return list(await self.session.scalars(query))

    async def get_trend_songs(self) -> list[TrendSong]:
        query = select(TrendSong)
        return list(await self.session.scalars(query))

