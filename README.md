# mynance
Applicazione per gestire le proprie finanze

> Personal-finance companion. Initialized from the official
> [`fastapi/full-stack-fastapi-template`](https://github.com/fastapi/full-stack-fastapi-template)
> (AR-Init / Story 1.1) and restyled to the **"Morbido"** design system.

## Stack

- **Backend** — FastAPI + SQLModel/SQLAlchemy 2 + Alembic + Pydantic v2, deps via `uv`. API under `/api/v1`; OpenAPI is the canonical contract; errors as `application/problem+json` (RFC 9457).
- **Frontend** — React 19 + Vite + TypeScript + TanStack Query/Router, **Tailwind v4 + shadcn/ui**, package manager **Bun**. Talks to the backend **only** through the generated client in `frontend/src/lib/api/`.
- **DB** — PostgreSQL (local: compose; deploy: Neon). **Money is stored as integer cents** (see below).
- **Design** — "Morbido" tokens as CSS custom properties (light/dark, system default + manual override) in `frontend/src/theme/`.

## Local development

```bash
cp .env.example .env          # fill values; .env is gitignored
docker compose up             # api + db + frontend (hot reload both sides)
# regenerate the typed API client after backend changes:
bash scripts/generate_client.sh
```

Backend at `http://localhost:8000` (`/api/v1/docs`), frontend at `http://localhost:5173`.

## Conventions (binding)

- **Money = integer minor units (cents)** on `BIGINT *_cents` columns — **never** a float or a localized string in the DB/API. Formatting to `€ 1.234,56` (Italian) happens **only** at the frontend display layer (`frontend/src/lib/format.ts`); cents helpers live in `backend/app/calc/money.py`. See `_bmad-output/planning-artifacts/architecture.md` (Anti-patterns).
- **Italian domain nouns verbatim** in code (`Utente`, `Movimento`, `Spesa`, `Secchiello`, …); snake_case DB/JSON; PascalCase React components.
- **Never recompute derived money client-side** — always call the API; the generated client is the only egress.
- Every query is scoped by `utente_id` (per-Utente isolation).

Planning artifacts (PRD, UX, architecture, epics) live under `_bmad-output/`.
