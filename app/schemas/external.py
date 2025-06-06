from pydantic import BaseModel, model_validator, AliasChoices, Field


class ExternalVideoDataSchema(BaseModel):
    class VideoMeta(BaseModel):
        originalCoverUrl: str

    class AuthorMeta(BaseModel):
        name: str
        avatar: str
        following: int = 0
        friends: int = 0
        fans: int = 0
        heart: int = 0
        video: int = 0
        digg: int = 0

    id: str | None = None
    playCount: int | None = None
    commentCount: int | None = None
    diggCount: int | None = None
    shareCount: int | None = None
    mediaUrls: list[str] | None = None
    videoMeta: VideoMeta | None = None
    authorMeta: AuthorMeta | None = None  # If error occured, all fields is null except error
    error: str | None = None

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
    publish_cnt: int
    rank: int


class ExternalTrendSongDataSchema(BaseModel):
    cover: str
    link: str
    title: str
    author: str
    rank: int

