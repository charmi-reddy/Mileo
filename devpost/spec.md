---
doc: spec
status: draft
---

# Commute Hours — Technical Spec

## How This Works, In Plain Language
This app is a small, mobile-first web app built around one simple flow: the user enters their commute details, picks a study session that fits within that trip, works through a short Python flashcard deck, confirms the minutes they really studied, and then sees their weekly progress update. The whole app is built to prove one thing: a person can use part of their commute to do a short, optional learning session without creating pressure or assuming they studied more than they actually did.

The app will be a small Flask backend with a lightweight SQLite database and a vanilla JavaScript frontend. That keeps the project simple enough for a proof of concept while still matching the learner’s preference for Python, REST APIs, and SQL. The front end is a narrow-screen web app that behaves like a mobile app, and the backend exposes a few clear routes for settings, deck data, sessions, and summary data. The design is intentionally small: no login, no external services, no real-time syncing, and no location data.

## The Core Journey Through the System
The PRD core journey maps cleanly to a few small pieces:

1. The user opens the app and lands on the setup screen.
2. The browser loads the settings state and shows any saved route nickname or last-used commute time.
3. The user enters a route nickname and a commute duration in minutes, then chooses a session length.
4. The browser validates the chosen commute time: it must be at least the selected session length. If not, the app shows a message and prevents the session from starting.
5. The frontend requests the bundled deck from the backend, which serves a static list of 10 Python flashcards.
6. The user studies one card at a time, reveals the answer, marks it as understood or review again, and moves through the deck.
7. When the session ends, the app asks for the actual study minutes and validates the value before save.
8. The frontend sends the saved session to the backend via a POST endpoint.
9. The backend stores the completed session in SQLite and returns the updated weekly summary data.
10. The dashboard computes "hours reclaimed" from confirmed study minutes and updates the daily bar chart.
11. A refresh simply re-reads the persisted data from SQLite and the browser’s stored settings, so the values persist without login.
12. If a session is saved incorrectly, the user can open the dashboard’s recent-session list and delete the incorrect item. The total and chart update immediately.

PRD ref: `prd.md > The Core Journey`.

## Stack
- Python 3.x
- Flask for the backend web app
- SQLite for persistent local data
- vanilla JavaScript for the frontend UI logic
- HTML/CSS for the responsive mobile layout

Rationale:
- This matches the learner’s stated preference for Python, Flask, SQL, and REST APIs.
- It stays small, easy to run locally, and well-suited to a proof-of-concept app.
- It avoids adding a framework or extra service for a project whose value is in the core flow, not in infrastructure.

Documentation links:
- Flask: https://flask.palletsprojects.com/
- SQLite: https://www.sqlite.org/docs.html
- vanilla JavaScript: https://developer.mozilla.org/en-US/docs/Web/JavaScript

## Where It Runs and How Someone Tries It
This app runs locally in the browser and on a local Flask server. It does not require deployment to be valid for the hackathon demo, and deployment is optional.

Run locally:
1. Open a terminal in the project folder.
2. Create a Python virtual environment if desired.
3. Install dependencies: `pip install flask`
4. Start the app: `python app.py`
5. Open the browser to `http://localhost:5000`

For the required demo recording, the user will:
- open the app on the local server,
- enter a fictional route and commute duration,
- choose a valid session length,
- complete the flashcard flow,
- save a session,
- show the dashboard update after refresh.

The project should also include a README with quick start instructions and a short note that the app is local-only and intentionally avoids login, GPS, and other out-of-scope features.

## Look and Feel
The product should feel calm, minimal, and trustworthy. The UI should use:
- a light neutral palette with strong contrast for readability
- large tap targets for phone use
- a single-column mobile layout with generous spacing
- minimal copy that reinforces optional use and no pressure
- a compact dashboard that still makes the weekly totals easy to read

This matches the PRD’s look-and-feel direction and avoids the generic feel of a busy productivity app. The stack supports this easily with plain HTML/CSS and no heavy visual framework.

## Components

### App shell / setup screen
What it does: Shows the route nickname field, commute time, and session choice buttons, plus a brief note that this is for passengers and rest is fine.
PRD ref: `prd.md > Setup and session planning`.

### Flashcard session screen
What it does: Shows one question at a time, reveals the answer on demand, tracks progress like 3 of 10, and lets the user mark understood or review again.
PRD ref: `prd.md > Flashcard study flow`.

### Session confirmation screen
What it does: Asks the user how many minutes they actually studied, pre-fills the planned session length, validates the number, and triggers a save.
PRD ref: `prd.md > Save and confirmation`.

