# TechDigest — Deployment

**Live demo:** [tech-digest-mu.vercel.app](https://tech-digest-mu.vercel.app) · **API:** [techdigest-backend.onrender.com](https://techdigest-backend.onrender.com)

This is the real, verified setup — every step below was actually run against the services named, not a generic template. All four services are on free tiers.

## Services

| Service | Provider | Role |
|---|---|---|
| Postgres | [Neon](https://neon.tech) | The real database — articles, users, bookmarks, everything |
| Backend API | [Render](https://render.com) (Web Service) | Flask + gunicorn, Dockerfile-based |
| Scheduled ingestion | GitHub Actions | Runs ingestion + AI summarization every 15 minutes |
| Frontend | [Vercel](https://vercel.com) | Static Vite build |
| Redis | [Upstash](https://upstash.com) | Provisioned, currently **unused** — see below |

## Why this doesn't mirror local dev's architecture exactly

Locally (`docker-compose.yml`), ingestion and AI summarization run through a persistent Celery worker + Beat scheduler, backed by Redis — the real async architecture this project is built around, complete with retry/backoff, task idempotency, and its own test suite (see `docs/architecture.md`).

Production doesn't use that, for one concrete reason: **Render's free tier only covers Web Services.** Both a persistent Background Worker and a Cron Job require a paid plan there — discovered by actually trying to create them, not from reading pricing docs in advance. Rather than pay for an always-on process to handle a workload that's genuinely light (a handful of new articles every 15 minutes), scheduled ingestion moved to a **GitHub Actions workflow** (`.github/workflows/production-ingestion.yml`) on a `cron: "*/15 * * * *"` schedule, running a synchronous script (`backend/scripts/run_production_pipeline.py`) directly against Neon and OpenRouter — no queue, no broker, no persistent process.

This preserves the actual guarantee that matters — the API never blocks on ingestion or AI calls, since ingestion happens in a completely separate process on its own schedule — while trading Celery's in-process retry/backoff and task concurrency for a simpler, cron-run equivalent (bounded retries tracked in `processing_failures`, spread across scheduled runs instead of seconds apart). For this workload's actual volume, that's a reasonable fit, not a downgrade pretending not to be one. Honest caveat: GitHub's scheduled workflows aren't guaranteed to fire at exactly `*/15` — GitHub can delay a scheduled run by several minutes under load. Fine here; nothing about this app is time-critical at the minute level.

**Upstash Redis** was originally provisioned for a persistent Celery worker under the original plan. It's kept, deliberately, even though nothing in production currently connects to it — costs nothing on the free tier, and stays available if real traffic ever justified paying for a persistent worker later.

## Production AI provider

Ollama (local dev's AI provider) is a persistent local server process — not something a free-tier host runs either. Production uses **OpenRouter** instead (`AI_PROVIDER=openrouter`), a free-tier-model-backed, OpenAI-compatible API — a config change, not an application-code change, since summarization already sits behind a swappable `AIProviderClient` interface. See `docs/architecture.md`'s AI-provider section.

## Environment variables

Set on both the Render backend service and the GitHub Actions workflow (as repository secrets, prefixed `PROD_` there):

```
APP_ENV=production
DATABASE_URL=<Neon connection string>
SECRET_KEY=<random, generated separately from local dev's>
JWT_SECRET_KEY=<random, generated separately from local dev's>
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=<OpenRouter API key>
OPENROUTER_MODEL=nvidia/nemotron-nano-9b-v2:free
CORS_ORIGINS=<the real deployed frontend URL>
```

`REDIS_URL` is set on the Render backend service (for consistency with local config shape) but not read by anything in the actual request path — the deployed API never touches Celery.

## Setting it up from scratch

1. **Neon**: create a project, run `flask db upgrade` against its connection string (`DATABASE_URL=<neon-url> flask db upgrade` from `backend/`), then seed sources (`python -m scripts.seed_sources`).
2. **Render**: New Web Service → connect the repo → Root Directory `backend` → Docker (auto-detected, no command override needed — the `Dockerfile`'s own `CMD` already runs `gunicorn`) → add the environment variables above.
3. **GitHub Actions**: add the four `PROD_*` secrets under the repo's Settings → Secrets and variables → Actions. The workflow only starts actually firing on schedule once it's merged to `main` — `workflow_dispatch` (manual "Run workflow") works from a feature branch for testing first.
4. **Vercel**: New Project → import the repo → Root Directory `frontend` → one env var, `VITE_API_BASE_URL=<render-backend-url>/api`.
5. Update Render's `CORS_ORIGINS` to the real Vercel URL once it's known (there's a real chicken-and-egg order here — the backend needs to exist before Vercel can point at it, and CORS needs Vercel's URL, so this is always a two-pass step).

## Known limitations, stated honestly

- **Cold starts.** Render's free web service spins down after inactivity; the first request after idle time can take ~50 seconds. Expected, not a bug.
- **Ingestion timing isn't exact.** GitHub Actions' `cron` schedule can drift by several minutes under platform load.
- **Free-tier AI reliability.** OpenRouter's free models occasionally return rate limits from their shared pool — the pipeline just retries on the next scheduled run rather than failing hard.
- **A one-time data seed.** The 137 articles present at initial deploy were copied from local dev (`scripts/copy_articles_to_production.py`) so the demo didn't start empty — everything since then is live, real ingestion.
