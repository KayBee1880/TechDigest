from app.services.user_service import UserService


def test_register_creates_user_with_hashed_password(app):
    user = UserService().register(email="a@example.com", password="password123")

    assert user.email == "a@example.com"
    assert user.password_hash != "password123"


def test_register_returns_none_for_duplicate_email(app):
    UserService().register(email="a@example.com", password="password123")

    result = UserService().register(email="a@example.com", password="different")

    assert result is None


def test_authenticate_returns_user_for_correct_password(app):
    UserService().register(email="a@example.com", password="password123")

    user = UserService().authenticate(email="a@example.com", password="password123")

    assert user is not None
    assert user.email == "a@example.com"


def test_authenticate_returns_none_for_wrong_password(app):
    UserService().register(email="a@example.com", password="password123")

    user = UserService().authenticate(email="a@example.com", password="wrong")

    assert user is None


def test_authenticate_returns_none_for_unknown_email(app):
    user = UserService().authenticate(email="nobody@example.com", password="password123")

    assert user is None


def test_generate_and_decode_token_roundtrip(app):
    service = UserService()
    user = service.register(email="a@example.com", password="password123")

    token = service.generate_token(user)

    assert UserService.decode_token(token) == user.id


def test_decode_token_returns_none_for_garbage(app):
    assert UserService.decode_token("not-a-real-token") is None
