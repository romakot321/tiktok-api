from pydantic import BaseModel, model_validator, AliasChoices, Field


class ExternalVideoDataSchema(BaseModel):
    post_id: str
    play_count: int
    comment_count: int
    digg_count: int
    share_count: int
    preview_image: str
    video_url: str

    @model_validator(mode="before")
    @classmethod
    def strip_keys(cls, state) -> dict:
        if not isinstance(state, dict):
            return state
        for key, value in list(state.items()):
            if isinstance(key, str):
                key = key.strip(' ')
            state[key] = value
        return state


class ExternalDataSchema(BaseModel):
    account_id: str
    followers: int
    following: int
    likes: int
    videos_count: int
    digg_count: int
    profile_pic_url_hd: str

    @model_validator(mode="before")
    @classmethod
    def strip_keys(cls, state) -> dict:
        if not isinstance(state, dict):
            return state
        for key, value in state.items():
            if isinstance(key, str):
                key = key.strip(' ')
            state[key] = value
        return state


class ExternalTrendVideoDataSchema(BaseModel):
    class VideoSchema(BaseModel):
        class VideoCoverSchema(BaseModel):
            url_list: list[str]

        cover: VideoCoverSchema

    class StatisticsSchema(BaseModel):
        play_count: int

    desc: str
    share_url: str
    statistics: StatisticsSchema
    video: VideoSchema


class ExternalTrendHashtagDataSchema(BaseModel):
    hashtag_name: str
    video_views: int


class ExternalTrendSongDataSchema(BaseModel):
    cover: str
    link: str
    title: str
    author: str

