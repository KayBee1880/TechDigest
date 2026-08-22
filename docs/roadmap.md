# TechDigest — Milestone Roadmap

Each milestone should be its own set of commits/PRs, not one giant drop. Order matters — later milestones depend on earlier ones actually running.

## M0 — Architecture & repo skeleton (this milestone)
- Project definition, architecture doc, repo structure.
- Root config files (`.gitignore`, `.env.example`, `docker-compose.yml` skeleton, `README.md`, `LICENSE`).
- Empty-but-structured `frontend/` and `backend/` trees.

## M1 — Backend foundation
- Flask app factory, config classes (dev/test/prod via env vars).
- SQLAlchemy models: `users`, `article_sources`, `articles`, `summaries`, `bookmarks`, `ingestion_jobs`, `processing_failures`.
- Alembic migrations.
- Health check endpoint (`/health`).
- Pytest setup with a test database.
- ~~Docker Compose: Postgres + backend running together~~ — Postgres is containerized; the backend's `Dockerfile` is deferred to M3, so it can be written once alongside the Celery worker's (they'll likely share most of the same image). Don't drop this — needs to land before M7 deployment.
- Repository-layer tests deferred to M2, once a repository layer actually exists to test.

## M2 — Article ingestion (synchronous first) — done
- `NewsProviderClient` implementations for HN API + 2-3 RSS feeds.
- `NewsIngestionService`: normalize + dedupe + persist.
- A manual script (`scripts/ingest_articles.py`) to run ingestion on demand.
- Tests with mocked HTTP responses (no live network calls in CI).

## M3 — Asynchronous processing — done
- Redis + Celery wired into Docker Compose (`worker` + `beat` services, sharing `backend`'s Dockerfile).
- Ingestion moved to a scheduled Celery Beat task (`ingest_all_sources_task`, every 15 min).
- `SummarizationService` + `AIProviderClient` (Ollama default, swappable).
- Retry/backoff, `processing_failures` tracking, idempotent task design (`summarize_article_task`).
- Worker tests (mocked AI calls) — 28 tests total.
- Verified end-to-end against the real stack (not just mocked tests): real ingestion, real Celery hand-off between `backend` and `worker`, real Ollama summarization, Beat firing on schedule. Found and fixed a real concurrency mismatch (worker defaulted to 12 concurrent Ollama calls; capped at 2) during that run.

## M4 — REST API — done
- `ArticleService`, `BookmarkService`, `UserService`. No separate `SearchService` — search (Postgres `ILIKE` on title) is a single filter inside `ArticleService.list_articles`, not enough distinct logic yet to justify its own service class; revisit if search logic grows.
- Endpoints: list/filter/search articles, article detail, auth (JWT register/login), bookmarks CRUD, all behind a `login_required` decorator where relevant.
- Marshmallow schemas for request/response validation (chosen over Pydantic).
- API integration tests, plus service-level unit tests — 65 tests total.

## M5 — Frontend — done
- Vite + React + TypeScript + Tailwind CSS v4 scaffold.
- React Query API layer (`src/api/`, typed against the backend's Marshmallow schemas), React Router routes.
- Feed (search + pagination), article detail (with bookmarking), saved articles, login/register screens.
- Loading/empty/error states throughout every data-fetching view.
- Component + hook tests (Vitest + React Testing Library) — `pool: 'threads'` required on this machine (Windows-specific worker-spawning issue with Vitest's default pool; see `private/command-reference.md`).
- CORS enabled on the backend — a real gap the first live frontend request surfaced (no backend test goes through an actual browser, so 65 green tests gave zero signal).
- Found and fixed a real content-gap bug via actual use of the app: articles with no body text (mostly Hacker News link-posts) were getting nonsense AI "summaries" from title-only input; now correctly marked `summary_status="unavailable"`. Affected 90 of the articles ingested so far — see `private/interview-notes.md` for why fetching real article text is now a higher-priority future improvement than it first looked.

## M6 — CI/CD
- `backend-ci.yml`, `frontend-ci.yml`, `docker-build.yml` GitHub Actions.
- Branch protection expectations documented (PRs required, checks must pass).

## M7 — Deployment
- Frontend on Netlify/Vercel free tier.
- Backend + worker on Render/Railway free tier.
- Neon Postgres + Upstash Redis free tiers.
- Deployment guide in `docs/deployment.md`.

## M8 — Documentation & polish
- Full README (screenshots, setup, demo link).
- `docs/api-design.md`, `docs/database-schema.md`, `docs/async-processing.md`, `docs/security.md`, `docs/testing-strategy.md`, `docs/design-decisions.md`.
- Known limitations + roadmap-beyond-v1 section.

## Explicitly future (post-portfolio-v1)
Personalization/ranking, multi-language, notifications/email digests, social features, admin dashboard, dedicated search engine, multi-tenant accounts — see `docs/project-definition.md`.
