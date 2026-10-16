---
doc: prd
status: approved
---

# Mileo — Product Requirements

One line: a mobile-first app that helps commuters turn part of their journey into a short, optional study block without pressure, guilt, or unsafe behavior.

## The Core Journey
1. The user opens the app and lands on the setup screen.
2. They enter a route nickname such as "Home to office" and a one-way commute time in minutes.
3. They pick a study session length that fits within that commute, using a custom minute input rather than preset buttons.
4. They choose a topic and difficulty, and optionally upload a PDF, DOCX, or TXT file to ground the generated deck.
5. The app generates a 10-question deck and opens the study screen with the first card visible.
6. The user taps "Reveal answer" and then chooses either "Understood" or "Review again."
7. The app advances to the next card and continues until the deck is complete or the user ends early.
8. The confirmation screen asks, "How many minutes did you actually study?" and pre-fills the planned session length for adjustment.
9. The user taps Save and the app stores the real confirmed minutes in SQLite.
10. The dashboard updates immediately to show the week’s study minutes, hours reclaimed, and recent-session list.
11. If the user refreshes the page, the saved sessions and totals remain visible.
12. If a session was saved incorrectly, the user can delete it from the recent session list; editing a saved session is not required for this proof of concept.

## Screens and Layout
The app is designed for a narrow phone screen and follows a simple single-column flow:
- Setup / commute planner
- AI deck generation panel
- Flashcard study screen
- Study confirmation screen
- Weekly dashboard with totals and recent sessions

The layout is uncluttered, with big tap targets and concise labels. The app prioritizes clarity and speed over complicated navigation.

## Look and Feel
The app should feel calm, modern, and low-pressure. It should not feel gamified or socially competitive. The visual language is minimal and trustworthy, with strong contrast, roomy spacing, and large buttons on a mobile-first layout.

## Features and Behavior

### Setup and session planning
- The user sees a setup screen with a route nickname field and one-way commute duration in minutes.
- The user can manually enter a study session length that fits within that commute.
- The app validates that commute minutes are at least the selected study length; otherwise a clear error appears and the user cannot continue.
- The app is intentionally single-user and local-only.
- Planned study time never counts as completed study; only actual confirmed minutes count.

### AI microlearning flow
- The user can generate a deck by choosing a topic and difficulty.
- The user may optionally upload a PDF, DOCX, or TXT file to provide source material.
- If no file is uploaded, the deck still generates from the topic + difficulty alone.
- The backend generates exactly 10 questions, each with a question, an answer, and an explanation.
- Generated decks are persisted in SQLite and can be reused from the saved deck list.
- The app never exposes the Gemini API key in frontend code.

### Flashcard study flow
- The user studies one question at a time.
- The answer is hidden until the user taps "Reveal answer."
- The card can be marked either as understood or review again.
- The progress indicator shows the actual card count across the full deck, such as "1 of 10", "2 of 10".
- The user may end the session early.

### Save and confirmation
- The app asks how many minutes were actually studied.
- The planned session length is prefilled so the user can adjust it if needed.
- Only valid positive values that do not exceed the planned plan are accepted.
- The save button is disabled after the first tap to avoid duplicate saves.
- On success, the app shows a message and keeps the weekly totals accurate.

### Dashboard and weekly summary
- The dashboard shows current-week study minutes and hours reclaimed.
- Weekly totals use Monday-Sunday boundaries in the local timezone, defaulting to Asia/Kolkata.
- The dashboard includes a recent sessions list with the last 10 entries.
- The dashboard remains accurate after a page refresh.

### Recent sessions and correction flow
- The recent sessions list contains the last 10 saved sessions.
- The must-have correction flow is Delete.
- Delete asks for confirmation and updates the totals immediately.
- Edit is not required for the proof of concept.

## States and Boundaries
- **First use** — setup screen is empty and ready for route and commute details.
- **Valid setup** — route, commute time, and custom session length are accepted.
- **Invalid setup** — empty route, invalid commute, or session greater than commute triggers a clear message.
- **Deck generation** — topic/difficulty alone works, upload is optional.
- **Study session active** — one card is visible at a time and answer is hidden until revealed.
- **Session complete or ended early** — user proceeds to actual-minute confirmation.
- **Invalid save** — zero or over-limit values are rejected.
- **Saved session** — totals update immediately and persist in SQLite.
- **Deleted session** — the session is removed and totals update immediately.

## Product Decisions
- The product is intentionally single-user and local.
- Planned minutes are never treated as completed study time.
- A commute must be at least the selected session length.
- The app should reinforce that rest is valid and that study should feel optional and calm.
- The main correction path is delete, because it fixes the most damaging mistake: an inflated session total.
- The AI deck is generated in the backend only; no API key is shipped to the browser.

## What We're Building
The proof of concept includes:
- Setup with route name and commute time
- Manual session-length input
- AI deck generation from topic + difficulty, with optional document context
- 10-question flashcard study flow
- Save validation and duplicate-prevention behavior
- Weekly dashboard and recent sessions
- SQLite persistence and refresh safety

## Deferred From the POC
- Login and account systems
- Social features or leaderboards
- GPS route tracking or transit trip optimization
- Advanced analytics beyond weekly totals
- Multiple user accounts or cross-device sync

## Possible Later Enhancements
- More deck management tools and saved content history
- Better AI prompts and richer document extraction
- More detailed analytics and dashboard filters
- Accessibility and UX refinement

## Non-Goals
- Public comparison features
- Real-time route optimization
- Account-based data or social sharing
- Mandatory document uploads for every deck
- Complex multi-user infrastructure

## Open Questions
- The exact wording of validation messages can be finalized during implementation, as long as they are clear and helpful.
- The recent sessions list will stay capped at the last 10 entries unless the product expands later.

