
"""Tests for CivicFix issue reporting APIs."""

import pytest

from app import create_app


@pytest.fixture()
def app(tmp_path, monkeypatch):
    database_path = tmp_path / "test_issues.db"

    monkeypatch.setattr(
        "config.Config.DATABASE_PATH",
        database_path,
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


def register_and_login(client):
    register_response = client.post(
        "/api/auth/register",
        json={
            "name": "Issue Tester",
            "email": "issue-tester@example.com",
            "password": "StrongPass123!",
        },
    )

    assert register_response.status_code in (200, 201)

    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "issue-tester@example.com",
            "password": "StrongPass123!",
        },
    )

    assert login_response.status_code == 200


def test_create_issue_requires_login(client):
    response = client.post(
        "/api/issues/",
        json={
            "title": "Road pothole",
            "description": "Large pothole near the bus stop.",
            "category": "Pothole",
        },
    )

    assert response.status_code in (401, 403)


def test_create_issue_success(client):
    register_and_login(client)

    response = client.post(
        "/api/issues/",
        json={
            "title": "Road pothole",
            "description": "Large pothole near the bus stop.",
            "category": "Pothole",
            "address": "Main Road",
        },
    )

    assert response.status_code in (200, 201)


def test_create_issue_missing_title(client):
    register_and_login(client)

    response = client.post(
        "/api/issues/",
        json={
            "description": "A damaged streetlight needs repair.",
            "category": "Streetlight",
        },
    )

    assert response.status_code == 400


def test_list_issues_endpoint(client):
    response = client.get("/api/issues/")

    assert response.status_code == 200


def test_my_issues_requires_login(client):
    response = client.get("/api/issues/my")

    assert response.status_code in (401, 403)


def test_invalid_coordinates_are_rejected(client):
    register_and_login(client)

    response = client.post(
        "/api/issues/",
        json={
            "title": "Broken streetlight",
            "description": "The light is not working.",
            "category": "Streetlight",
            "latitude": 250,
            "longitude": 80,
        },
    )

    assert response.status_code == 400
