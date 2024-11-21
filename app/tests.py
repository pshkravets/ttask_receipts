import pytest

from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app import app
from models import Base, get_db, User
from utils import decode_access_token


TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def test_client(db_session):

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def user_payload():
    return {
        'login': 'test login',
        'username': 'test username',
        'password': 'testpassword'
    }


@pytest.fixture
def receipt_payload():
    return {
        "payment": {
            "type": "cash",
            "amount": 200.0
        },
        "products": [
            {"name": "Apple", "price": 1.5, "quantity": 10},
            {"name": "Banana", "price": 1.2, "quantity": 5}
        ]
    }

def signup_request(user_payload, test_client):
    return test_client.post('/registration/', params=user_payload)


def get_gwt(user_payload, test_client):
    signup_request(user_payload, test_client)
    return test_client.get('/authorize/', params=user_payload).json()['token']

def create_receipt(user_payload, test_client, receipt_payload):
    token = get_gwt(user_payload, test_client)
    return test_client.post('/receipt/', headers={'Authorization': f'Bearer {token}'}, json=receipt_payload)


def test_registration_api(test_client, db_session, user_payload):
    response = signup_request(user_payload, test_client)
    user = db_session.query(User).filter_by(login=user_payload['login']).first()
    assert response.status_code == 201
    assert user.username == user_payload['username']


def test_authorization(test_client, db_session, user_payload):
    signup_request(user_payload, test_client)
    response = test_client.get('/authorize/', params=user_payload)
    assert response.status_code == 200
    assert decode_access_token(response.json()['token'])['sub'] == user_payload['login']


def test_create_receipt(test_client, db_session, user_payload, receipt_payload):
    response = create_receipt(user_payload, test_client, receipt_payload)
    assert response.status_code == 200
    assert response.json()['payment'] == receipt_payload['payment']


def test_users_receipt_list(test_client, db_session, user_payload, receipt_payload):
    token = get_gwt(user_payload, test_client)
    create_response = create_receipt(user_payload, test_client, receipt_payload)
    response = test_client.get('/my_receipts/', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert create_response.json() == response.json()[0]


def test_public_receipts(test_client, db_session, user_payload, receipt_payload):
    create_response = create_receipt(user_payload, test_client, receipt_payload)
    response = test_client.get(f'/receipt_text/{create_response.json()["id"]}/')
    assert response.status_code == 200


def test_wrong_authorization_credentials(test_client, db_session, user_payload):
    signup_request(user_payload, test_client)
    response = test_client.get('/authorize/', params={'login': 'wronglogin', 'password': 'wrongpasswd'})
    assert response.status_code == 400
    assert response.json()['detail'] == 'Your login or password is incorrect'


def registration_with_existing_login(test_client, db_session, user_payload):
    signup_request(user_payload, test_client)
    response = signup_request(user_payload, test_client)
    assert response.status_code == 400
    assert response.json()['detail'] == 'User with this login already exists'


def get_receipt_wrong_id(test_client, db_session, user_payload, receipt_payload):
    token = get_gwt(user_payload, test_client)
    create_receipt(user_payload, test_client, receipt_payload)
    response = test_client('/my_receipts/{receipt_id}', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 404
    assert response.json()['detail'] == 'Receipt with this id doesn\'t exist'