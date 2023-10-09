import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from src.dependencies import get_db
from src.main import app
from src.database.services.crud import UserCreate, get_user_service, ScoreCreate, get_score_service
from src.database.models import User


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
    db_user_obj_1 = user_crud_service.create(new_user)

    new_user_2 = UserCreate(
        username="Mickey Mouse",
        public_id="Mickey Public ID"
    )
    db_user_obj_2 = user_crud_service.create(new_user_2)

    new_score_1 = ScoreCreate(
        date_set=datetime(2023, 12, 13, 14, 15),
        score_type="single",
        owner_id=db_user_obj_1.id,
        value=10
    )

    new_score_2 = ScoreCreate(
        date_set=datetime(2023, 12, 14, 15, 16),
        score_type="multi",
        owner_id=db_user_obj_1.id,
        value=20
    )

    new_score_3 = ScoreCreate(
        date_set=datetime(2023, 12, 15, 16, 17),
        score_type='single',
        owner_id=db_user_obj_2.id,
        value=23
    )

    new_score_4 = ScoreCreate(
        date_set=datetime(2023, 12, 16, 17, 18),
        score_type='single',
        owner_id=db_user_obj_1.id,
        value=24
    )

    score_crud_service = get_score_service(db)
    db_score_1_obj = score_crud_service.create(new_score_1)
    db_score_2_obj = score_crud_service.create(new_score_2)
    db_score_3_obj = score_crud_service.create(new_score_3)
    db_score_4_obj = score_crud_service.create(new_score_4)