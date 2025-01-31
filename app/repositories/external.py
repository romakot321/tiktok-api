from aiohttp import ClientSession
import os
import json
from loguru import logger

from app.schemas.external import ExternalDataSchema
from app.schemas.external import ExternalTrendHashtagDataSchema, ExternalTrendVideoDataSchema


class ExternalRepository:
    url = "https://api.brightdata.com"
    token_header = {"Authorization": "Bearer " + os.getenv("EXTERNAL_TOKEN", "")}
    apify_token = os.getenv("APIFY_TOKEN")

    async def trigger_data_collect(self, nicknames: list[str]) -> str:
        """Return task_id from external api"""
        async with ClientSession(base_url=self.url, headers=self.token_header) as session:
            resp = await session.post(
                '/datasets/v3/trigger?dataset_id=gd_l1villgoiiidt09ci&include_errors=true',
                json=[{"url": 'https://www.tiktok.com/@' + name} for name in nicknames]
            )
            assert resp.status == 200, await resp.text()
            data = await resp.json()
            logger.debug("Triggered collect: " + str(data))
            return data['snapshot_id']

    async def get_collected_data(self, task_id: str) -> list[ExternalDataSchema] | None:
        async with ClientSession(base_url=self.url, headers=self.token_header) as session:
            resp = await session.get(
                f'/datasets/v3/snapshot/{task_id}?format=json'
            )
            if resp.status == 202:
                return
            assert resp.status == 200, await resp.text()
            data = await resp.json()
        logger.debug("Data collected")
        return [ExternalDataSchema.model_validate(i) for i in data]

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

    async def get_trend_songs_data(self) -> list[ExternalTrendVideoDataSchema]:
        async with ClientSession() as session:
            resp = await session.post(
                f"https://api.apify.com/v2/acts/lexis-solutions~tiktok-trending-songs-scraper/run-sync-get-dataset-items?token={self.apify_token}",
                json={ "maxItems": 20, "countryCode": "US", "period": "7" }
            )
            data = await resp.json()
        logger.debug(f"Loaded {len(data)} songs")
        return [ExternalTrendSongDataSchema.model_validate(row) for row in data]

