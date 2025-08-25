import pytest
from fastapi import HTTPException, status
from backend.core.auth import AuthenticationService, UserCreate

class DummySessionManager:
    pass

@pytest.fixture
def auth_service():
    return AuthenticationService(DummySessionManager(), secret_key="testsecret")

def test_create_user_success(auth_service):
    user_data = UserCreate(username="testuser", email="test@example.com", password="password123")
    user = pytest.run(auth_service.create_user(user_data))
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.is_active

def test_create_user_duplicate_username(auth_service):
    user_data = UserCreate(username="dupuser", email="dup1@example.com", password="password123")
    pytest.run(auth_service.create_user(user_data))
    user_data2 = UserCreate(username="dupuser", email="dup2@example.com", password="password123")
    with pytest.raises(HTTPException) as exc:
        pytest.run(auth_service.create_user(user_data2))
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Username already exists" in str(exc.value.detail)

def test_create_user_duplicate_email(auth_service):
    user_data = UserCreate(username="user1", email="dupemail@example.com", password="password123")
    pytest.run(auth_service.create_user(user_data))
    user_data2 = UserCreate(username="user2", email="dupemail@example.com", password="password123")
    with pytest.raises(HTTPException) as exc:
        pytest.run(auth_service.create_user(user_data2))
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Email already exists" in str(exc.value.detail)

def test_authenticate_user_success(auth_service):
    user_data = UserCreate(username="authuser", email="auth@example.com", password="password123")
    pytest.run(auth_service.create_user(user_data))
    user = pytest.run(auth_service.authenticate_user("authuser", "password123"))
    assert user is not None
    assert user.username == "authuser"

def test_authenticate_user_wrong_password(auth_service):
    user_data = UserCreate(username="wrongpass", email="wrongpass@example.com", password="password123")
    pytest.run(auth_service.create_user(user_data))
    user = pytest.run(auth_service.authenticate_user("wrongpass", "wrongpassword"))
    assert user is None

def test_authenticate_user_inactive(auth_service):
    user_data = UserCreate(username="inactive", email="inactive@example.com", password="password123")
    user = pytest.run(auth_service.create_user(user_data))
    user.is_active = False
    auth_service.users[user.user_id] = user
    result = pytest.run(auth_service.authenticate_user("inactive", "password123"))
    assert result is None
