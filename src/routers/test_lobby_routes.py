

def test_get_lobbies(client, db, seed_db):
    response = client.get('/lobbies')
    assert len(response.json()) == 2
    assert response.json()[0]['name'] == 'test_lobby_1'


def test_create_lobby(client, db, seed_db):
    response = client.post('/lobbies',
                           json={'name': 'test_lobby_3'})
    assert response.status_code == 201
    assert len(response.json()) == 3
    assert response.json()[2]['name'] == 'test_lobby_3'




