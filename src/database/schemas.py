import uuid

from pydantic import BaseModel
from datetime import datetime
from typing import Literal
from pydantic.types import UUID4


class ScoreBase(BaseModel):
    date_set: datetime
    score_type: Literal["multi", "single"]
    owner_id: int
    value: int


class ScoreCreate(ScoreBase):
    pass


class Score(ScoreBase):
    id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str
    public_id: str
    is_active: bool = False
    is_host: bool = False
    is_ready: bool = False
    scores: list[Score] = []
    lobby_id: int = None


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class LobbyBase(BaseModel):
    name: str


class LobbyCreate(LobbyBase):
    pass


class Lobby(LobbyBase):
    id: int
    public_id: str
    players: list[User] = []

    class Config:
        orm_mode = True













