---
doc: scope
status: draft
---

# Commute Hours

A mobile-first app that turns a commute into a small, optional learning break without adding pressure or unsafe screen use.

## The Unique Kernel
The distinctive idea is a commute-aware micro-learning app that treats study as optional, bounded, and grounded in real travel time. The user chooses a session length that fits within their one-way commute, studies from a short Python interview-prep deck, and only counts confirmed study minutes after the session ends. It is not a productivity app, a to-do app, or a gamified learning platform—it is a respectful, small-learning tool built around a real daily pain point and a real daily decision.

## Who It's For
A student or software intern who commutes by public transport for around two hours each way and wants a low-pressure way to use part of that time for learning. The app is for passengers only; it is never used while driving, cycling, or crossing roads. The person wants a clean, low-friction experience that does not turn the commute into a demand or a guilt loop.

## The Core Loop
The user opens the app, enters a route nickname and one-way commute duration, chooses a 5, 10, or 15 minute session that fits, and then studies a deck of Python interview-prep flashcards one by one. They reveal the answer, mark a card as understood or review again, and end the session early or complete it. At the end, they confirm actual study minutes and save the session. The dashboard then shows this week’s real study minutes as “hours reclaimed,” alongside a simple daily bar chart. Planned time never counts toward completed study.

## Inspiration & Identity
This should feel calm, minimal, and trustworthy. The visual identity is a clean phone-first layout: large flashcard, clear actions, minimal friction, and a compact weekly summary. The mood is practical and uplifting, not gamified, not noisy, and not guilt-inducing. Rest is a valid choice; the app should reinforce that the commute is still a commute.

## Why This Matters to the Learner
This matters because the learner experiences a real daily problem: a large amount of time is lost to commuting, and a small, optional study break feels like a meaningful improvement without becoming another obligation. The app is built around a real personal habit and a real personal tension: using commute time well without demanding too much from the self.

## What "Working" Looks Like
The proof of concept is a narrow-phone app where a user can enter route details, start a valid session length, complete a short flashcard flow, confirm actual minutes, and save a session. After refresh, the saved data still appears on the dashboard. The app handles zero-session and invalid-input states with clear messages. The weekly total is based on real confirmed study minutes and is shown as “hours reclaimed” with a daily bar chart. A fictional demo week is visibly labeled and separated from real totals.

## The POC Boundary
In scope:
- One local user, no login
- Route nickname plus one-way commute duration in minutes
- One bundled Python interview-prep deck with 10 flashcards
- 5, 10, and 15 minute session lengths
- Reveal-answer + understood/review-again flow
- Actual study minutes confirmation and session save
- Weekly summary as hours reclaimed and daily bar chart
- Duplicate prevention, invalid input handling, zero-session states, edit/delete flows
- Refresh persistence for settings and completed sessions
- Demo week kept visibly separate from real data
- Mobile-first responsive layout

Out of scope for the first proof:
- Accounts and login
- Social features and leaderboards
- GPS, maps, route optimization, fares, or transit data
- Live AI generation or audio content
- Podcasts, audio downloads, reminders, or multiple decks/topics
- Offline support until the core flow is validated

## Later
- Offline queued saves with IndexedDB and sync once the online flow works
- Additional decks or optional audio content
- More polished accessibility and empty states
- Broader weekly analytics and richer visualization
- Extra user preferences or route history

## Explicitly Cut
- Accounts and social features: not needed for a solo personal tool and would expand the product beyond the single-user proof.
- GPS/maps and route optimization: the app is intentionally not location-aware and does not depend on user travel data.
- Transit fares and live routing: this is not a trip-planning app and would broaden the scope beyond the learning session goal.
- Live AI generation: the deck is bundled and fixed for the proof of concept; dynamic generation is a later milestone.
- Multiple topics and reminders: one topic and one focused flow are enough to prove the value of the concept.
- Offline support before online validation: offline queueing is useful, but it should come after the core session flow is proven working.
