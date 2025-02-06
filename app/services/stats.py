from fastapi import Depends, HTTPException
import asyncio
import datetime as dt
from loguru import logger

from app.repositories.external import ExternalRepository
from app.repositories.stats import StatsRepository
from app.repositories.user import UserRepository
from app.schemas.stats import StatsUserSchema, StatsSchema
from app.schemas.stats import StatsTrendVideoSchema, StatsTrendHashtagSchema, StatsTrendSongSchema
from app.schemas.external import ExternalDataSchema
from app.db.base import get_session
from app.db.tables import UserStats, VideoStats, TrendVideo, TrendHashtag, TrendSong


class StatsService:
    def __init__(
            self,
            external_repository: ExternalRepository = Depends(),
            stats_repository: StatsRepository = Depends(),
            user_repository: UserRepository = Depends()
    ):
        self.external_repository = external_repository
        self.stats_repository = stats_repository
        self.user_repository = user_repository

    async def get_current(self, nickname: str) -> StatsSchema:
        stats = await self.stats_repository.get_latest(nickname)
        if stats is None:
            raise HTTPException(404)
        return StatsSchema.model_validate(stats)

    async def get_increase(self, nickname: str, days: int) -> StatsUserSchema:
        model = await self.stats_repository.get_increase(nickname, days)
        return StatsUserSchema.model_validate(model)

    async def get_trend_videos(self) -> list[StatsTrendVideoSchema]:
        models = await self.stats_repository.get_trend_videos()
        return [StatsTrendVideoSchema.model_validate(model) for model in models]

    async def get_trend_hashtags(self) -> list[StatsTrendHashtagSchema]:
        models = await self.stats_repository.get_trend_hashtags()
        return [StatsTrendHashtagSchema.model_validate(model) for model in models]

    async def get_trend_songs(self) -> list[StatsTrendSongSchema]:
        models = await self.stats_repository.get_trend_songs()
        return [StatsTrendSongSchema.model_validate(model) for model in models]

    async def _save_user_stats(self, schema: ExternalDataSchema, created_at: dt.datetime):
        user_stats = UserStats(
            followers=schema.userInfo.stats.followerCount,
            following=schema.userInfo.stats.followingCount,
            likes=schema.userInfo.stats.heartCount,
            diggs=schema.userInfo.stats.diggCount,
            nickname=schema.userInfo.user.uniqueId,
            created_at=created_at
        )
        await self.stats_repository.store_user(user_stats)
        await self.user_repository.update_avatar(user_stats.nickname, schema.userInfo.user.avatarMedium)

    async def _load_video_stats(self, nicknames: list[str], created_at: dt.datetime):
        data = await self.external_repository.get_video_data(nicknames)
        videos = [
            VideoStats(video_id=schema.id, views=schema.playCount, comments=schema.commentCount,
                       diggs=schema.diggCount, shares=schema.shareCount, nickname=schema.authorMeta.name,
                       created_at=created_at, cover_url=schema.videoMeta.originalCoverUrl, video_url=schema.mediaUrls[0])
            for schema in data
        ]
        [await self.stats_repository.store_video(video, do_commit=False) for video in videos]
        await self.stats_repository.commit()

    async def _load_trend_video(self):
        videos = await self.external_repository.get_trend_videos_data()
        models = [
            TrendVideo(description=video.desc, video_url=video.share_url,
                       cover_url=video.video.cover.url_list[0], views=video.statistics.play_count)
            for video in videos
        ]
        [await self.stats_repository.store_trend_video(model, do_commit=False) for model in models]
        await self.stats_repository.commit()

    async def _load_trend_hashtags(self):
        return  # TODO: Remove when connected
        hashtags = await self.external_repository.get_trend_hashtags_data()
        models = [
            TrendHashtag(name=hashtag.hashtag_name, views=hashtag.video_views)
            for hashtag in hashtags
        ]
        [await self.stats_repository.store_trend_hashtag(model, do_commit=False) for model in models]
        await self.stats_repository.commit()

    async def _load_trend_songs(self):
        return  # TODO: Remove when connected
        songs = await self.external_repository.get_trend_songs_data()
        models = [
            TrendSong(cover_url=song.cover, song_url=song.link, title=song.title, author=song.author)
            for song in songs
        ]
        [await self.stats_repository.store_trend_song(model, do_commit=False) for model in models]
        await self.stats_repository.commit()

    @classmethod
    async def load_user_stats(cls, nickname: str):
        session_getter = get_session()
        db_session = await anext(session_getter)
        self = cls(
            external_repository=ExternalRepository(),
            stats_repository=StatsRepository(session=db_session),
            user_repository=UserRepository(session=db_session)
        )

        data = await self.external_repository.get_user_data([nickname])

        now = dt.datetime.now()
        [await self._save_user_stats(stats, now) for stats in data]
        await self._load_video_stats([nickname], now)
        logger.debug(f"Add {len(data)} stats")

        try:
            await anext(session_getter)
        except StopAsyncIteration:
            pass

    @classmethod
    async def update_stats(cls):
        session_getter = get_session()
        db_session = await anext(session_getter)
        self = cls(
                external_repository=ExternalRepository(),
                stats_repository=StatsRepository(session=db_session),
                user_repository=UserRepository(session=db_session)
        )

        users = await self.user_repository.list()
        if users:
            nicknames = [user.nickname for user in users]
            now = dt.datetime.now()

            data = await self.external_repository.get_user_data(nicknames)
            [await self._save_user_stats(stats, now) for stats in data]
            await self._load_video_stats(nicknames, now)

            logger.debug(f"Add {len(data)} user stats")

        await self.stats_repository.clear_trend_videos()
        await self.stats_repository.clear_trend_hashtags()
        await self.stats_repository.clear_trend_songs()
        await self._load_trend_video()
        await self._load_trend_hashtags()
        await self._load_trend_songs()

        try:
            await anext(session_getter)
        except StopAsyncIteration:
            pass

