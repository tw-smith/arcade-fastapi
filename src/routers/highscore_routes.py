from fastapi import APIRouter, Depends, status
from typing import Literal, List
from pydantic import BaseModel
from datetime import datetime
from src.database.services.crud import ScoreCRUDService, get_score_service, UserCRUDService, get_user_service
from src.database.schemas import ScoreCreate
from src.database.models import User

router = APIRouter()


class HighScoreItem(BaseModel):
    player: str
    value: int


class HighScoreSubmitItem(BaseModel):
    user_public_id: str
    value: int


@router.get("/highscores", response_model=list[HighScoreItem])
async def get_high_scores(score_type: Literal['multi', 'single'],
                          userid: str = None,
                          count: int = 10,
                          score_crud_service: ScoreCRUDService = Depends(get_score_service)):
    score_list = score_crud_service.get_high_scores(score_type, count, userid)
    return_list = []
    for item in score_list:
        return_list.append({'player': item.player.username, 'value': item.value})
      #TODO: this doesn't pick up incorrect type for player or value but does pick up if one is misisng
        # also feel like there should be a better way to do this than iterating through score list
    return return_list


@router.post("/highscores", status_code=status.HTTP_201_CREATED, response_model=List[HighScoreItem])
async def post_high_score(score_type: Literal['multi', 'single'],
                          high_score: HighScoreSubmitItem,
                          score_crud_service: ScoreCRUDService = Depends(get_score_service),
                          user_crud_service: UserCRUDService = Depends(get_user_service)):
    db_user = user_crud_service.search_by_public_id(high_score.user_public_id)
    new_score = ScoreCreate(
        date_set=datetime.utcnow(),
        score_type=score_type,
        owner_id=db_user.id,
        value=high_score.value
    )
    db_obj = score_crud_service.create(new_score)
    score_list = score_crud_service.get_high_scores(score_type)
    return_list = []
    for item in score_list:
        return_list.append({'player': item.player.username, 'value': item.value})
        # TODO: this doesn't pick up incorrect type for player or value but does pick up if one is misisng
    return return_list
