from fastapi import APIRouter
from src.websocket_dependencies import sio

router = APIRouter()

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
async def snake_update(sid, data):
    session = await sio.get_session(sid)
    await sio.emit('new_snake_parameters', data, room=session['lobby_public_id'], skip_sid=sid)


@sio.event
async def food_update(sid, data):
    session = await sio.get_session(sid)
    await sio.emit('new_food_parameters', data, room=session['lobby_public_id'], skip_sid=sid)


@sio.event
async def game_params_update(sid, data):
    session = await sio.get_session(sid)
    await sio.emit('new_game_parameters', data, room=session['lobby_public_id'], skip_sid=sid)