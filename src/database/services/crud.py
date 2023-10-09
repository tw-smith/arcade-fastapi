from typing import Any, Optional, TypeVar, Generic, List, Literal
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import Depends
from fastapi.exceptions import HTTPException
from ..models import User, Score, Lobby
from ..schemas import UserCreate, ScoreCreate, LobbyCreate
from src.dependencies import get_db
from src.database.services.database import Base


ModelType = TypeVar('ModelType', bound=Base)
SchemaCreateType = TypeVar('SchemaCreateType', bound=BaseModel)


class BaseCRUDService(Generic[ModelType, SchemaCreateType]): #TODO: understand this generic typing
    def __init__(self, model, db_session: Session):
        self.model = model
        self.db_session = db_session

    def get(self, id: Any) -> Optional[ModelType]:
        db_obj = self.db_session.get(self.model, id)
        if db_obj is None:
            raise HTTPException(status_code=404, detail='Not Found')
        return db_obj

    def list_all(self) -> List[ModelType]:
        db_list = self.db_session.query(self.model).all()
        if db_list is None:
            raise HTTPException(status_code=404, detail='Not Found')
        return db_list

    def create(self, obj: SchemaCreateType) -> ModelType:
        db_obj: ModelType = self.model(**obj.dict())
        self.db_session.add(db_obj)
        try:
            self.db_session.commit()
        except IntegrityError as e:
            raise HTTPException(status_code=409, detail="Database creation error")
        return db_obj

    def delete(self, id: Any) -> ModelType:
        db_obj = self.db_session.get(self.model, id)
        self.db_session.delete(db_obj)
        self.db_session.commit()
        return db_obj


class UserCRUDService(BaseCRUDService[User, UserCreate]):
    def __init__(self, db_session: Session):
        super().__init__(User, db_session)

    def search_by_username(self, username) -> ModelType:
        db_obj: ModelType = self.db_session.query(self.model).filter(self.model.username == username).first()
        return db_obj

    def search_by_public_id(self, user_public_id) -> ModelType:
        db_obj: ModelType = self.db_session.query(self.model).filter(self.model.public_id == user_public_id).first()
        return db_obj


def get_user_service(db_session: Session = Depends(get_db)) -> UserCRUDService:
    return UserCRUDService(db_session)


class ScoreCRUDService(BaseCRUDService[Score, ScoreCreate]):
    def __init__(self, db_session: Session):
        super().__init__(Score, db_session)

    def get_high_scores(self, score_type: Literal["multi", "single"], count: int = 10, user_public_id: str = None) -> List[Score]:
        if user_public_id:
            db_list = self.db_session.query(Score).filter(Score.player.has(public_id=user_public_id), Score.score_type == score_type).order_by(Score.value.desc()).limit(count).all()
        else:
            db_list = self.db_session.query(Score).filter(Score.score_type == score_type).order_by(Score.value.desc()).limit(count).all()
        return db_list

def get_score_service(db_session: Session = Depends(get_db)) -> ScoreCRUDService:
    return ScoreCRUDService(db_session)


class LobbyCRUDService(BaseCRUDService[Lobby, LobbyCreate]):
    def __init__(self, db_session: Session):
        super().__init__(Lobby, db_session)


def get_lobby_service(db_session: Session = Depends(get_db)) -> LobbyCRUDService:
    return LobbyCRUDService(db_session)

