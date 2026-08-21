from app.services.user_service import UserService


def test_register_returns_201_with_user_and_token(app, client):
    response = client.post(
        "/api/auth/register",
        json={"email": "a@example.com", "password": "password123"},
    )

    assert response.status_code == 201
    body = response.get_json()
    assert body["user"]["email"] == "a@example.com"
    assert "password" not in body["user"]
    assert "token" in body


def test_register_returns_400_for_short_password(app, client):
    response = client.post(
        "/api/auth/register", json={"email": "a@example.com", "password": "short"}
    )

    assert response.status_code == 400


def test_register_returns_409_for_duplicate_email(app, client):
    UserService().register(email="a@example.com", password="password123")

    response = client.post(
        "/api/auth/register",
        json={"email": "a@example.com", "password": "password123"},
    )

    assert response.status_code == 409


def test_login_returns_token_for_valid_credentials(app, client):
    UserService().register(email="a@example.com", password="password123")

    response = client.post(
        "/api/auth/login", json={"email": "a@example.com", "password": "password123"}
    )

    assert response.status_code == 200
    assert "token" in response.get_json()


def test_login_returns_401_for_wrong_password(app, client):
    UserService().register(email="a@example.com", password="password123")

    response = client.post(
        "/api/auth/login", json={"email": "a@example.com", "password": "wrong"}
    )

    assert response.status_code == 401
