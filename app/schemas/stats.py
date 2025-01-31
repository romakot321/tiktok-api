from pydantic import BaseModel, ConfigDict, computed_field
import datetime as dt


class StatsUserSchema(BaseModel):
    created_at: dt.datetime
    followers: int
    following: int
    likes: int
    diggs: int
    nickname: str

    model_config = ConfigDict(from_attributes=True)


class StatsVideoSchema(BaseModel):
    video_id: str
    views: int
    comments: int
    diggs: int
    shares: int
    nickname: str

    @computed_field
    @property
    def video_url(self) -> str:
        return f"https://www.tiktok.com/@{self.nickname}/video/{self.video_id}"

    model_config = ConfigDict(from_attributes=True)


class StatsSchema(BaseModel):
    user_stats: StatsUserSchema
    video_stats: list[StatsVideoSchema]

    model_config = ConfigDict(from_attributes=True)
