from src.database.services.crud import LobbyCRUDService, get_lobby_service

def test_get_lobbies(client, db, seed_db):
    response = client.get('/lobbies')
    assert len(response.json()) == 2
    assert response.json()[0]['name'] == 'test_lobby_1'


def test_create_lobby(client, db, seed_db, valid_jwt):
    response = client.post(f"/lobbies?token={valid_jwt}",
                           json={'name': 'test_lobby_3'})
    assert response.status_code == 201
    assert len(response.json()) == 3
    assert response.json()[2]['name'] == 'test_lobby_3'
    lobby_crud_service: LobbyCRUDService = get_lobby_service(db)
    db_obj = lobby_crud_service.get(3)
    assert len(db_obj.players) == 1
    assert db_obj.players[0].public_id == 'Mickey Public ID'


def test_create_lobby_no_token(client, db, seed_db):
    response = client.post('/lobbies',
                           json={'name': 'test_lobby_3'})
    assert response.status_code == 401


def test_create_lobby_no_such_user(client, db, seed_db, no_user_jwt):
    response = client.post(f"/lobbies?token={no_user_jwt}",
                           json={'name': 'test_lobby_3'})
    assert response.status_code == 401


def test_join_lobby(client, db, seed_db, valid_jwt, valid_jwt_2, valid_jwt_3):
    response = client.post(f"/joinlobby?token={valid_jwt}",
                           json={'name': 'test_lobby_2'})
    assert response.status_code == 200
    lobby_crud_service: LobbyCRUDService = get_lobby_service(db)
    db_obj = lobby_crud_service.get_lobby_by_name('test_lobby_2')
    assert len(db_obj.players) == 1
    assert db_obj.players[0].public_id == 'Mickey Public ID'
    response = client.post(f"/joinlobby?token={valid_jwt_2}",
                           json={'name': 'test_lobby_2'})
    assert response.status_code == 200
    db_obj = lobby_crud_service.get_lobby_by_name('test_lobby_2')
    assert len(db_obj.players) == 2
    assert db_obj.players[0].public_id == 'Test Public ID'
    assert db_obj.players[1].public_id == 'Mickey Public ID'

    # While we have a full lobby, test for full lobby reject join
    response = client.post(f"/joinlobby?token={valid_jwt_3}",
                           json={'name': 'test_lobby_2'})
    assert response.status_code == 409
    assert response.json()['detail'] == 'Lobby full'




