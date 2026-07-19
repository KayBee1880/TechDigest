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

## M2 — Article ingestion (synchronous first)
- `NewsProviderClient` implementations for HN API + 2-3 RSS feeds.
- `NewsIngestionService`: normalize + dedupe + persist.
- A manual script (`scripts/ingest_articles.py`) to run ingestion on demand.
- Tests with mocked HTTP responses (no live network calls in CI).

## M3 — Asynchronous processing
- Redis + Celery wired into Docker Compose.
- Move ingestion to a scheduled Celery Beat task.
- `SummarizationService` + `AIProviderClient` (Ollama default, swappable).
- Retry/backoff, `processing_failures` tracking, idempotent task design.
- Worker tests (mocked AI calls).

## M4 — REST API
- `ArticleService`, `SearchService`, `BookmarkService`, `UserService`.
- Endpoints: list/filter/search articles, article detail, auth (JWT), bookmarks CRUD.
- Marshmallow/Pydantic schemas for request/response validation.
- API integration tests.

## M5 — Frontend
- Vite + React + TypeScript + Tailwind scaffold.
- React Query API layer, React Router routes.
- Feed, article detail, search/filter UI, saved articles, auth screens.
- Loading/empty/error states for every data-fetching view.
- Component + hook tests (Vitest + RTL).

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
