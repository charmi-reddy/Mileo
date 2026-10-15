---
doc: prd
status: approved
---

# Commute Hours — Product Requirements

One line: a mobile-first app that turns daily commute time into a small, optional study break without pressure or unsafe use.
Source: `scope.md > The Core Loop`, `scope.md > The Unique Kernel`, and `scope.md > What "Working" Looks Like`.

## The Core Journey
1. The user opens the app on their phone and sees a concise setup screen.
2. They enter a route nickname such as "Home to college" and a one-way commute time in minutes.
3. They choose a 5, 10, or 15 minute session that fits within their commute duration.
4. The app opens a flashcard view showing one Python interview question at a time.
5. The user taps "Show answer" to reveal the short answer and then taps either "Understood" or "Review again."
6. The app advances to the next card and shows a progress indicator like "3 of 10."
7. The user continues until all cards are finished or taps "End early."
8. A confirmation screen asks, "How many minutes did you actually study?" with the planned time prefilled so they can adjust it.
9. The user taps Save and sees a clear confirmation that the session was saved.
10. The dashboard updates immediately to show this week's study minutes as "hours reclaimed" and a daily bar chart.
11. If the user refreshes the page, the saved session and totals remain visible.
12. If a save is mistaken, the user can fix it from the dashboard by deleting the session; edit is a stretch goal only.

## Screens and Layout
The app is designed for a narrow phone screen and follows a simple single-column flow:
- Setup / session planner
- Flashcard study screen
- Save confirmation screen
- Weekly dashboard with hours reclaimed and recent sessions
- Bottom-sheet session actions for correcting a mistaken save

The layout is uncluttered, with big tap targets and concise text. The app does not require a complicated navigation model for this proof of concept.

## Look and Feel
The product should feel calm, minimal, trustworthy, and low-pressure. It should not feel gamified or socially competitive. The visual language is clean and modern, with large buttons, strong readability, and a quiet tone that reinforces that rest is valid and that the app is for passengers only, not for driving or walking.

## Features and Behavior

### Setup and session planning
- The user sees a setup screen with a route nickname field and a one-way commute duration in minutes.
- The user can enter a route nickname such as "Home to college" or another label that makes sense for their daily trip.
- The user picks a 5, 10, or 15 minute session option.
- The setup screen includes a short line that makes the product's intent clear: it is for commuting time, and resting is fine.
- The app requires the commute time to be at least the chosen session length; otherwise it shows a clear message and does not continue.
- Planned time never counts as completed study; only actual confirmed study minutes count.

### Flashcard study flow
- The user sees one Python interview-prep flashcard at a time.
- The card includes a question and a short answer hidden until the user taps "Show answer."
- After reading the answer, the user taps either "Understood" or "Review again."
- The app advances to the next card and shows progress, such as "3 of 10."
- The user can end the session early with "End early" instead of finishing the full deck.
- The app treats each session as a real-use decision, not an open-ended study challenge.

### Save and confirmation
- At the end of the session, the user lands on a confirmation screen asking: "How many minutes did you actually study?"
- The planned session length is prefilled so the user can adjust it if needed.
- The app accepts only a valid number of minutes, and the value must not exceed the selected session duration.
- Zero minutes or invalid values produce a clear error message and are not saved.
- On successful save, the app shows a clear success message, such as "Session saved."
- The app stores only real, confirmed study minutes and never counts planned time.

### Dashboard and weekly summary
- The dashboard shows this week's study minutes as "hours reclaimed," using actual study minutes divided by 60.
- The dashboard also shows a simple daily bar chart for the current week.
- Weekly totals use Monday-Sunday boundaries in the user's timezone, defaulting to Asia/Kolkata.
- The dashboard remains correct after a page refresh.

### Recent sessions and correction flow
- Under the weekly chart, the dashboard includes a "Recent sessions" list with the date and minutes for the last 10 saved sessions.
- Tapping a recent session opens a bottom sheet designed for a narrow phone screen.
- The bottom sheet offers one action:
  - "Delete session"
- Delete is the must-have recovery action for the proof of concept.
- Delete flow:
  - The user is asked to confirm: "Delete this session? Your weekly total will update."
  - Confirming the delete removes the session immediately.
  - The total and chart update immediately to reflect the deletion.
- Edit minutes is explicitly a stretch goal and is not part of the required proof of concept.
- No undo history, no bulk edits, and no account system are part of this proof of concept.

## States and Boundaries
- **First use** — The user sees a clean setup screen with empty fields and a brief supportive line about the app's purpose.
- **Valid setup** — Route nickname and commute duration are entered, and the session buttons are available.
- **Invalid setup** — Empty or malformed values trigger a clear validation message.
- **Study session active** — One question is visible at a time and the answer is hidden until the user reveals it.
- **Session complete or ended early** — The user reaches the confirmation step and records actual minutes.
- **Invalid save** — Zero, empty, or over-limit minutes trigger an error message and do not save.
- **Saved session** — Success is visible and totals update immediately.
- **Dashboard after refresh** — Saved data remains visible and correct after reload.
- **Deleted session** — The session disappears from the recent list and totals update immediately.

## Product Decisions
- The product is intentionally single-user and local to the proof of concept.
- Planned time is not treated as study time until actual minutes are confirmed.
- Rest is a valid choice and is explicitly supported in the product messaging.
- A commute duration must be at least the chosen session length, otherwise the user sees a clear message and cannot proceed.
- The must-have recovery flow is delete, because it corrects the worst mistake: a wrongly saved session inflating the total.
- Edit minutes is a stretch goal, not a required part of the prototype.
- The app intentionally excludes GPS, maps, route optimization, fares, and live data to stay in the proof-of-concept boundary.

## What We're Building
The proof of concept must include:
- Setup screen with route nickname, commute time, and session length choices
- Single-card flashcard flow with reveal and review tracking
- End-of-session actual-minute confirmation
- Save validation and success state
- Weekly dashboard with totals and daily chart
- Recent sessions list and delete flow that updates totals immediately
- Persistence across refresh
- Clear empty, invalid, and zero-value states

## Deferred From the POC
- Account systems and login
- Social features and leaderboards
- GPS, maps, or route optimization
- Transit fares or real route data
- Live AI generation or dynamic deck creation
- Audio, podcasts, or reminders
- Multiple topics
- Offline queued sync
- Edit-minutes correction flow beyond the stretch goal

## Possible Later Enhancements
- Offline save queue and sync
- Additional decks or optional audio content
- More detailed analytics and richer weekly insights
- Edit-minutes flow as a polished correction feature
- More accessibility polish and empty-state improvements

## Non-Goals
- Social comparison or public leaderboards
- Real-time trip optimization or travel planning
- Account-based data or social sharing
- AI-generated personalized study decks in the first build
- Multiple topics or dynamic content beyond the bundled Python deck

## Open Questions
- The exact wording of the validation messages can be chosen during the build as long as the behavior is clear and user-friendly.
- The "Recent sessions" list is limited to the last 10 saved sessions and does not require filtering by week unless product needs expand later.

