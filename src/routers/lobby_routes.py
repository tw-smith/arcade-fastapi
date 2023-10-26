import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from src.dependencies import get_db
from src.database.services.crud import LobbyCRUDService, get_lobby_service, UserCRUDService, get_user_service
from src.database.schemas import LobbyCreate
from src.database.models import User
from src.auth_dependencies import get_authorised_user
from src.websocket_dependencies import sio

router = APIRouter()


class LobbyItem(BaseModel):
    name: str
    public_id: str
    players: list[dict]


class LobbyItemCreate(BaseModel):
    name: str


@router.get('/lobbies', response_model=list[LobbyItem])
async def get_lobbies(current_user: Annotated[User, Depends(get_authorised_user)],
                      lobby_crud_service: LobbyCRUDService = Depends(get_lobby_service)):
    lobby_list = lobby_crud_service.list_all()
    return_list = []
    for item in lobby_list:
        player_list = []
        for player in item.players:
            player_list.append({'player_name': player.username})
        return_list.append({
            'name': item.name,
            'public_id': item.public_id,
            'players': player_list
        })
    return return_list


@router.post('/lobbies', response_model=LobbyItem, status_code=status.HTTP_201_CREATED)
async def create_lobby(lobby: LobbyItemCreate,
                       current_user: Annotated[User, Depends(get_authorised_user)],
                       lobby_crud_service: LobbyCRUDService = Depends(get_lobby_service)):
    new_lobby = LobbyCreate(
        name=lobby.name,
        public_id=str(uuid.uuid4())
    )
    db_obj = lobby_crud_service.create(new_lobby)
    lobby_db_obj = lobby_crud_service.add_user_to_lobby(db_obj.public_id, current_user)
    player_list = []
    for player in lobby_db_obj.players:
        player_list.append({'player_name': player.username})
    return {
        'name': lobby_db_obj.name,
        'public_id': lobby_db_obj.public_id,
        'players': player_list
    }

