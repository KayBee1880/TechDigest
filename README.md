# TechDigest

AI-powered technology news aggregator. Pulls articles from multiple free sources, generates concise AI summaries in the background, and serves them through a React frontend backed by a Flask REST API.

> Status: early scaffold (M0 — architecture & repo structure). See [docs/roadmap.md](docs/roadmap.md) for the build plan.

## Why this project exists

Reading tech news means checking many sources and skimming long articles. TechDigest aggregates sources into one feed and summarizes each article with AI, processed asynchronously so the app stays responsive. See [docs/project-definition.md](docs/project-definition.md) for the full problem statement, users, and scope.

## Architecture

See [docs/architecture.md](docs/architecture.md) for the full data flow (source → ingestion → DB → async summarization → API → frontend), failure handling, deduplication, and rate-limiting strategy.

## Stack

- **Frontend**: React, TypeScript, Tailwind CSS, TanStack Query, React Router, Vitest, React Testing Library
- **Backend**: Flask, SQLAlchemy, PostgreSQL, Redis, Celery, Pytest, Marshmallow
- **Infra**: Docker Compose, GitHub Actions, free-tier hosting (Netlify/Vercel + Render/Railway + Neon + Upstash)
- **AI**: Ollama (local) by default, swappable for Hugging Face Inference or OpenRouter free-tier models

## Repository structure

```
techdigest/
  frontend/     React + TypeScript SPA
  backend/      Flask API + Celery worker (modular monolith)
  docs/         Architecture, API, schema, deployment, testing docs
  scripts/      Seed data, ingestion, worker helper scripts
  .github/      CI workflows, issue/PR templates
```

## Local setup

Not yet runnable end-to-end — backend and frontend scaffolding land in M1/M5. Once available:

```bash
cp .env.example .env
docker compose up
```

## Documentation

- [Project definition](docs/project-definition.md)
- [Architecture](docs/architecture.md)
- [Roadmap](docs/roadmap.md)

## License

MIT — see [LICENSE](LICENSE).
