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


class LobbyItemJoin(BaseModel):
    public_id: str


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


@sio.event
async def join_lobby_request(sid,
                             public_id):
    print(f"SID: {sid}")
    db = next(get_db())
    lobby_crud_service: LobbyCRUDService = get_lobby_service(db)
    user_crud_service: UserCRUDService = get_user_service(db)
    session = await sio.get_session(sid)
    user = user_crud_service.search_by_username(session['username'])
    # user = await get_user_from_sid(sid)
    lobby_db_obj = lobby_crud_service.add_user_to_lobby(public_id, user)
    # await sio.save_session(sid, {'lobby_public_id': public_id})
    db.close()
    await sio.enter_room(sid, session['lobby_public_id'])
    await sio.emit('lobby_status_update', get_lobby_status(public_id), room=session['lobby_public_id'])


@sio.event
async def leave_lobby(sid):
    db = next(get_db())
    lobby_crud_service: LobbyCRUDService = get_lobby_service(db)
    user_crud_service: UserCRUDService = get_user_service(db)
    session = await sio.get_session(sid)
    user = user_crud_service.search_by_username(session['username'])
    lobby_crud_service.remove_user_from_lobby(user)
    db.close()
    await sio.leave_room(sid, session['lobby_public_id'])
    await sio.emit('lobby_status_update', get_lobby_status(session['lobby_public_id']), room=session['lobby_public_id'])
    await sio.disconnect(sid)


@sio.event
async def player_ready_toggle(sid):
    print(f"SID: {sid}")
    db = next(get_db())
    user_crud_service: UserCRUDService = get_user_service(db)
    lobby_crud_service: LobbyCRUDService = get_lobby_service(db)
    session = await sio.get_session(sid)
    user = user_crud_service.search_by_username(session['username'])
    #user = await get_user_from_sid(sid)
    if user.is_ready:
        is_ready = False
    else:
        is_ready = True
    user_crud_service.user_ready(user, is_ready)
    print(user.is_ready)
    player_list = get_lobby_status(session['lobby_public_id'])
    print(player_list)
    db.close()
    await sio.emit('lobby_status_update', player_list, room=session['lobby_public_id'])


@sio.event
async def connect(sid, auth):
    print(f"SID: {sid}")
    db = next(get_db())
    user_crud_service: UserCRUDService = get_user_service(db)
    user = await get_authorised_user(auth.get('HTTP_TOKEN'), user_crud_service)
    print(user.username)
    db.close()
    await sio.save_session(sid, {'username': user.username,
                                 'lobby_public_id': auth.get('HTTP_LOBBY_ID')})


@sio.event
async def start_game_request(sid, public_id):
    print('start game request')
    print(sid)
    await sio.emit('start_game', room=public_id)
    await sio.emit('set_p1', room=sid)
    await sio.emit('set_p2', room=public_id, skip_sid=sid)

@sio.event
async def set_initial_food(sid, data):
    session = await sio.get_session(sid)
    await sio.emit('set_initial_food', data, room=session['lobby_public_id'], skip_sid=sid)


@sio.event
async def game_update(sid, data):
    session = await sio.get_session(sid)
    await sio.emit('new_game_parameters', data, room=session['lobby_public_id'], skip_sid=sid)


def get_lobby_status(public_id: str):
    db = next(get_db())
    lobby_crud_service: LobbyCRUDService = get_lobby_service(db)
    print(f"search lobby id: {public_id}")
    lobby_db_obj = lobby_crud_service.get_lobby_by_public_id(public_id)
    player_list = []
    for player in lobby_db_obj.players:
        player_list.append({
            'username': player.username,
            'is_ready': player.is_ready,
            'is_host': player.is_host
        })
    return player_list
