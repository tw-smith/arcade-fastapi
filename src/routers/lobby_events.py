import logging

from fastapi import APIRouter
from src.dependencies import get_db
from src.database.services.crud import UserCRUDService, LobbyCRUDService, get_user_service, get_lobby_service
from src.websocket_dependencies import sio
from src.auth_dependencies import get_authorised_user
from fastapi.exceptions import HTTPException
from src.dependencies import logger

router = APIRouter()


def get_lobby_status(public_id: str):
    logger.warning(f"Public ID: {public_id}")
    db = next(get_db())
    lobby_crud_service: LobbyCRUDService = get_lobby_service(db)
    print(f"search lobby id: {public_id}")
    lobby_db_obj = lobby_crud_service.get_lobby_by_public_id(public_id)
    if lobby_db_obj is None: # lobby doesn't exist any more because last player has left
        return []
    player_list = []
    for player in lobby_db_obj.players:
        player_list.append({
            'username': player.username,
            'is_ready': player.is_ready,
            'is_host': player.is_host
        })
    return player_list


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
async def disconnect(sid):
    db = next(get_db())
    lobby_crud_service: LobbyCRUDService = get_lobby_service(db)
    user_crud_service: UserCRUDService = get_user_service(db)
    session = await sio.get_session(sid)
    user = user_crud_service.search_by_username(session['username'])
    user_crud_service.user_ready(user, False)
    lobby_crud_service.remove_user_from_lobby(user)
    db.close()
    await sio.leave_room(sid, session['lobby_public_id'])
    try:
        await sio.emit('lobby_status_update', get_lobby_status(session['lobby_public_id']), room=session['lobby_public_id'])
    except HTTPException as e:
        pass
    # await sio.disconnect(sid)

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
    try:
        lobby_db_obj = lobby_crud_service.add_user_to_lobby(public_id, user)
    except HTTPException as e:
        if e.status_code == 409:
            return 'Full'
        if e.status_code == 404:
            return 'Not Found'

    db.close()
    await sio.enter_room(sid, session['lobby_public_id'])
    await sio.emit('lobby_status_update', get_lobby_status(public_id), room=session['lobby_public_id'])


@sio.event
async def player_ready_toggle(sid):
    print(f"SID: {sid}")
    db = next(get_db())
    user_crud_service: UserCRUDService = get_user_service(db)
    lobby_crud_service: LobbyCRUDService = get_lobby_service(db)
    session = await sio.get_session(sid)
    user = user_crud_service.search_by_username(session['username'])
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