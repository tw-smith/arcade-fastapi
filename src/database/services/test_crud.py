import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from ..models import User
from src.main import app
from src.dependencies import get_db
from src.database.services.crud import UserCRUDService, get_user_service, \
    ScoreCRUDService, get_score_service, \
    LobbyCRUDService, get_lobby_service
from src.database.schemas import UserCreate, ScoreCreate, LobbyCreate

SQLALCHEMY_DATABASE_URL = 'sqlite:///./test.db'


@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    User.metadata.create_all(bind=engine)
    yield engine


@pytest.fixture(scope="function")
def db(db_engine):
    engine = db_engine
    connection = engine.connect()
    transaction = connection.begin()
    db = Session(bind=connection)
    yield db
    db.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def seed_db(db):
    new_user = UserCreate(
        username="Joe Bloggs",
        public_id="Test Public ID"
    )
    user_crud_service = get_user_service(db)
    db_user_obj = user_crud_service.create(new_user)

    new_score_1 = ScoreCreate(
        date_set=datetime(2023, 12, 13, 14, 15),
        score_type="single",
        owner_id=db_user_obj.id,
        value=10
    )

    new_score_2 = ScoreCreate(
        date_set=datetime(2023, 12, 14, 15, 16),
        score_type="multi",
        owner_id=db_user_obj.id,
        value=20
    )
    score_crud_service = get_score_service(db)
    db_score_1_obj = score_crud_service.create(new_score_1)
    db_score_2_obj = score_crud_service.create(new_score_2)


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
    assert len(db_score_list) is 2


def test_database_search_by_username(db, seed_db):
    user_crud_service = get_user_service(db)
    db_user_obj = user_crud_service.search_by_username("Joe Bloggs")
    assert db_user_obj is not None
    assert db_user_obj.username == "Joe Bloggs"


def test_database_delete(db, seed_db):
    user_crud_service = get_user_service(db)
    db_user_obj = user_crud_service.delete(1)
    db_search_user_obj = user_crud_service.search_by_username("Joe Bloggs")
    assert db_search_user_obj is None
    score_crud_service = get_score_service(db)
    db_score_list = score_crud_service.list_all()
    assert len(db_score_list) is 0



