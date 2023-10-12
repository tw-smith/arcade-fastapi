

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

def test_create_lobby_no_token(client, db, seed_db):
    response = client.post('/lobbies',
                           json={'name': 'test_lobby_3'})
    assert response.status_code == 401

def test_create_lobby_no_such_user(client, db, seed_db, no_user_jwt):
    response = client.post(f"/lobbies?token={no_user_jwt}",
                           json={'name': 'test_lobby_3'})
    assert response.status_code == 401




