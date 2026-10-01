# TechDigest — Deployment

**Live demo:** [tech-digest-mu.vercel.app](https://tech-digest-mu.vercel.app) · **API:** [techdigest-backend.onrender.com](https://techdigest-backend.onrender.com)

This is the real, verified setup — every step below was actually run against the services named, not a generic template. All four services are on free tiers.

## Services

| Service | Provider | Role |
|---|---|---|
| Postgres | [Neon](https://neon.tech) | The real database — articles, users, bookmarks, everything |
| Backend API | [Render](https://render.com) (Web Service) | Flask + gunicorn, Dockerfile-based |
| Scheduled ingestion | GitHub Actions | Runs ingestion + AI summarization — scheduled every 15 minutes, in practice every few hours (measured; see limitations) |
| Frontend | [Vercel](https://vercel.com) | Static Vite build |
| Redis | [Upstash](https://upstash.com) | Provisioned, currently **unused** — see below |

## Why this doesn't mirror local dev's architecture exactly

Locally (`docker-compose.yml`), ingestion and AI summarization run through a persistent Celery worker + Beat scheduler, backed by Redis — the real async architecture this project is built around, complete with retry/backoff, task idempotency, and its own test suite (see `docs/architecture.md`).

Production doesn't use that, for one concrete reason: **Render's free tier only covers Web Services.** Both a persistent Background Worker and a Cron Job require a paid plan there — discovered by actually trying to create them, not from reading pricing docs in advance. Rather than pay for an always-on process to handle a workload that's genuinely light (a handful of new articles per run), scheduled ingestion moved to a **GitHub Actions workflow** (`.github/workflows/production-ingestion.yml`) on a `cron: "*/15 * * * *"` schedule, running a synchronous script (`backend/scripts/run_production_pipeline.py`) directly against Neon and OpenRouter — no queue, no broker, no persistent process.

This preserves the actual guarantee that matters — the API never blocks on ingestion or AI calls, since ingestion happens in a completely separate process on its own schedule — while trading Celery's in-process retry/backoff and task concurrency for a simpler, cron-run equivalent (bounded retries tracked in `processing_failures`, spread across scheduled runs instead of seconds apart). For this workload's actual volume, that's a reasonable fit, not a downgrade pretending not to be one. Honest caveat, measured rather than assumed: GitHub treats a `*/15` cron as a request, not a promise — across 299 real runs the median gap between runs was about 2.3 hours (90th percentile ~5 hours, worst gap ~45 hours). So feed freshness is measured in hours, not minutes. Acceptable for a demo news digest; not something to describe as "every 15 minutes."

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
OPENROUTER_MODEL=nvidia/nemotron-3-super-120b-a12b:free
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
- **Ingestion is far less frequent than its schedule.** The workflow requests every 15 minutes; GitHub actually ran it a median of ~2.3 hours apart (p90 ~5h, worst gap ~45h, from 299 recorded runs). New articles appear in batches, hours apart.
- **Free-tier AI is unreliable in two different ways.** Individual calls get rate-limited or hit `503` from OpenRouter's shared pools — the pipeline retries those on later runs, and a run reports only a `503` message, not a crash. Separately, the free *catalog itself churns*: the model chosen at launch was retired within a day (see the incident below). The current model is set in `.github/workflows/production-ingestion.yml`; if it stops working, list `https://openrouter.ai/api/v1/models`, filter for `:free`, and test candidates before switching — don't assume a name that used to work still does.
- **A run that summarizes nothing now fails visibly.** `scripts/run_production_pipeline.py` exits non-zero when it attempted summaries and none succeeded, so a red run in the Actions tab means something systemic broke (model retired, key revoked, provider down) — individual failures still don't turn it red. It only helps if someone looks: check that GitHub's Actions notifications are enabled for the account.
- **Dependencies that change behavior are pinned.** `SQLAlchemy` and `alembic` are pinned in `backend/requirements.txt` because an unpinned SQLAlchemy 2.1 silently changed the default Postgres driver and broke every fresh install (CI, Docker builds) while an older local environment kept working.
- **A one-time data seed.** The 137 articles present at initial deploy were copied from local dev (`scripts/copy_articles_to_production.py`) so the demo didn't start empty — everything since then is live, real ingestion.

## Post-launch incidents

**Part 1 — summarization silently stopped for a month (Aug 24 – Sep 26).** No new article was summarized, so the feed (which shows only summarized articles) stopped updating — while the scheduled workflow kept reporting success. The free model selected at launch had been retired by OpenRouter; every summarization call returned `404`, the pipeline caught each failure per article (by design, so one bad article can't sink a run) and exited 0. Nothing checked whether *any* article had succeeded. It was found when a separate failure finally turned the job red: an unpinned dependency had changed SQLAlchemy's default Postgres driver, breaking fresh installs. Fixes: dependencies pinned, model replaced with one verified against known-correct classifications, the job now fails when a run makes zero progress, per-run summarization is capped, and the OpenRouter client reports upstream error bodies instead of an opaque `KeyError`. Articles that exhausted their retry budget during the outage were marked `failed` and have to be reset deliberately.

**Part 2 — the fix above had its own bug (Sep 30).** The new "fail on zero progress" rule correctly flagged a run where all 25 attempts hit `429` (a brief, real rate-limit spike on OpenRouter's shared free pool) — but the assumption that the next run would simply retry those articles was wrong. The cap selected the newest 25 pending articles each run, and a continuous stream of fresh ingestion kept out-ranking the rate-limited batch indefinitely — not delayed, potentially never retried. Fixed by making "already failed at least once" the primary selection priority, with recency only as a tiebreak, so a retry's position can only ever improve. Verified against the real database: all 18 previously-stuck articles were summarized on the next real run after the fix.
