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

