from flask_login import current_user
from website.models import User


def test_signup(client):
    response = client.post(
        "/signup",
        data={
            "email": "newuser@test.com",
            "password": "Password123!",
            "password2": "Password123!",
            "username": "newuser",
            "firstname": "New",
            "lastname": "User",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Account created successfully!" in response.data
    assert current_user.is_authenticated
    assert User.query.filter_by(email="newuser@test.com").first() is not None


def test_login(client, init_database):
    response = client.post(
        "/login",
        data={"email": "user1@test.com", "password": "TestPassword123!"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Logged successfully!" in response.data
    assert current_user.is_authenticated


def test_logout(init_database, authorized_client):
    response = authorized_client.post("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"Logged out successfully!" in response.data
    assert not current_user.is_authenticated
