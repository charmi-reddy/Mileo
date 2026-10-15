from __future__ import annotations

import os
import re
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_TIMEZONE = "Asia/Kolkata"
MAX_ROUTE_NAME_LENGTH = 80
MAX_COMMUTE_MINUTES = 24 * 60

FLASHCARDS = [
    {
        "id": 1,
        "question": "What is the difference between a list and a tuple in Python?",
        "answer": "A list is mutable and can be changed after creation, while a tuple is immutable and cannot be changed once created.",
        "explanation": "Lists are commonly used when you need to add, remove, or update values. Tuples are useful when you want fixed data or a safer structure.",
    },
    {
        "id": 2,
        "question": "What does a Python dictionary store?",
        "answer": "A dictionary stores data as key-value pairs, where each key maps to a value.",
        "explanation": "This is useful for lookup-based data, such as user profiles, configs, or caches.",
    },
    {
        "id": 3,
        "question": "What is a Python function return value?",
        "answer": "A function can return a value using the return keyword, and that value is sent back to the caller.",
        "explanation": "The caller can then use the returned result in another calculation, condition, or variable assignment.",
    },
    {
        "id": 4,
        "question": "What is the purpose of a virtual environment?",
        "answer": "A virtual environment isolates project dependencies so different projects can use different versions of libraries without conflicting.",
        "explanation": "This prevents package-version mismatches between projects on the same machine.",
    },
    {
        "id": 5,
        "question": "What does the .split() method do on a string?",
        "answer": "It breaks a string into a list of smaller strings using a chosen separator, usually a space or comma.",
        "explanation": "This is often used when parsing input, CSV data, or user-entered text.",
    },
    {
        "id": 6,
        "question": "What is a set in Python?",
        "answer": "A set is an unordered collection of unique items.",
        "explanation": "Sets are useful when you care about membership or uniqueness rather than order.",
    },
    {
        "id": 7,
        "question": "What is a list comprehension?",
        "answer": "A list comprehension is a compact way to create a list from an existing iterable using a single expression.",
        "explanation": "It is often more concise than writing a full loop, but should stay readable for maintainability.",
    },
    {
        "id": 8,
        "question": "What is a for loop used for in Python?",
        "answer": "A for loop is used to repeat a block of code over a sequence such as a list, string, or range.",
        "explanation": "This is a core pattern for iterating through data and applying the same logic to each item.",
    },
    {
        "id": 9,
        "question": "What is the difference between == and = in Python?",
        "answer": "== compares two values, while = assigns a value to a variable.",
        "explanation": "This is a very common beginner mistake, and understanding it helps avoid logic bugs.",
    },
    {
        "id": 10,
        "question": "What is a function in Python?",
        "answer": "A function is a reusable block of code that performs a specific task and can be called when needed.",
        "explanation": "Functions help break programs into smaller, easier-to-test pieces and reduce repetition.",
    },
]


def resolve_db_path(test_db_path: str | Path | None = None) -> Path:
    if test_db_path is not None:
        return Path(test_db_path)
    configured = os.environ.get("MILEO_DB_PATH")
    if configured:
        return Path(configured)
    return BASE_DIR / "data" / "app.db"


def default_settings() -> dict:
    return {"route_name": "", "commute_minutes": 0, "timezone": DEFAULT_TIMEZONE}


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
        return jsonify({"deck": FLASHCARDS})

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

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
