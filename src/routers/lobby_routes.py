import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from src.database.services.crud import LobbyCRUDService, get_lobby_service
from src.database.schemas import LobbyCreate
from src.database.models import User
from src.auth_dependencies import get_authorised_user




router = APIRouter()


class LobbyItem(BaseModel):
    name: str



@router.get('/lobbies', response_model=list[LobbyItem])
async def get_lobbies(lobby_crud_service: LobbyCRUDService = Depends(get_lobby_service)):
    lobby_list = lobby_crud_service.list_all()
    return_list = []
    for item in lobby_list:
        return_list.append({'name': item.name})
    return return_list


@router.post('/lobbies', response_model=list[LobbyItem], status_code=status.HTTP_201_CREATED)
async def create_lobby(lobby: LobbyItem,
                       current_user: Annotated[User, Depends(get_authorised_user)],
                       lobby_crud_service: LobbyCRUDService = Depends(get_lobby_service)):
    new_lobby = LobbyCreate(
        name=lobby.name,
        public_id=str(uuid.uuid4())
    )
    db_obj = lobby_crud_service.create(new_lobby)
    lobby_list = lobby_crud_service.list_all()
    return_list = []
    for item in lobby_list:
        return_list.append({'name': item.name})
    return return_list

