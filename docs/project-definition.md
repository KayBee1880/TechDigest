# TechDigest — Project Definition

## Problem

Technology news is fragmented across dozens of sources (Hacker News, TechCrunch, Ars Technica, The Verge, GitHub Trending, Reddit). Reading everything is impractical, and most articles bury their key point in several paragraphs. TechDigest solves this by pulling articles from multiple sources into one place and using AI to generate a short summary for each one, so a reader can scan a day's tech news in a few minutes instead of an hour.

## Target users

- A developer or student who wants a daily digest of tech news without opening ten tabs.
- A recruiter or engineer evaluating this repository as a portfolio project — they are effectively a "user" of the *codebase*, not just the app.

Design decisions favor the second audience wherever the two conflict (e.g., prefer a clearly-documented, cleanly-separated backend over a marginally faster hack).

## Core user journeys

1. **Browse the feed** — user lands on the home page and sees recent articles with title, source, category, and AI summary.
2. **Filter/search** — user narrows the feed by category, source, or keyword.
3. **Read detail** — user opens an article to see the full summary and a link to the original source.
4. **Save for later** — a logged-in user bookmarks an article and finds it again under "Saved."
5. **(Implicit) Ingestion** — no human triggers this: a background worker periodically pulls new articles, deduplicates them, and queues them for summarization, so the feed stays fresh without user action.

## MVP scope

In scope for v1:
- Ingest articles from a small, fixed set of free sources (RSS feeds + Hacker News API).
- Deduplicate by canonical URL / content hash.
- Generate one summary per article via a configurable AI provider (local Ollama by default; swappable).
- REST API to list, filter, search, and fetch article detail.
- Basic user accounts (JWT auth) + bookmarks.
- React frontend: feed, detail page, filters, search, saved articles, loading/empty/error states.
- Background processing via Celery + Redis, with retries and status tracking.
- Dockerized local dev (single `docker compose up`).
- CI: lint + test on both frontend and backend, Docker image build.
- Deployed demo (free-tier hosting) with a working public URL.

## Explicitly postponed (not v1)

- Personalized recommendations / ranking algorithms.
- Multi-language support.
- Push notifications / email digests.
- Social features (comments, sharing, following other users).
- Admin dashboard / moderation tooling.
- Full-text search engine (Elasticsearch etc.) — start with Postgres `ILIKE`/trigram search, revisit only if it's genuinely insufficient.
- Multi-tenant or org accounts.

These are listed in `docs/roadmap.md` as "future" so the repo signals deliberate scoping rather than missing features.

## Keeping this from becoming over-engineered

- One backend service (modular monolith) + one worker process. No microservices — nothing here has independent scaling or deployment needs that would justify the operational cost.
- One AI provider abstraction, not a plugin marketplace. Support exactly the providers listed in the stack (Ollama, HF Inference, OpenRouter) behind one interface.
- One relational database. No polyglot persistence.
- Search starts as Postgres full-text search, not a dedicated search cluster.
- Every added dependency must map to a concept on the resume/job description (async processing, CI/CD, testing, deployment) — not added for novelty.
