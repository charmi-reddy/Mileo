import json

import pytest

from app import create_app, parse_question_objects


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


def test_generate_ai_questions_and_persist_batch(client, monkeypatch):
    def fake_generate_question_batch(topic, difficulty, source_text):
        assert topic == "Python"
        assert difficulty == "Beginner"
        assert source_text == "Python basics"
        return [
            {"question": f"Q{i}", "answer": f"A{i}", "explanation": f"E{i}"}
            for i in range(1, 11)
        ]

    monkeypatch.setattr("app.generate_question_batch", fake_generate_question_batch)

    response = client.post(
        "/api/ai/generate",
        data={"topic": "Python", "difficulty": "Beginner", "source_text": "Python basics"},
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["count"] == 10
    assert payload["batch_id"] > 0
    assert len(payload["questions"]) == 10

    saved = client.get("/api/ai/batches")
    assert saved.status_code == 200
    assert saved.get_json()["batches"][0]["topic"] == "Python"


def test_generate_ai_questions_without_upload_or_source_text(client, monkeypatch):
    def fake_generate_question_batch(topic, difficulty, source_text):
        assert topic == "Algorithms"
        assert difficulty == "Advanced"
        assert "Algorithms" in source_text or "Advanced" in source_text
        return [
            {"question": f"Q{i}", "answer": f"A{i}", "explanation": f"E{i}"}
            for i in range(1, 11)
        ]

    monkeypatch.setattr("app.generate_question_batch", fake_generate_question_batch)

    response = client.post(
        "/api/ai/generate",
        data={"topic": "Algorithms", "difficulty": "Advanced"},
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert response.get_json()["count"] == 10


def test_ai_progress_can_resume_batch(client, monkeypatch):
    def fake_generate_question_batch(topic, difficulty, source_text):
        return [
            {"question": f"Q{i}", "answer": f"A{i}", "explanation": f"E{i}"}
            for i in range(1, 11)
        ]

    monkeypatch.setattr("app.generate_question_batch", fake_generate_question_batch)

    response = client.post(
        "/api/ai/generate",
        data={"topic": "Data structures", "difficulty": "Intermediate", "source_text": "Lists, sets, dicts"},
        content_type="multipart/form-data",
    )
    batch_id = response.get_json()["batch_id"]

    progress_response = client.get(f"/api/ai/progress/{batch_id}")
    assert progress_response.status_code == 200
    assert progress_response.get_json()["current_index"] == 0

    update = client.post(
        f"/api/ai/progress/{batch_id}",
        json={"current_index": 3, "understood_count": 2},
    )
    assert update.status_code == 200

    resumed = client.get(f"/api/ai/progress/{batch_id}")
    assert resumed.get_json()["current_index"] == 3
    assert resumed.get_json()["understood_count"] == 2


def test_parse_question_objects_recovers_fenced_json_with_prose():
    questions = [
        {"question": f"Q{i}", "answer": f"A{i}", "explanation": f"E{i}"}
        for i in range(1, 11)
    ]
    raw_text = """Here is the deck you asked for:
```json
{payload}
```
Hope that helps.
""".format(payload=json.dumps(questions))

    parsed = parse_question_objects(raw_text)

    assert len(parsed) == 10
    assert parsed[0]["question"] == "Q1"
    assert parsed[-1]["explanation"] == "E10"
