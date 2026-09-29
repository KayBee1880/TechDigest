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

## M6 — CI/CD ✅
- `backend-ci.yml`, `frontend-ci.yml`, `docker-build.yml` GitHub Actions.
- Ruff added to the backend (`pyproject.toml`) — first lint run caught real issues (unsorted imports, an outdated `typing.Callable` import, a missing exception chain in `app/tasks.py`).
- Branch protection expectations: PRs required against `main`, all three checks (Backend CI, Frontend CI, Docker Build) must pass before merge — enforced by workflow design (`pull_request` trigger) even before GitHub's branch protection rules are turned on in repo settings.
- Real gap CI caught that local checks missed: the PR's first run had two failures — an ESLint `react-refresh/only-export-components` error (`AuthContext.tsx` exported both a component and a hook; fixed by moving `useAuth` into its own file) and, once that was fixed, a TypeScript error in `articles.ts` that the failed lint step had been blocking from ever running. See `private/interview-notes.md`.

## Visual redesign & categories (between M6 and M7) ✅
- **Backend:** AI-based category classification, extending the existing summarization pipeline to also classify each article into one of nine CS-field categories in the same Ollama call. `GET /api/articles?category=X` filter, `GET /api/articles/categories` taxonomy endpoint. All 136 existing articles backfilled against the real Ollama instance.
- Two real findings along the way: classification was non-deterministic (Ollama's default sampling temperature, not the prompt — fixed with `temperature: 0`), and the backfill script had no resilience to a single slow request (crashed partway through a real run; fixed with per-article error handling). See `private/interview-notes.md`.
- **Frontend:** clean editorial/news-feed visual redesign — serif headlines, warm neutral palette, a manual light/dark theme toggle (persisted, defaults to system preference, no flash-of-wrong-theme on load) — plus category filter chips on the feed wired to the endpoints above.
- **Feed correctness fix:** the redesign briefly exposed real articles with no summary in the feed (still `summary_status="pending"`) — undercut the app's core premise, so `ArticleService.list_articles` now only returns articles with a completed summary and category.
- **Bookmark notes:** the account-creation pitch was previously just "so you can bookmark," which is thin — added a `notes` field on bookmarks so a saved article can carry a short personal note, with the note UI intentionally split (quick, optional capture right after saving; full editing on the Saved page).
- Real UX bugs caught by using the shipped features, not by tests: "Save for later" gave no feedback on an already-saved article (fixed by checking real bookmark state instead of trusting local mutation state); the note field stayed open indefinitely after saving; the Saved page's "Remove" button disabled every saved article while any one delete was in flight (one shared mutation reused across a list instead of scoped per item, caught via DevTools network throttling). Full write-ups in `private/interview-notes.md`.

## M7 — Deployment ✅
Live: [tech-digest-mu.vercel.app](https://tech-digest-mu.vercel.app) (frontend) · [techdigest-backend.onrender.com](https://techdigest-backend.onrender.com) (API). Full setup, real architecture divergence from local dev, and honest limitations: `docs/deployment.md`.

- **Production AI provider:** Ollama can't run on a free-tier host (a persistent, resource-heavy local process), but the deployed app still needs to keep summarizing/classifying new articles as they're ingested. Added `OpenRouterClient`, a second `AIProviderClient` implementation using OpenRouter's free-tier models — a config change (`AI_PROVIDER=openrouter`), not an application-code change, exercising the swappable-provider abstraction for the first time with a real second provider. Local dev keeps using Ollama.
  - Extracted the prompt-building and JSON-parse-with-fallback logic (previously Ollama-specific) into shared functions in `ai_provider.py`, now used by both clients — the second provider needing identical behavior is what justified the refactor.
  - Real finding: the first free-tier model name picked from memory had been retired by OpenRouter; found a working one (`nvidia/nemotron-nano-9b-v2:free`) by querying OpenRouter's own live model catalog instead of guessing again, then verified it against the same real articles already validated against Ollama's classification — identical categories, confirmed deterministic.
- **Hosting: Neon (Postgres), Render (backend API), Vercel (frontend).** Backend + worker were planned for Render/Railway, but Render's free tier turned out to cover Web Services only — Background Workers *and* Cron Jobs both require a paid plan, discovered by actually trying to create them. Rather than pay for an always-on process handling a genuinely light workload, scheduled ingestion + summarization moved to a **GitHub Actions cron workflow** instead, running a synchronous script directly against Neon and OpenRouter every 15 minutes — no Celery, no Redis, no persistent worker in production. Local dev's full Celery/Redis/Beat architecture is unchanged and still runs via `docker compose up`; this is a deployment-layer simplification, not an architecture rewrite. Full reasoning: `docs/deployment.md`, `private/interview-notes.md`.
- **Upstash Redis** is provisioned but currently unused in production — kept intentionally (free tier, zero cost) rather than torn down, in case a future traffic increase ever justifies a real persistent worker.
- **Post-launch incident (Aug 24 – Sep 26):** the free AI model chosen at launch was retired by OpenRouter within a day, and summarization silently stopped for a month — the pipeline handled each per-article failure and exited 0, so the scheduled job stayed green while the feed froze. It was uncovered by a separate failure (an unpinned SQLAlchemy 2.1 changed the default Postgres driver, breaking fresh installs). Fixed with pinned dependencies, a verified replacement model, a job that now fails when a run makes zero progress, a per-run summarization cap, and a client that surfaces upstream error bodies. Also measured: GitHub's `*/15` schedule actually ran a median ~2.3 hours apart. Details and the honest limits of the fix: `docs/deployment.md`.
- One-time data seed: the 137 articles already summarized/categorized locally were copied to Neon (`scripts/copy_articles_to_production.py`) so the deployed demo didn't start empty; everything since has come from real, live scheduled ingestion.

## M8 — Documentation & polish
- Full README (screenshots, setup, demo link).
- `docs/api-design.md`, `docs/database-schema.md`, `docs/async-processing.md`, `docs/security.md`, `docs/testing-strategy.md`, `docs/design-decisions.md`.
- Known limitations + roadmap-beyond-v1 section.

## Explicitly future (post-portfolio-v1)
Personalization/ranking, multi-language, notifications/email digests, social features, admin dashboard, dedicated search engine, multi-tenant accounts — see `docs/project-definition.md`.