### Dashboard
What it does: Shows “hours reclaimed” and the daily bar chart, plus the list of recent sessions.
PRD ref: `prd.md > Dashboard and weekly summary` and `prd.md > Recent sessions and correction flow`.

### Session delete bottom sheet
What it does: Opens from a recent session, asks for confirmation, and removes the session while updating totals immediately.
PRD ref: `prd.md > Recent sessions and correction flow`.

## Data Model
The app needs a small, simple data model because this is a single-user local proof of concept.

### Settings
- route_name: string
- commute_minutes: integer
- timezone: string (default "Asia/Kolkata")

Stored in a `settings` table in SQLite. This is the source of truth. LocalStorage is only used as a cache layer for quick page refresh behavior; it must not be the primary store for settings.

### Sessions
- id: string or integer primary key
- route_name: string
- planned_minutes: integer
- actual_minutes: integer
- created_at: ISO timestamp
- timezone: string

Stored in a `sessions` table and used for totals and the recent-session list. Each session is immutable once saved, except for delete in the proof-of-concept flow. There is no account system or user table.

### Deck
- id: integer
- question: string
- answer: string
- explanation: string

Stored as a static list in a Python module or JSON file and served via the Flask API. This is bundled original content for the proof of concept.

### Per-card marks
- `Understood` and `Review again` are session-only UI marks.
- They do not persist individually to the database or localStorage.
- They influence the current session flow only, not session totals or historical records.

The app uses the actual study minutes for totals, not planned minutes. A session cannot claim more study minutes than the selected session duration.

## File Structure
```
project/
├── app.py                     # Flask app entry point
├── requirements.txt           # Python dependencies
├── README.md                  # Quick start and run instructions
├── devpost/
│   ├── learner-profile.md
│   ├── scope.md
│   ├── prd.md
│   ├── spec.md
│   └── ...
├── src/
│   ├── __init__.py
│   ├── config.py              # app config / defaults
│   ├── db.py                  # SQLite setup and queries
│   ├── deck.py                # bundled flashcard deck
│   ├── routes.py              # Flask routes for settings, deck, sessions, summary
│   ├── models.py              # optional lightweight helper models
│   └── utils.py               # helper functions for validation and weekly totals
├── templates/
│   ├── index.html             # app shell
│   ├── dashboard.html         # dashboard view if split into templates
│   └── ...
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── app.js
│   └── images/
│       └── ...
└── data/
    └── app.db                 # SQLite database at runtime
```

This structure keeps concerns separated without over-engineering the project. The frontend is simple; the backend is still clear enough to debug.

## External Services and Dependencies
The app relies on no external services beyond the local browser and local SQLite database.

No external API keys, no auth, and no cloud services are required for the proof of concept.

The only critical dependency list is:
- Flask
- Python standard library modules for SQLite and datetime handling
- browser local storage for optional UI persistence and page refresh continuity

## Important Failure Modes
- **Invalid commute/session mismatch** → the app shows a message saying the commute must be at least the selected session length and does not proceed.
- **Invalid or zero minutes on save** → the app shows a clear validation message and does not save.
- **Duplicate or accidental saved session** → the user can delete the session from the recent-session list, and the total updates immediately.
- **Page refresh with saved data** → the app rehydrates from SQLite and local settings so the dashboard and settings still show the user’s previous work.

## What Was Simplified and Why
- **Single-user local storage instead of auth or a multi-user backend** — the product is intentionally built for one person and a local proof of concept. Authentication would add a lot of complexity without helping prove the core learning loop.
- **Bundled flashcard deck instead of dynamic generation** — the deck is fixed and original so the app demonstrates the actual experience without depending on a live AI or external service.
- **No offline queueing for now** — offline behavior is intentionally deferred until the online flow is proven and polished.
- **Delete only for correction** — the must-have correction path is delete, while edit is left as a stretch goal because it is less essential to the actual product value.

## Decisions and Open Issues
Decisions made here:
- Use Flask + SQLite + vanilla JS to match the learner’s stated stack and keep the app small.
- Keep the app single-user, local-only, and intentionally non-social.
- Use local storage or server-side persistence for settings and session data, with SQLite as the main durable store.
- Keep the app’s scope to a single Python deck, a small dashboard, and a delete-only correction flow.
- Treat the commute duration as a required constraint: it must be at least the selected session length.

One genuine uncertainty discussed and clarified:
- The learner initially described a more elaborate dashboard and data model, but the product was simplified to a narrow mobile POC with a delete-only correction flow and no demo-week data. This was accepted as a deliberate size reduction in service of the proof of concept.

Open questions carried forward from the PRD:
- Exact validation-message wording can be chosen during implementation.
- The recent-session list is capped at the last 10 entries and does not need a week filter unless product needs expand later.
