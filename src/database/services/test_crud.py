from datetime import datetime
from src.database.services.crud import get_user_service, get_score_service, get_lobby_service
from src.database.schemas import UserCreate, ScoreCreate, LobbyCreate


def test_database_create(db):
    new_user = UserCreate(
        username="Test Username",
        public_id="Test Public ID"
    )
    user_crud_service = get_user_service(db)
    db_user_obj = user_crud_service.create(new_user)
    print(type(db_user_obj.username))
    print(db_user_obj.username)
    assert db_user_obj.username == "Test Username"
    assert db_user_obj.public_id is not None

    new_score = ScoreCreate(
        date_set=datetime(2023, 12, 13, 14, 15),
        score_type="single",
        owner_id=1,
        value=10
    )
    score_crud_service = get_score_service(db)
    db_score_obj = score_crud_service.create(new_score)
    assert db_score_obj.value is 10
    assert db_score_obj.player.username == "Test Username"

    new_lobby = LobbyCreate(
        name="Test Lobby"
    )
    lobby_crud_service = get_lobby_service(db)
    db_lobby_obj = lobby_crud_service.create(new_lobby)
    assert db_lobby_obj.name == "Test Lobby"
    assert db_lobby_obj.public_id is not None


def test_database_get_and_list(db, seed_db):
    user_crud_service = get_user_service(db)
    db_user_obj = user_crud_service.get(1)
    assert db_user_obj.username == "Joe Bloggs"
    assert db_user_obj.scores is not None
    score_crud_service = get_score_service(db)
    db_score_obj = score_crud_service.get(1)
    assert db_score_obj.value is 10
    assert db_score_obj.player.username == "Joe Bloggs"
    db_score_list = score_crud_service.list_all()
    assert len(db_score_list) is 4


def test_database_search_by_username(db, seed_db):
    user_crud_service = get_user_service(db)
    db_user_obj = user_crud_service.search_by_username("Joe Bloggs")
    assert db_user_obj is not None
    assert db_user_obj.username == "Joe Bloggs"


def test_database_search_by_public_id(db, seed_db):
    user_crud_service = get_user_service(db)
    db_user_obj = user_crud_service.search_by_public_id('Mickey Public ID')
    assert db_user_obj is not None
    assert db_user_obj.username == "Mickey Mouse"


def test_database_delete(db, seed_db):
    user_crud_service = get_user_service(db)
    db_user_obj = user_crud_service.delete(1)
    db_user_obj_2 = user_crud_service.delete(2)
    db_search_user_obj = user_crud_service.search_by_username("Joe Bloggs")
    assert db_search_user_obj is None
    score_crud_service = get_score_service(db)
    db_score_list = score_crud_service.list_all()
    assert len(db_score_list) is 0


def test_get_high_scores(db, seed_db):
    score_crud_service = get_score_service(db)
    score_list = score_crud_service.get_high_scores('single')
    assert len(score_list) is 3
    score_list_player_filter = score_crud_service.get_high_scores('single', user_public_id='Mickey Public ID')
    assert len(score_list_player_filter) is 1
    assert score_list_player_filter[0].player.username == 'Mickey Mouse'
    score_list_count_limit = score_crud_service.get_high_scores('single', count=2)
    assert len(score_list_count_limit) is 2



