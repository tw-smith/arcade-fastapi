from jose import jwt
from src.database.services.crud import get_score_service



def test_get_highscores(client, db, seed_db):
    response = client.get('/highscores?score_type=single')
    assert response.status_code == 200
    assert len(response.json()) == 3
    response = client.get('/highscores?score_type=multi')
    assert response.status_code == 200
    assert len(response.json()) == 1
    response = client.get('/highscores?score_type=single&count=2')
    assert response.status_code == 200
    assert len(response.json()) == 2
    response = client.get('/highscores?score_type=single&userid=Mickey%20Public%20ID')
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['player'] == 'Mickey Mouse'


def test_post_highscore(client, db, seed_db, valid_jwt):
    headers = {'Authorization': f"Bearer {valid_jwt}"}
    response = client.post('/highscores',
                           headers=headers,
                           json={'score_type': 'single', 'value': 75})
    assert response.status_code == 201
    score_service = get_score_service(db)
    score_list = score_service.get_high_scores('single', user_public_id='Mickey Public ID')
    assert len(score_list) == 2
    assert score_list[0].value == 75


def test_post_highscore_no_token(client, db, seed_db):
    response = client.post("/highscores",
                           json={'score_type': 'single', 'value': 75})
    assert response.status_code == 401


def test_post_highscore_no_such_user(client, db, seed_db, no_user_jwt):
    response = client.post(f"/highscores?token={no_user_jwt}",
                           json={'score_type': 'single', 'value': 75})
    token_payload = jwt.decode(no_user_jwt, key='', options={'verify_signature': False})
    assert token_payload.get("sub") == "No Such User"
    assert response.status_code == 401







