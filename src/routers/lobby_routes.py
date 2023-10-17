import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, status, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.database.services.crud import LobbyCRUDService, get_lobby_service
from src.database.schemas import LobbyCreate
from src.database.models import User
from src.auth_dependencies import get_authorised_user




router = APIRouter()


class LobbyItem(BaseModel):
    name: str
    public_id: str
    players: list[dict]


class LobbyItemCreate(BaseModel):
    name: str

class LobbyItemJoin(BaseModel):
    public_id: str



@router.get('/lobbies', response_model=list[LobbyItem])
async def get_lobbies(lobby_crud_service: LobbyCRUDService = Depends(get_lobby_service)):
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


@router.post('/lobbies', response_model=list[LobbyItem], status_code=status.HTTP_201_CREATED)
async def create_lobby(lobby: LobbyItemCreate,
                       current_user: Annotated[User, Depends(get_authorised_user)],
                       lobby_crud_service: LobbyCRUDService = Depends(get_lobby_service)):
    print(current_user)
    new_lobby = LobbyCreate(
        name=lobby.name,
        public_id=str(uuid.uuid4())
    )
    db_obj = lobby_crud_service.create(new_lobby)
    lobby_db_obj = lobby_crud_service.add_user_to_lobby(lobby.name, current_user)
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
    print(lobby_list)
    return return_list

@router.post('/joinlobby')
async def join_lobby(lobby: LobbyItemCreate,
                     current_user: Annotated[User, Depends(get_authorised_user)],
                     lobby_crud_service: LobbyCRUDService = Depends(get_lobby_service)):
    lobby_db_obj = lobby_crud_service.add_user_to_lobby(lobby.name, current_user)




