import json

import pytest

from app import create_app


@pytest.fixture
def client(tmp_path):
    db_path = tmp_path / "test_app.db"
    app = create_app(test_db_path=db_path)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_empty_initial_settings(client):
    response = client.get("/api/settings")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["route_name"] == ""
    assert payload["commute_minutes"] == 0
    assert payload["timezone"] == "Asia/Kolkata"


def test_save_and_retrieve_valid_settings(client):
    response = client.put(
        "/api/settings",
        json={"route_name": "Home", "commute_minutes": 45, "timezone": "Asia/Kolkata"},
    )
    assert response.status_code == 200

    saved = client.get("/api/settings")
    payload = saved.get_json()
    assert payload["route_name"] == "Home"
    assert payload["commute_minutes"] == 45
    assert payload["timezone"] == "Asia/Kolkata"


def test_rejects_invalid_commute_duration(client):
    response = client.put(
        "/api/settings",
        json={"route_name": "Home", "commute_minutes": 0, "timezone": "Asia/Kolkata"},
    )
    assert response.status_code == 400


def test_valid_session_save_and_summary(client):
    client.put("/api/settings", json={"route_name": "Home", "commute_minutes": 60, "timezone": "Asia/Kolkata"})
    response = client.post(
        "/api/sessions",
        json={"route_name": "Home", "planned_minutes": 15, "actual_minutes": 12, "timezone": "Asia/Kolkata"},
    )
    assert response.status_code == 200

    summary = client.get("/api/summary")
    payload = summary.get_json()
    assert payload["week_minutes"] == 12
    assert payload["hours_reclaimed"] == 0.2
    assert payload["recent_sessions"][0]["actual_minutes"] == 12


def test_rejects_session_exceeding_commute(client):
    client.put("/api/settings", json={"route_name": "Home", "commute_minutes": 30, "timezone": "Asia/Kolkata"})
    response = client.post(
        "/api/sessions",
        json={"route_name": "Home", "planned_minutes": 35, "actual_minutes": 30, "timezone": "Asia/Kolkata"},
    )
    assert response.status_code == 400


def test_rejects_actual_minutes_above_planned(client):
    client.put("/api/settings", json={"route_name": "Home", "commute_minutes": 90, "timezone": "Asia/Kolkata"})
    response = client.post(
        "/api/sessions",
        json={"route_name": "Home", "planned_minutes": 10, "actual_minutes": 11, "timezone": "Asia/Kolkata"},
    )
    assert response.status_code == 400


def test_delete_session_and_summary_updates(client):
    client.put("/api/settings", json={"route_name": "Home", "commute_minutes": 60, "timezone": "Asia/Kolkata"})
    client.post(
        "/api/sessions",
        json={"route_name": "Home", "planned_minutes": 15, "actual_minutes": 10, "timezone": "Asia/Kolkata"},
    )

    response = client.delete("/api/sessions/1")
    assert response.status_code == 200

    summary = client.get("/api/summary")
    assert summary.get_json()["week_minutes"] == 0
    assert len(summary.get_json()["recent_sessions"]) == 0


def test_delete_missing_session_returns_404(client):
    response = client.delete("/api/sessions/999")
    assert response.status_code == 404


def test_rejects_invalid_timezone(client):
    response = client.put(
        "/api/settings",
        json={"route_name": "Home", "commute_minutes": 45, "timezone": "Mars/Phobos"},
    )
    assert response.status_code == 400
