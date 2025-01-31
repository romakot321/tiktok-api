from pydantic import BaseModel, ConfigDict


class UserSchema(BaseModel):
    id: int
    nickname: str
    avatar: str

    model_config = ConfigDict(from_attributes=True)


class UserCreateSchema(BaseModel):
    app_id: str
    app_bundle: str
    nickname: str

