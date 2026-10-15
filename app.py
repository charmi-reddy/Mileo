from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "app.db"

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

app = Flask(__name__, static_folder="static", template_folder="templates")


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_db_connection()
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
    conn.commit()
    conn.close()


def default_settings() -> dict:
    return {"route_name": "", "commute_minutes": 0, "timezone": "Asia/Kolkata"}


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/settings")
def get_settings():
    conn = get_db_connection()
    row = conn.execute("SELECT route_name, commute_minutes, timezone FROM settings WHERE id = 1").fetchone()
    conn.close()
    if row is None:
        return jsonify(default_settings())
    return jsonify({
        "route_name": row["route_name"],
        "commute_minutes": row["commute_minutes"],
        "timezone": row["timezone"],
    })


@app.put("/api/settings")
def put_settings():
    payload = request.get_json(silent=True) or {}
    route_name = str(payload.get("route_name", "")).strip()
    commute_minutes = payload.get("commute_minutes")
    timezone = str(payload.get("timezone") or "Asia/Kolkata").strip() or "Asia/Kolkata"

    if commute_minutes is None or str(commute_minutes).strip() == "":
        return jsonify({"error": "Commute time is required."}), 400

    try:
        commute_minutes = int(commute_minutes)
    except (TypeError, ValueError):
        return jsonify({"error": "Commute time must be a number."}), 400

    if commute_minutes < 0:
        return jsonify({"error": "Commute time cannot be negative."}), 400

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO settings (id, route_name, commute_minutes, timezone) VALUES (1, ?, ?, ?) ON CONFLICT(id) DO UPDATE SET route_name = excluded.route_name, commute_minutes = excluded.commute_minutes, timezone = excluded.timezone",
        (route_name, commute_minutes, timezone),
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})


@app.get("/api/deck")
def get_deck():
    return jsonify({"deck": FLASHCARDS})


@app.post("/api/sessions")
def create_session():
    payload = request.get_json(silent=True) or {}
    route_name = str(payload.get("route_name", "")).strip()
    planned_minutes = payload.get("planned_minutes")
    actual_minutes = payload.get("actual_minutes")
    timezone = str(payload.get("timezone") or "Asia/Kolkata").strip() or "Asia/Kolkata"

    if not route_name:
        return jsonify({"error": "Route name is required."}), 400

    try:
        planned_minutes = int(planned_minutes)
        actual_minutes = int(actual_minutes)
    except (TypeError, ValueError):
        return jsonify({"error": "Minutes must be valid numbers."}), 400

    if planned_minutes <= 0:
        return jsonify({"error": "Session length must be greater than zero."}), 400

    if actual_minutes <= 0:
        return jsonify({"error": "Study minutes must be greater than zero."}), 400

    if actual_minutes > planned_minutes:
        return jsonify({"error": "Study minutes cannot exceed the planned session length."}), 400

    created_at = datetime.now(ZoneInfo(timezone)).isoformat()

    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO sessions (route_name, planned_minutes, actual_minutes, created_at, timezone) VALUES (?, ?, ?, ?, ?)",
        (route_name, planned_minutes, actual_minutes, created_at, timezone),
    )
    conn.commit()
    session_id = cursor.lastrowid
    conn.close()

    return jsonify({"status": "saved", "session_id": session_id})


@app.delete("/api/sessions/<session_id>")
def delete_session(session_id: str):
    conn = get_db_connection()
    conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"})


@app.get("/api/summary")
def get_summary():
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT id, route_name, planned_minutes, actual_minutes, created_at, timezone FROM sessions ORDER BY created_at DESC"
    ).fetchall()
    conn.close()

    tz_name = "Asia/Kolkata"
    tz = ZoneInfo(tz_name)
    now = datetime.now(tz)
    week_start = now - timedelta(days=now.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    week_end = week_start + timedelta(days=7)

    weekly_minutes = 0
    daily_data = []
    for i in range(7):
        day_start = week_start + timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        day_minutes = 0
        for row in rows:
            created_at = datetime.fromisoformat(row["created_at"])
            if day_start <= created_at < day_end:
                day_minutes += int(row["actual_minutes"])
        daily_data.append({
            "day": day_start.strftime("%a"),
            "date": day_start.strftime("%Y-%m-%d"),
            "minutes": day_minutes,
        })
        weekly_minutes += day_minutes

    recent_sessions = []
    for row in rows[:10]:
        created_at = datetime.fromisoformat(row["created_at"])
        recent_sessions.append({
            "id": row["id"],
            "route_name": row["route_name"],
            "actual_minutes": row["actual_minutes"],
            "created_at": created_at.strftime("%Y-%m-%d %H:%M"),
        })

    return jsonify({
        "week_minutes": weekly_minutes,
        "hours_reclaimed": round(weekly_minutes / 60, 2),
        "daily": daily_data,
        "recent_sessions": recent_sessions,
    })


init_db()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
