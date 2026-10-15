# Commute Hours

A mobile-first app that lets a commuter choose a short optional learning session during public transport travel, study a packaged Python flashcard deck, confirm actual study minutes, and see the weekly summary update.

## Features
- Route nickname and one-way commute duration setup
- Session lengths of 5, 10, or 15 minutes
- Python interview-prep flashcards with answer reveal
- Actual study minutes confirmation and save validation
- Weekly dashboard showing hours reclaimed and daily totals
- Recent sessions list with delete-based correction flow

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open http://localhost:5000 in a browser.

## Notes
- Intended for a single local user, no login.
- Commute time must be at least the selected session length.
- Actual confirmed study minutes determine the weekly total.
- Planned time never counts.
