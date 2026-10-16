---
doc: checklist
status: approved
---

# Build Checklist

Build mode: fast

## Slices

- [x] **1. Setup and route validation work end to end**
  Becomes usable: The app can load, save settings, and reject invalid commute/session combinations before the user starts a session.
  Why now: This proves the setup logic and validation are correct before the study flow is built on top.
  PRD ref: `prd.md > Setup and session planning`, `prd.md > States and Boundaries`
  Spec ref: `spec.md > Components`, `spec.md > Data Model`, `spec.md > Important Failure Modes`
  Build: Create the Flask app, SQLite setup, settings API, and the setup screen UI with validation rules.
  Verify (mechanical): Start the app, save valid settings, and confirm invalid combinations show a message instead of proceeding.
  Learner check: Open the app and try a valid route + commute time, then try a session longer than the commute and confirm the message is clear.
  Commit: `Add settings validation and app shell`

- [x] **2. AI deck generation and optional document grounding work**
  Becomes usable: The user can select a topic and difficulty, optionally upload a source file, and generate a 10-question deck without requiring a document.
  Why now: The AI deck is the main value-adding layer of the product and differentiates it from a static flashcard set.
  PRD ref: `prd.md > AI microlearning flow`, `prd.md > The Core Journey`
  Spec ref: `spec.md > Components`, `spec.md > Data Model`, `spec.md > External Services and Dependencies`
  Build: Add the topic/difficulty form, optional upload support, backend Gemini call, and deck validation for exactly 10 questions.
  Verify (mechanical): Generate a deck from topic + difficulty alone and then with a document attached. Confirm the backend validates the structure and returns a valid deck.
  Learner check: Confirm the app can generate a useful study set without forcing a document upload.
  Commit: `Add AI deck generation and optional upload support`

- [x] **3. The study loop saves truthful minutes and updates totals**
  Becomes usable: The user can study the deck, confirm actual study time, and save a session without overstating the effort.
  Why now: Truthful minutes are the core trust mechanism in the app and the key to a useful weekly dashboard.
  PRD ref: `prd.md > Flashcard study flow`, `prd.md > Save and confirmation`, `prd.md > Dashboard and weekly summary`
  Spec ref: `spec.md > Data Model`, `spec.md > Components`, `spec.md > Important Failure Modes`
  Build: Add the card flow, answer reveal, progress tracking, save-button lock, and dashboard totals using Monday-Sunday in Asia/Kolkata.
  Verify (mechanical): Save a valid session, reject an invalid value, reload the page, and confirm totals remain consistent.
  Learner check: Confirm the deck counter shows real absolute progress and the stored total reflects actual minutes instead of planned time.
  Commit: `Add AI study flow and truthful totals`

- [x] **4. Recent sessions and delete correction flow work**
  Becomes usable: The user can review recent sessions and remove a mistaken save from the dashboard.
  Why now: This is the required correction mechanism for user trust and accurate weekly totals.
  PRD ref: `prd.md > Recent sessions and correction flow`
  Spec ref: `spec.md > Components`, `spec.md > Important Failure Modes`
  Build: Add the recent-session list, delete confirmation flow, and chart/summary recalculation after removal.
  Verify (mechanical): Save a session, delete it, and confirm the session disappears from the recent list and from the totals.
  Learner check: Create a mistaken session, remove it, and verify the dashboard updates immediately.
  Commit: `Add recent sessions and delete correction`

## Hands-on Checkpoints

- [x] Early usable behavior explored — setup, validation, deck generation, and study loop walkthrough
- [x] Final kick-the-tires exploration and feedback completed

## Final Review

- [x] Final review complete — feedback resolved and product flow matched the final project direction

## Code Tour and App Map

- [x] Learning activity complete — guided route, focused alternative, prior practice connected, or brief recap
- [x] Optional edit and transfer reflection addressed — offered/declined/already covered/not applicable as appropriate
- [x] `devpost/app-map.html` generated from finished code, checked, and shown, including a project-grounded practice to reuse

Activity and evidence: The final project was reviewed against the actual app behavior: custom session length, topic/difficulty generation, optional upload support, secure `.env` handling, persisted SQLite totals, and delete-based correction flow.
Route and stops: Setup → AI deck generation → study loop → actual-minute confirmation → dashboard summary → delete correction.
Edit outcome: Product docs and build checklist were aligned to the final working flow.
Reflection: The app is intentionally narrow, local, trust-building, and low-pressure; the key product principle is that planned time is never treated as completed study time.
Activity mode: live app and editor

## Revisions

- [x] Final alignment completed for the current Mileo flow.
