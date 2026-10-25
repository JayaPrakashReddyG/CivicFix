
"""Tests for CivicFix authentication APIs."""

import pytest

from app import create_app
from database import get_db


@pytest.fixture()
def app(tmp_path, monkeypatch):
    database_path = tmp_path / "test_civicfix.db"

    monkeypatch.setattr(
        "config.Config.DATABASE_PATH",
        database_path,
    )

    monkeypatch.setattr(
        "config.Config.TESTING",
        True,
        raising=False,
    )

    app = create_app()
    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key",
    )

    with app.app_context():
        from database import init_db

        init_db(app)

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def test_home_page_responds(client):
    response = client.get("/")
    assert response.status_code == 200


def test_register_success(client):
    response = client.post(
        "/api/auth/register",
        json={
            "name": "Test Citizen",
            "email": "citizen@example.com",
            "password": "StrongPass123!",
        },
    )

    assert response.status_code in (200, 201)


def test_register_duplicate_email(client):
    payload = {
        "name": "Test Citizen",
        "email": "duplicate@example.com",
        "password": "StrongPass123!",
    }

    first_response = client.post(
        "/api/auth/register",
        json=payload,
    )
    second_response = client.post(
        "/api/auth/register",
        json=payload,
    )

    assert first_response.status_code in (200, 201)
    assert second_response.status_code in (400, 409)


def test_register_missing_fields(client):
    response = client.post(
        "/api/auth/register",
        json={"email": "missing@example.com"},
    )

    assert response.status_code == 400


def test_login_with_registered_user(client):
    client.post(
        "/api/auth/register",
        json={
            "name": "Login Citizen",
            "email": "login@example.com",
            "password": "StrongPass123!",
        },
    )

    response = client.post(
        "/api/auth/login",
        json={
            "email": "login@example.com",
            "password": "StrongPass123!",
        },
    )

    assert response.status_code == 200


def test_login_with_wrong_password(client):
    client.post(
        "/api/auth/register",
        json={
            "name": "Login Citizen",
            "email": "wrongpass@example.com",
            "password": "StrongPass123!",
        },
    )

    response = client.post(
        "/api/auth/login",
        json={
            "email": "wrongpass@example.com",
            "password": "IncorrectPassword!",
        },
    )

    assert response.status_code in (400, 401)


def test_current_user_requires_login(client):
    response = client.get("/api/auth/me")
    assert response.status_code in (401, 403)
