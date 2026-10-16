---
doc: spec
status: approved
---

# Mileo — Technical Spec

## How This Works, In Plain Language
Mileo is a local Flask app with a SQLite database and a mobile-first frontend. The user sets their commute, chooses a study session length, and generates a 10-question microlearning deck based on a topic and difficulty. If they want extra context, they can also upload a PDF, DOCX, or TXT file. The backend calls the Gemini API server-side using a local .env key and persists the generated deck and learning progress in SQLite. The user then studies the deck one card at a time, confirms actual minutes, and sees the weekly dashboard update.

This app is intentionally small and reliable: no login, no user accounts, no cloud sync, and no remote frontend API exposure. The app’s value is in the commute-learning loop, not infrastructure complexity.

## The Core Journey Through the System
1. The user loads the app and sees the setup screen.
2. The frontend loads saved settings from SQLite and pre-fills the route and commute values if present.
3. The user enters route nickname, commute minutes, and a custom session length.
4. The app validates that commute time is at least the chosen session length.
5. The user selects a topic and difficulty, and optionally uploads a document.
6. The frontend posts to `/api/ai/generate` with the topic, difficulty, and optional file.
7. The backend combines the upload text with the chosen topic/difficulty, calls Gemini, and validates that exactly 10 question objects are returned.
8. The frontend receives the deck and shows the first card.
9. The user taps reveal, marks understood or review again, and moves through the deck.
10. The session ends with the actual minute confirmation screen.
11. The frontend posts the session to `/api/sessions` and the backend stores it in SQLite.
12. The dashboard reads the weekly summary and recent sessions from SQLite and renders the updated totals.

## Stack
- Python 3.13+
- Flask
- SQLite
- vanilla JavaScript
- HTML/CSS
- Gemini API via server-side HTTP request
- python-dotenv for local environment loading
- optional document extraction via `pypdf` and `python-docx`

## Where It Runs and How Someone Tries It
The app runs locally in a browser via a local Flask server. There is no production deployment requirement for the proof of concept.

Run locally:
1. Open a terminal in the project folder.
2. Activate the virtual environment if present.
3. Run `pip install -r requirements.txt` if needed.
4. Start the app: `python app.py`
5. Open `http://127.0.0.1:5000`

The local .env file stores `GEMINI_API_KEY` and `GEMINI_MODEL`; it is not committed to git.

## Look and Feel
The UI is calm, minimal, and easy to trust. It uses:
- a light blue mobile-first palette
- large tap targets
- a single-column layout
- compact, readable copy
- clear validation and success states

## Components

### Setup screen
Displays route name, commute time, and the custom session length field. This is the entry point for the main learning flow.

### AI deck generation panel
Contains topic, difficulty, optional document upload, and the generate-deck action. Document upload is optional; topic + difficulty alone is enough to generate a valid deck.

### Study screen
Shows one question at a time, reveals the answer on tap, and lets the user select understood or review again.

### Confirmation screen
Asks how many minutes were actually studied, validates the value, and prevents duplicate saves.

### Dashboard
Shows total study minutes, hours reclaimed, a daily chart, and the last 10 recent sessions.

## Data Model

### Settings
- route_name: string
- commute_minutes: integer
- timezone: string (default Asia/Kolkata)

Stored in the `settings` table.

### Sessions
- id: integer primary key
- route_name: string
- planned_minutes: integer
- actual_minutes: integer
- created_at: ISO timestamp
- timezone: string

Stored in the `sessions` table and used for totals and recent-session history.

### AI batches
- id: integer primary key
- topic: string
- difficulty: string
- source_text: text
- created_at: ISO timestamp
- questions: JSON text

Stored in `ai_batches` and used to persist generated question sets.

### AI progress
- batch_id: integer primary key
- current_index: integer
- understood_count: integer
- updated_at: ISO timestamp

Stored in `ai_progress` so a user can resume a generated deck without regenerating.

### Per-card marks
- `Understood` and `Review again` are session-only UI marks.
- They do not persist beyond the current run.
- They influence the current study flow only.

## File Structure
```
project/
├── app.py
├── .env
├── .gitignore
├── requirements.txt
├── README.md
├── data/
│   └── app.db
├── templates/
│   └── index.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
├── tests/
│   └── test_app.py
├── devpost/
│   ├── scope.md
│   ├── prd.md
│   ├── spec.md
│   └── ...
└── .venv/
```

## External Services and Dependencies
The app depends on:
- Flask
- SQLite
- Gemini REST API
- python-dotenv
- optional PDF/DOCX/TXT extraction libraries

No API key is stored in frontend JavaScript. The key is loaded from a local `.env` file on the server.

## Important Failure Modes
- **Invalid commute/session mismatch** → app blocks progression and shows a clear validation message.
- **Zero or invalid actual study minutes** → app rejects the save with a validation error.
- **Gemini API failure** → backend returns a clear error and does not break the rest of the app.
- **Duplicate save** → the save button locks after first tap to prevent repeated saves.
- **Page refresh after session save** → dashboard and stored data remain intact because the app reads from SQLite.

## What Was Simplified and Why
- Single-user app: to keep the product local and easy to demo.
- Manual session length: to avoid forcing preset choices and support realistic commute planning.
- Optional file upload: to support grounded generation without making documents mandatory.
- SQLite as the source of truth: to match the app’s local-first architecture and keep data reliable.

## Decisions and Open Issues
Decisions made:
- Gemini generation is backend-only.
- Topic + difficulty alone is valid without upload.
- File upload is optional, not required.
- Local SQLite stores route, sessions, generated decks, and progress.
- The app is intentionally local and single-user.

Open issues to track later:
- richer document processing and stronger extraction fallback behavior
- more deck management actions such as edit/delete by saved batch
- possible analytics and history enhancements beyond recent sessions
