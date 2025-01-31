from pydantic import BaseModel, ConfigDict
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
    comments: M[int]
    diggs: M[int]
    shares: M[int]

    model_config = ConfigDict(from_attributes=True)


class StatsSchema(BaseModel):
    user_stats: StatsUserSchema
    video_stats: list[StatsVideoSchema]
