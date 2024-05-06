from datetime import date
from unittest.mock import Mock

import pytest
from sqlalchemy import select

from src.database.models import Contact
from tests.conftest import TestingSessionLocal
from conf import messages

contact_data = {
    "name": "test_name",
    "email": "testemail@ukr.net",
    "phone": "0674444444",
    "birthday": str(date(1975, 12, 12)),
    "password": "12345678",
}

contact_data2 = {
    "name": "test_name2",
    "email": "test2email@ukr.net",
    "phone": "0624444444",
    "birthday": str(date(1975, 12, 12)),
    "password": "12345678",
}

def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("api/auth/signup", json=contact_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["name"] == contact_data["name"]
    assert data["email"] == contact_data["email"]
    assert data["phone"] == contact_data["phone"]
    assert data["birthday"] == contact_data["birthday"]
    assert "password" not in data


def test_repeat_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("api/auth/signup", json=contact_data)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == messages.ACCOUNT_EXIST


def test_not_confirmed_login(client):
    response = client.post(
        "api/auth/login",
        data={
            "username": contact_data.get("email"),
            "password": contact_data.get("password"),
        },
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == messages.EMAIL_NOT_CONFIRMED


@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(Contact).where(Contact.email == contact_data.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = client.post(
        "api/auth/login",
        data={
            "username": contact_data.get("email"),
            "password": contact_data.get("password"),
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "token_type" in data


def test_wrong_password_login(client):
    response = client.post(
        "api/auth/login",
        data={"username": contact_data.get("email"), "password": "password"},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == messages.INVALID_PASSWORD


def test_wrong_email_login(client):
    response = client.post(
        "api/auth/login",
        data={"username": "email", "password": contact_data.get("password")},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == messages.INVALID_EMAIL


def test_validation_error_login(client):
    response = client.post(
        "api/auth/login", data={"password": contact_data.get("password")}
    )
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data


def test_signup2(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("api/auth/signup", json=contact_data2)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["name"] == contact_data2["name"]
    assert data["email"] == contact_data2["email"]
    assert data["phone"] == contact_data2["phone"]
    assert data["birthday"] == contact_data2["birthday"]
    assert "password" not in data
