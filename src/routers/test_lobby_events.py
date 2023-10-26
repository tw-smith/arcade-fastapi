import pytest
from fastapi.exceptions import HTTPException
from src.database.services.crud import UserCRUDService, get_user_service, LobbyCRUDService, get_lobby_service
from src.routers.lobby_events import get_lobby_status

# def test_get_lobby_status(db, seed_db): TODO fix this test
#     user_crud_service: UserCRUDService = get_user_service(db)
#     lobby_crud_service: LobbyCRUDService = get_lobby_service(db)
#     with pytest.raises(HTTPException) as e:
#         result = get_lobby_status('dummy_public_id')
#     user = user_crud_service.get(1)
#     lobby = lobby_crud_service.get(1)
#     lobby_crud_service.add_user_to_lobby(lobby.public_id, user)
#     result = get_lobby_status(lobby.public_id)
#     assert len(result) == 1
#     assert result[0] == {
#         'username': 'Joe Bloggs',
#         'is_ready': False,
#         'is_host': False
#     }