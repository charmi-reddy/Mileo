---
doc: checklist
status: approved
---

# Build Checklist

Build mode: fast

## Slices

- [ ] **1. Setup and route validation work end to end**
  Becomes usable: The app can load, save settings, and reject invalid commute/session combinations before the user starts a session.
  Why now: This proves the setup logic and validation are correct before the study flow is built on top.
  PRD ref: `prd.md > Setup and session planning`, `prd.md > States and Boundaries`
  Spec ref: `spec.md > Components`, `spec.md > Data Model`, `spec.md > Important Failure Modes`
  Build: Create the Flask app, SQLite setup, settings API, and the setup screen UI with validation rules.
  Verify (mechanical): Start the app, save valid settings, and confirm invalid combinations show a message instead of proceeding.
  Learner check: Open the app and try a valid route + commute time, then try a session longer than the commute and confirm the message is clear.
  Commit: `Add settings validation and app shell`

- [ ] **2. The flashcard loop is working**
  Becomes usable: The user can see one Python flashcard at a time, reveal the answer, choose understood or review again, and track progress.
  Why now: The unique kernel is the flashcard session itself, so it must exist before the dashboard and persistence are added.
  PRD ref: `prd.md > Flashcard study flow`, `prd.md > The Core Journey`
  Spec ref: `spec.md > Components`, `spec.md > Data Model`
  Build: Add the bundled flashcard deck, the card UI, answer reveal, progress counter, and the end-early flow.
  Verify (mechanical): Open the app, start a session, reveal answers, and confirm the counter advances correctly.
  Learner check: Complete a few cards and confirm the flow feels simple and readable on a phone screen.
  Commit: `Add flashcard study loop`

- [ ] **3. Sessions save correctly and weekly totals update**
  Becomes usable: The user can finish or end early, enter actual minutes, save the session, and see the dashboard totals update.
  Why now: The income-making behavior of the app is the saved study session and truthful totals.
  PRD ref: `prd.md > Save and confirmation`, `prd.md > Dashboard and weekly summary`
  Spec ref: `spec.md > Data Model`, `spec.md > Components`, `spec.md > Important Failure Modes`
  Build: Add the session save endpoint, actual-minute validation, save-button disable after tap, and the summary calculations using Monday-Sunday in Asia/Kolkata.
  Verify (mechanical): Save a valid session, then attempt zero and over-limit values to confirm validation blocks them. Reload the dashboard and confirm totals remain.
  Learner check: Save a session, confirm the success message appears, and check that the weekly total looks correct.
  Commit: `Add session save and truthful totals`

- [ ] **4. Recent sessions and delete correction flow work**
  Becomes usable: The user can review the last 10 sessions and remove a mistaken one from a mobile-friendly bottom sheet.
  Why now: This is the required fix for a wrong save and a must-have recovery flow.
  PRD ref: `prd.md > Recent sessions and correction flow`
  Spec ref: `spec.md > Components`, `spec.md > Important Failure Modes`
  Build: Add the recent-session list to the dashboard, bottom-sheet delete confirmation, and deletion logic that changes totals immediately.
  Verify (mechanical): Save a session, delete it, and confirm it disappears from the recent list and from the totals.
  Learner check: Create a mistaken session, delete it, and confirm the dashboard update is clear and immediate.
  Commit: `Add recent sessions and delete correction`

## Hands-on Checkpoints

- [ ] Early usable behavior explored — setup, validation, and flashcard loop walkthrough
- [ ] Final kick-the-tires exploration and feedback completed

## Final Review

- [ ] Final review complete — feedback resolved and learner confirms ready to ship

## Code Tour and App Map

- [ ] Learning activity complete — guided route, focused alternative, prior practice connected, or brief recap
- [ ] Optional edit and transfer reflection addressed — offered/declined/already covered/not applicable as appropriate
- [ ] `devpost/app-map.html` generated from finished code, checked, and shown, including a project-grounded practice to reuse

Activity and evidence: To be filled in after implementation and review.
Route and stops: To be filled in after implementation and review.
Edit outcome: To be filled in after implementation and review.
Reflection: To be filled in after implementation and review.
Activity mode: live app and editor

## Revisions

- [ ] No revisions yet.
