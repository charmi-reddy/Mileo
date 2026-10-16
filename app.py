from __future__ import annotations

import io
import json
import os
import re
import sqlite3
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_TIMEZONE = "Asia/Kolkata"
MAX_ROUTE_NAME_LENGTH = 80
MAX_COMMUTE_MINUTES = 24 * 60
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
AI_BATCH_LIMIT = 10

def resolve_db_path(test_db_path: str | Path | None = None) -> Path:
    if test_db_path is not None:
        return Path(test_db_path)
    configured = os.environ.get("MILEO_DB_PATH")
    if configured:
        return Path(configured)
    return BASE_DIR / "data" / "app.db"


def default_settings() -> dict:
    return {"route_name": "", "commute_minutes": 0, "timezone": DEFAULT_TIMEZONE}


def parse_question_objects(raw_text: str) -> list[dict]:
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```\s*$", "", cleaned)
    start = cleaned.find("[")
    end = cleaned.rfind("]")
    if start != -1 and end != -1 and end > start:
        cleaned = cleaned[start : end + 1]
    payload = json.loads(cleaned)
    if not isinstance(payload, list):
        raise ValueError("Gemini returned an unexpected format.")
    normalized = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        question = str(item.get("question") or "").strip()
        answer = str(item.get("answer") or "").strip()
        explanation = str(item.get("explanation") or "").strip()
        if not question or not answer or not explanation:
            continue
        normalized.append({
            "question": question,
            "answer": answer,
            "explanation": explanation,
        })
    if len(normalized) != AI_BATCH_LIMIT:
        raise ValueError(f"Gemini must return exactly {AI_BATCH_LIMIT} questions.")
    return normalized


def generate_question_batch(topic: str, difficulty: str, source_text: str) -> list[dict]:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Gemini API key is not configured.")

    safe_topic = (topic or "General learning").strip()
    safe_difficulty = (difficulty or "Beginner").strip() or "Beginner"
    safe_source = (source_text or "").strip()
    if not safe_source:
        raise ValueError("Source text is required to generate questions.")

    prompt = (
        "You are generating a microlearning flashcard deck for a commuter app. "
        f"Create exactly {AI_BATCH_LIMIT} concise and useful questions about the topic: '{safe_topic}'. "
        f"Difficulty level: {safe_difficulty}. "
        "Use the supplied source material to ground the questions. "
        "Return only a valid JSON array with exactly 10 objects. Each object must have exactly three keys: "
        "question, answer, and explanation. Keep the wording clear and educational. "
        "Do not include markdown fences or extra commentary.\n\nSource:\n"
        + safe_source[:12000]
    )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 4000,
        },
    }

    request = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={api_key}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        data = json.loads(response.read().decode("utf-8"))

    candidate = data["candidates"][0]
    text_blocks = candidate["content"]["parts"]
    raw_text = "".join(part.get("text", "") for part in text_blocks)
    return parse_question_objects(raw_text)


def extract_uploaded_text(file_storage) -> str:
    if file_storage is None or not getattr(file_storage, "filename", None):
        return ""

    filename = Path(str(file_storage.filename)).name
    suffix = Path(filename).suffix.lower()
    raw_bytes = file_storage.read()

    if suffix == ".txt":
        return raw_bytes.decode("utf-8", errors="ignore")

    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:  # pragma: no cover - depends on optional dependency
            raise ValueError("PDF support requires the pypdf package.") from exc
        reader = PdfReader(io.BytesIO(raw_bytes))
        pages = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            pages.append(page_text)
        return "\n".join(pages)

    if suffix == ".docx":
        try:
            from docx import Document
        except ImportError as exc:  # pragma: no cover - depends on optional dependency
            raise ValueError("DOCX support requires the python-docx package.") from exc
        document = Document(io.BytesIO(raw_bytes))
        return "\n".join(paragraph.text for paragraph in document.paragraphs if paragraph.text.strip())

    raise ValueError("Unsupported file type. Please upload a PDF, DOCX, or TXT file.")


def get_db_connection(db_path: Path | str) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def validate_timezone(value: object) -> str:
    zone_name = str(value or DEFAULT_TIMEZONE).strip() or DEFAULT_TIMEZONE
    try:
        ZoneInfo(zone_name)
    except Exception as exc:  # pragma: no cover - defensive guard for invalid zone names
        raise ValueError("Timezone is invalid.") from exc
    return zone_name


def validate_route_name(value: object, *, required: bool = False) -> str:
    if value is None:
        if required:
            raise ValueError("Route name is required.")
        return ""
    if not isinstance(value, str):
        raise ValueError("Route name must be a string.")
    route_name = value.strip()
    if required and not route_name:
        raise ValueError("Route name is required.")
    if len(route_name) > MAX_ROUTE_NAME_LENGTH:
        raise ValueError("Route name is too long.")
    return route_name


def parse_positive_int(value: object, field_name: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be a positive integer.")
    if isinstance(value, int):
        parsed = value
    elif isinstance(value, str):
        stripped = value.strip()
        if not re.fullmatch(r"\d+", stripped):
            raise ValueError(f"{field_name} must be a positive integer.")
        parsed = int(stripped)
    else:
        raise ValueError(f"{field_name} must be a positive integer.")
    if parsed <= 0:
        raise ValueError(f"{field_name} must be greater than zero.")
    return parsed


def normalize_datetime(value: object, default_timezone_name: str = DEFAULT_TIMEZONE) -> datetime:
    if value is None:
        raise ValueError("Timestamp is missing.")
    if isinstance(value, datetime):
        timestamp = value
    else:
        timestamp = datetime.fromisoformat(str(value).replace("Z", "+00:00"))

    if timestamp.tzinfo is None:
        default_tz = ZoneInfo(default_timezone_name)
        timestamp = timestamp.replace(tzinfo=default_tz)
    return timestamp.astimezone(timezone.utc)


def init_db(db_path: Path | str | None = None) -> None:
    resolved_path = resolve_db_path(db_path)
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    with get_db_connection(resolved_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                route_name TEXT NOT NULL,
                commute_minutes INTEGER NOT NULL,
                timezone TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                route_name TEXT NOT NULL,
                planned_minutes INTEGER NOT NULL,
                actual_minutes INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                timezone TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ai_batches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                source_text TEXT NOT NULL,
                created_at TEXT NOT NULL,
                questions TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ai_progress (
                batch_id INTEGER PRIMARY KEY,
                current_index INTEGER NOT NULL DEFAULT 0,
                understood_count INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(batch_id) REFERENCES ai_batches(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            "INSERT OR IGNORE INTO settings (id, route_name, commute_minutes, timezone) VALUES (1, '', 0, 'Asia/Kolkata')"
        )


def create_app(test_db_path: str | Path | None = None) -> Flask:
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config["DATABASE_PATH"] = str(resolve_db_path(test_db_path))
    init_db(app.config["DATABASE_PATH"])

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/api/settings")
    def get_settings():
        db_path = Path(app.config["DATABASE_PATH"])
        with get_db_connection(db_path) as conn:
            row = conn.execute(
                "SELECT route_name, commute_minutes, timezone FROM settings WHERE id = 1"
            ).fetchone()
          
        if row is None:
            return jsonify(default_settings())
        return jsonify({
            "route_name": row["route_name"],
            "commute_minutes": row["commute_minutes"],
            "timezone": row["timezone"],
        })

    @app.put("/api/settings")
    def put_settings():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"error": "Request body must be a JSON object."}), 400

        try:
            route_name = validate_route_name(payload.get("route_name", ""), required=False)
            commute_minutes = parse_positive_int(payload.get("commute_minutes"), "commute_minutes")
            timezone_name = validate_timezone(payload.get("timezone", DEFAULT_TIMEZONE))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

        if commute_minutes > MAX_COMMUTE_MINUTES:
            return jsonify({"error": "Commute time is too large."}), 400

        db_path = Path(app.config["DATABASE_PATH"])
        with get_db_connection(db_path) as conn:
            conn.execute(
                "INSERT INTO settings (id, route_name, commute_minutes, timezone) VALUES (1, ?, ?, ?) ON CONFLICT(id) DO UPDATE SET route_name = excluded.route_name, commute_minutes = excluded.commute_minutes, timezone = excluded.timezone",
                (route_name, commute_minutes, timezone_name),
            )
        return jsonify({"status": "ok"})

    @app.get("/api/deck")
    def get_deck():
        return jsonify({"deck": []})

    @app.post("/api/sessions")
    def create_session():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"error": "Request body must be a JSON object."}), 400

        try:
            route_name = validate_route_name(payload.get("route_name"), required=True)
            planned_minutes = parse_positive_int(payload.get("planned_minutes"), "planned_minutes")
            actual_minutes = parse_positive_int(payload.get("actual_minutes"), "actual_minutes")
            timezone_name = validate_timezone(payload.get("timezone", DEFAULT_TIMEZONE))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

        if actual_minutes > planned_minutes:
            return jsonify({"error": "Actual study minutes cannot exceed the planned session length."}), 400

        db_path = Path(app.config["DATABASE_PATH"])
        with get_db_connection(db_path) as conn:
            settings_row = conn.execute(
                "SELECT route_name, commute_minutes, timezone FROM settings WHERE id = 1"
            ).fetchone()
        if settings_row is None or int(settings_row["commute_minutes"]) <= 0:
            return jsonify({"error": "Commute configuration is required before saving a session."}), 400

        commute_minutes = int(settings_row["commute_minutes"])
        if planned_minutes > commute_minutes:
            return jsonify({"error": "Session length cannot exceed the configured commute duration."}), 400

        created_at = datetime.now(ZoneInfo(timezone_name)).astimezone(timezone.utc).isoformat()
        with get_db_connection(db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO sessions (route_name, planned_minutes, actual_minutes, created_at, timezone) VALUES (?, ?, ?, ?, ?)",
                (route_name, planned_minutes, actual_minutes, created_at, timezone_name),
            )
            session_id = cursor.lastrowid
        return jsonify({"status": "saved", "session_id": session_id})

    @app.delete("/api/sessions/<session_id>")
    def delete_session(session_id: str):
        try:
            integer_id = int(session_id)
        except (TypeError, ValueError):
            return jsonify({"error": "Session ID must be an integer."}), 400

        db_path = Path(app.config["DATABASE_PATH"])
        with get_db_connection(db_path) as conn:
            cursor = conn.execute("DELETE FROM sessions WHERE id = ?", (integer_id,))
            conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Session not found."}), 404
        return jsonify({"status": "deleted"})

    @app.get("/api/summary")
    def get_summary():
        db_path = Path(app.config["DATABASE_PATH"])
        with get_db_connection(db_path) as conn:
            settings_row = conn.execute(
                "SELECT route_name, commute_minutes, timezone FROM settings WHERE id = 1"
            ).fetchone()
            session_rows = conn.execute(
                "SELECT id, route_name, planned_minutes, actual_minutes, created_at, timezone FROM sessions ORDER BY created_at DESC"
            ).fetchall()

        reporting_tz_name = (settings_row["timezone"] if settings_row is not None else DEFAULT_TIMEZONE) or DEFAULT_TIMEZONE
        reporting_tz = ZoneInfo(reporting_tz_name)
        now = datetime.now(reporting_tz)
        week_start = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=now.weekday())
        daily_minutes = {}
        for i in range(7):
            day_start = week_start + timedelta(days=i)
            daily_minutes[day_start.date().isoformat()] = 0

        for row in session_rows:
            created_value = row["created_at"]
            try:
                created_at = normalize_datetime(created_value, row["timezone"] or reporting_tz_name)
            except ValueError:
                continue
            local_created = created_at.astimezone(reporting_tz)
            if week_start.date() <= local_created.date() <= (week_start + timedelta(days=6)).date():
                day_key = local_created.date().isoformat()
                daily_minutes[day_key] = daily_minutes.get(day_key, 0) + int(row["actual_minutes"])

        daily_data = []
        for i in range(7):
            day_start = week_start + timedelta(days=i)
            daily_data.append({
                "day": day_start.strftime("%a"),
                "date": day_start.strftime("%Y-%m-%d"),
                "minutes": daily_minutes.get(day_start.date().isoformat(), 0),
            })

        total_minutes = sum(item["minutes"] for item in daily_data)
        recent_sessions = []
        for row in session_rows[:10]:
            created_at = normalize_datetime(row["created_at"], row["timezone"] or reporting_tz_name)
            recent_sessions.append({
                "id": row["id"],
                "route_name": row["route_name"],
                "actual_minutes": row["actual_minutes"],
                "created_at": created_at.astimezone(reporting_tz).strftime("%Y-%m-%d %H:%M"),
            })

        return jsonify({
            "week_minutes": total_minutes,
            "hours_reclaimed": round(total_minutes / 60, 2),
            "daily": daily_data,
            "recent_sessions": recent_sessions,
        })

    @app.post("/api/ai/generate")
    def generate_ai_questions():
        topic = (request.form.get("topic") or "").strip()
        difficulty = (request.form.get("difficulty") or "Beginner").strip() or "Beginner"
        source_text = (request.form.get("source_text") or "").strip()

        uploaded_file = request.files.get("document")
        if uploaded_file and uploaded_file.filename:
            try:
                extracted = extract_uploaded_text(uploaded_file)
            except ValueError as exc:
                return jsonify({"error": str(exc)}), 400
            if extracted.strip():
                source_text = "\n\n".join(part for part in [source_text, extracted] if part.strip())

        if not topic:
            return jsonify({"error": "Topic is required."}), 400
        if not source_text:
            return jsonify({"error": "Add source text or upload a PDF, DOCX, or TXT file."}), 400

        try:
            questions = generate_question_batch(topic, difficulty, source_text)
        except (RuntimeError, ValueError, json.JSONDecodeError, urllib.error.URLError) as exc:
            return jsonify({"error": str(exc)}), 503 if "Gemini" in str(exc) or "API key" in str(exc) else 400

        now = datetime.now(timezone.utc).isoformat()
        db_path = Path(app.config["DATABASE_PATH"])
        with get_db_connection(db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO ai_batches (topic, difficulty, source_text, created_at, questions) VALUES (?, ?, ?, ?, ?)",
                (topic, difficulty, source_text, now, json.dumps(questions)),
            )
            batch_id = cursor.lastrowid
            conn.execute(
                "INSERT INTO ai_progress (batch_id, current_index, understood_count, updated_at) VALUES (?, 0, 0, ?)",
                (batch_id, now),
            )

        return jsonify({
            "status": "generated",
            "batch_id": batch_id,
            "count": len(questions),
            "questions": questions,
        })

    @app.get("/api/ai/batches")
    def list_ai_batches():
        db_path = Path(app.config["DATABASE_PATH"])
        with get_db_connection(db_path) as conn:
            rows = conn.execute(
                "SELECT id, topic, difficulty, created_at, questions FROM ai_batches ORDER BY id DESC LIMIT 20"
            ).fetchall()

        batches = []
        for row in rows:
            data = json.loads(row["questions"])
            batches.append({
                "id": row["id"],
                "topic": row["topic"],
                "difficulty": row["difficulty"],
                "created_at": row["created_at"],
                "question_count": len(data),
                "questions": data,
            })
        return jsonify({"batches": batches})

    @app.get("/api/ai/progress/<int:batch_id>")
    def get_ai_progress(batch_id: int):
        db_path = Path(app.config["DATABASE_PATH"])
        with get_db_connection(db_path) as conn:
            progress_row = conn.execute(
                "SELECT current_index, understood_count, updated_at FROM ai_progress WHERE batch_id = ?",
                (batch_id,),
            ).fetchone()
            batch_row = conn.execute(
                "SELECT topic, difficulty, questions FROM ai_batches WHERE id = ?",
                (batch_id,),
            ).fetchone()
        if batch_row is None:
            return jsonify({"error": "Batch not found."}), 404

        questions = json.loads(batch_row["questions"]) if batch_row["questions"] else []
        if progress_row is None:
            progress_row = {"current_index": 0, "understood_count": 0, "updated_at": batch_row["created_at"]}
        return jsonify({
            "batch_id": batch_id,
            "topic": batch_row["topic"],
            "difficulty": batch_row["difficulty"],
            "current_index": progress_row["current_index"],
            "understood_count": progress_row["understood_count"],
            "updated_at": progress_row["updated_at"],
            "question_count": len(questions),
            "questions": questions,
        })

    @app.post("/api/ai/progress/<int:batch_id>")
    def save_ai_progress(batch_id: int):
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"error": "Request body must be a JSON object."}), 400

        current_index = int(payload.get("current_index", 0))
        understood_count = int(payload.get("understood_count", 0))
        updated_at = datetime.now(timezone.utc).isoformat()

        db_path = Path(app.config["DATABASE_PATH"])
        with get_db_connection(db_path) as conn:
            conn.execute(
                "INSERT INTO ai_progress (batch_id, current_index, understood_count, updated_at) VALUES (?, ?, ?, ?) ON CONFLICT(batch_id) DO UPDATE SET current_index = excluded.current_index, understood_count = excluded.understood_count, updated_at = excluded.updated_at",
                (batch_id, current_index, understood_count, updated_at),
            )
        return jsonify({"status": "saved", "batch_id": batch_id})

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
