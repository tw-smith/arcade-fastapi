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


def test_post_highscore(client, db, seed_db):
    response = client.post('/highscores?score_type=single',
                           json={'user_public_id': 'Mickey Public ID', 'value': 75})
    assert response.status_code == 201
    score_service = get_score_service(db)
    score_list = score_service.get_high_scores('single', user_public_id='Mickey Public ID')
    assert len(score_list) == 2
    assert score_list[0].value == 75




