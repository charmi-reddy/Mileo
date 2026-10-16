---
doc: scope
status: approved
---

# Mileo

A mobile-first commute learning app that helps a commuter turn part of their trip into a focused, optional microlearning session without pressure or unsafe use.

## The Unique Kernel
The distinctive idea is a commute-aware learning app that treats study as optional, bounded, and grounded in real travel time. The user enters a route and commute duration, sets a custom session length that fits within the trip, and then starts a study flow built around a quick AI-generated deck. The deck can be generated from a selected topic and difficulty, with an optional PDF, DOCX, or TXT upload for more grounded content. Only confirmed study minutes count toward the weekly total; planned time never does.

## Who It's For
This is for a student, learner, or working professional who commutes regularly and wants a low-pressure way to make that time productive. The app is intentionally designed for passengers only and is not built for driving, walking, or real-time travel planning. The user values a simple, calm experience that is easy to trust and easy to finish.

## The Core Loop
The user opens the app, enters a route nickname and one-way commute time in minutes, and chooses a study session length that fits inside that commute. They can optionally upload a document or simply choose a topic and difficulty to generate a 10-question deck. The app then presents one question at a time, reveals the answer on demand, and lets the user mark the card as understood or review again. After the session, the user confirms the actual minutes studied and saves the session. The dashboard then updates the current week’s totals and recent session list. Planned time never counts toward completed study.

## Inspiration & Identity
The product should feel calm, minimal, and trustworthy. The visual language is clean, compact, and phone-first: large buttons, clear labels, strong contrast, and a quiet, reassuring tone. It is not a game, not a leaderboard, and not a guilt-driven productivity tool. Rest is a valid choice, and the app should reinforce that the commute is still a commute.

## Why This Matters to the Learner
The learner is trying to make daily travel time more useful without turning it into another source of pressure. The app reduces friction by turning commute minutes into a small, bounded microlearning block that can support repetition and recall without feeling like a big commitment.

## What "Working" Looks Like
The proof of concept is a narrow-phone app where a user can set up a route and commute, generate a valid 10-question deck from either topic/difficulty or an uploaded document, study through the deck, confirm actual minutes, and save a session. After refresh, the saved data remains visible. The app handles zero-session, invalid-input, and over-limit states with clear validation. The dashboard shows this week’s study minutes and recent sessions in local time, defaulting to Asia/Kolkata.

## The POC Boundary
In scope:
- One local user, no login
- Route nickname and one-way commute duration in minutes
- Custom manual session length entry
- Topic + difficulty AI deck generation
- Optional PDF, DOCX, or TXT upload for additional source context
- 10-question learning deck generation with answer/explanation output
- Reveal-answer + understood/review-again flow
- Actual study minutes confirmation and session save
- Weekly summary as hours reclaimed and daily chart
- Recent sessions list with delete flow
- SQLite persistence for app settings, sessions, and AI-generated batches
- Refresh persistence for settings and saved history
- Mobile-first responsive layout

Out of scope for the first proof:
- Accounts and login
- Social features and leaderboards
- GPS, maps, travel routing, or fare data
- Audio, podcasts, or reminders
- Multiple users or real-time sync
- Complex AI chat flows or long-form content generation
- LocalStorage as the primary source of truth

## Later
- Better deck management and saved deck reuse
- More advanced AI and prompt tuning
- Additional study analytics and richer dashboards
- Improved accessibility and visual polish
- More document types and smarter content grounding

## Explicitly Cut
- Account-based features and shared histories
- Public comparison or leaderboards
- Travel optimization and route intelligence
- AI as a mandatory requirement for every deck generation
- Overly complex or multi-user infrastructure

## Final product intent
The current product is a local, single-user microlearning app that helps commuters turn part of their journey into a small, useful study habit using a lightweight AI deck without adding friction or pressure.
