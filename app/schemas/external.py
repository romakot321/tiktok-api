from pydantic import BaseModel, model_validator, AliasChoices, Field


class ExternalVideoDataSchema(BaseModel):
    class VideoMeta(BaseModel):
        originalCoverUrl: str

    class AuthorMeta(BaseModel):
        name: str

    id: str
    playCount: int
    commentCount: int
    diggCount: int
    shareCount: int
    mediaUrls: list[str]
    videoMeta: VideoMeta
    authorMeta: AuthorMeta

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
    class Data(BaseModel):
        class Stats(BaseModel):
            followerCount: int
            followingCount: int
            heartCount: int
            videoCount: int
            diggCount: int

        class User(BaseModel):
            avatarMedium: str
            uniqueId: str

        user: User
        stats: Stats

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

    userInfo: Data


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

