from aiohttp import ClientSession
import os
import json
from loguru import logger

from app.schemas.external import ExternalDataSchema, ExternalTrendSongDataSchema, ExternalVideoDataSchema
from app.schemas.external import ExternalTrendHashtagDataSchema, ExternalTrendVideoDataSchema


class ExternalRepository:
    url = "https://api.brightdata.com"
    token_header = {"Authorization": "Bearer " + os.getenv("EXTERNAL_TOKEN", "")}
    apify_token = os.getenv("APIFY_TOKEN")

    async def get_user_data(self, nicknames: list[str]) -> list[ExternalDataSchema]:
        async with ClientSession() as session:
            resp = await session.post(
                f"https://api.apify.com/v2/acts/sandaliaapps~tiktok-user-data-extractor/run-sync-get-dataset-items?token={self.apify_token}",
                json={
                    "start_urls": [{"url": f"https://www.tiktok.com/@{name}", "method": "GET"} for name in nicknames],
                    "max_depth": 1
                }
            )
            data = await resp.json()
        logger.debug(f"Loaded {len(data)} users")
        return [ExternalDataSchema.model_validate(row) for row in data]

    async def get_video_data(self, nicknames: list[str]) -> list[ExternalVideoDataSchema]:
        async with ClientSession() as session:
            resp = await session.post(
                f"https://api.apify.com/v2/acts/clockworks~tiktok-profile-scraper/run-sync-get-dataset-items?token={self.apify_token}",
                json={
                    "profiles": nicknames,
                    "resultsPerPage": 5,
                    "shouldDownloadVideos": True,
                    "profileScrapeSections": [
                        "videos"
                    ]
                }
            )
            data = await resp.json()
        logger.debug(f"Loaded {len(data)} video")
        logger.debug([row for row in data if row.get("error") is not None])
        return [
            (ExternalVideoDataSchema.model_validate(row) if row.get('error') is None else ExternalVideoDataSchema(
                error=row.get('error'),
                authorMeta=ExternalVideoDataSchema.AuthorMeta(name=row.get("input", ''), avatar='')
            ))
            for row in data
        ]

    async def get_trend_hashtags_data(self) -> list[ExternalTrendHashtagDataSchema]:
        async with ClientSession() as session:
            resp = await session.post(
                f"https://api.apify.com/v2/acts/lexis-solutions~tiktok-trending-hashtags-scraper/run-sync-get-dataset-items?token={self.apify_token}",
                json={ "countryCode": "US", "maxItems": 30, "period": "7" }
            )
            data = await resp.json()
        logger.debug(f"Loaded {len(data)} hashtags")
        return [ExternalTrendHashtagDataSchema.model_validate(row) for row in data]

    async def get_trend_videos_data(self) -> list[ExternalTrendVideoDataSchema]:
        async with ClientSession() as session:
            resp = await session.post(
                f"https://api.apify.com/v2/acts/novi~fast-tiktok-api/run-sync-get-dataset-items?token={self.apify_token}",
                json={"isUnlimited": False, "limit": 2, "proxyConfiguration": {"useApifyProxy": False}, "publishTime": "ALL_TIME", "sortType": 0, "type": "TREND"}
            )
            data = await resp.json()
        logger.debug(f"Loaded {len(data)} videos")
        return [ExternalTrendVideoDataSchema.model_validate(row) for row in data]

    async def get_trend_songs_data(self) -> list[ExternalTrendSongDataSchema]:
        async with ClientSession() as session:
            resp = await session.post(
                f"https://api.apify.com/v2/acts/lexis-solutions~tiktok-trending-songs-scraper/run-sync-get-dataset-items?token={self.apify_token}",
                json={ "maxItems": 20, "countryCode": "US", "period": "7" }
            )
            data = await resp.json()
        logger.debug(f"Loaded {len(data)} songs")
        return [ExternalTrendSongDataSchema.model_validate(row) for row in data]

