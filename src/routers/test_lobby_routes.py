from src.database.services.crud import LobbyCRUDService, get_lobby_service
import socketio

def test_get_lobbies(client, db, seed_db):
    response = client.get('/lobbies')
    assert len(response.json()) == 2
    assert response.json()[0]['name'] == 'test_lobby_1'
    assert response.json()[0]['public_id'] == 'lobby_public_id_1'


def test_create_lobby(client, db, seed_db, valid_jwt):
    headers = {'Authorization': f"Bearer {valid_jwt}"}
    response = client.post('/lobbies',
                           headers=headers,
                           json={'name': 'test_lobby_3'})
    print(response.json())
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
    headers = {'Authorization': f"Bearer {no_user_jwt}"}
    response = client.post('/lobbies',
                           headers=headers,
                           json={'name': 'test_lobby_3'})
    assert response.status_code == 401


def test_join_lobby(client, db, seed_db, valid_jwt, valid_jwt_2, valid_jwt_3):
    headers = {'Authorization': f"Bearer {valid_jwt}"}
    response = client.post('/joinlobby',
                           headers=headers,
                           json={'name': 'test_lobby_2'})
    assert response.status_code == 200
    lobby_crud_service: LobbyCRUDService = get_lobby_service(db)
    db_obj = lobby_crud_service.get_lobby_by_name('test_lobby_2')
    assert len(db_obj.players) == 1
    assert db_obj.players[0].public_id == 'Mickey Public ID'
    headers = {'Authorization': f"Bearer {valid_jwt_2}"}
    response = client.post('/joinlobby',
                           headers=headers,
                           json={'name': 'test_lobby_2'})
    assert response.status_code == 200
    db_obj = lobby_crud_service.get_lobby_by_name('test_lobby_2')
    assert len(db_obj.players) == 2
    assert db_obj.players[0].public_id == 'Test Public ID'
    assert db_obj.players[1].public_id == 'Mickey Public ID'

    # While we have a full lobby, test for full lobby reject join
    headers = {'Authorization': f"Bearer {valid_jwt_3}"}
    response = client.post('/joinlobby',
                           headers=headers,
                           json={'name': 'test_lobby_2'})
    assert response.status_code == 409
    assert response.json()['detail'] == 'Lobby full'


async def test_ws(client):
    wsclient = socketio.AsyncClient()
    await wsclient.connect('http://127.0.0.1:8000')
    await wsclient.emit('testev')
    print(wsclient)
    assert 1==2

    @wsclient.on("test_emit")
    def foo(data):
        print(data)
        assert data == 'test_msg'







