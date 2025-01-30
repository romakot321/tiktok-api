from aiohttp import ClientSession
import os
import json
from loguru import logger

from app.schemas.external import ExternalDataSchema


class ExternalRepository:
    url = "https://api.brightdata.com"
    token_header = {"Authorization": "Bearer " + os.getenv("EXTERNAL_TOKEN")}

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

