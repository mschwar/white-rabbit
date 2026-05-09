# 02 — Stack

## Tech choices (locked — see ADR-002)

- **Web:** Next.js 14+ (App Router), TypeScript, Tailwind CSS, ESLint.
- **API:** Python 3.12+, FastAPI, Pydantic, openai SDK, tavily-python.
- **Storage:** Postgres (host TBD — see open question in `STATUS.md`; recommendation: Supabase if speed matters, Neon if Postgres-native ergonomics matter, local Docker for dev only).
- **Package management:** `npm` for web (yarn / pnpm acceptable but pick one and stick with it), `uv` for Python (Poetry acceptable as fallback).
- **Auth (Sprint 1):** shared password via Next.js middleware. See ADR-003.

## Repo layout

```
/Users/mschwar/Documents/white-rabbit/
├── AGENTS.md                  # Agent entry point.
├── README.md                  # Human entry point.
├── STATUS.md                  # Live state. Update every session.
├── .gitignore
├── docs/                      # All architectural and product docs here.
│   ├── 00-context.md
│   ├── 01-model.md
│   ├── 02-stack.md            # ← you are here
│   ├── 03-decisions.md
│   ├── 04-roadmap.md
│   └── 05-reuse.md
├── apps/
│   ├── web/                   # Next.js. `npm run dev` → :3000.
│   │   ├── src/
│   │   │   ├── app/           # App Router pages.
│   │   │   ├── middleware.ts  # Shared-password gate.
│   │   │   └── lib/           # Client utilities (incl. API client).
│   │   ├── package.json
│   │   └── tsconfig.json
│   └── api/                   # FastAPI. `uv run uvicorn api:app --reload` → :8000.
│       ├── api/               # Python package.
│       │   ├── __init__.py
│       │   ├── main.py        # FastAPI app entry, route definitions.
│       │   └── routes/
│       ├── pyproject.toml
│       └── tests/
└── packages/
    └── core/                  # Lifted Python primitives (see docs/05-reuse.md).
        ├── core/
        │   ├── __init__.py
        │   ├── models.py
        │   ├── search.py
        │   ├── orchestrator.py
        │   ├── cost.py
        │   └── (email_patterns.py deleted in BUILDOUT-08)
        ├── pyproject.toml
        └── tests/
```

`apps/api` depends on `packages/core` via local path install (`uv add ../../packages/core --editable` or pyproject path dependency). This keeps `core` independently testable and importable into `api`.

## Communication contract

Web ↔ API over HTTP (JSON). Web never holds upstream API keys (Tavily, OpenAI). All third-party calls happen in the Python service.

Sprint 1 endpoints (FastAPI):

```
POST /scout
  body: { "query": str, "filters": {...} }
  returns: { "leads": [Lead, ...], "metrics": RunMetrics }
```

Future endpoints (Sprint 2+):

```
POST /full
GET  /recipes
POST /recipes
POST /runs/{id}/feedback
```

The Next.js side proxies through `app/api/*` routes (or calls FastAPI directly). Either is fine; recommend proxying through Next.js so the browser can rely on relative URLs and same-origin cookies.

## Conventions

### TypeScript / Next.js

- App Router only. No `pages/` directory.
- Server Components by default. Client Components opt-in via `'use client'` directive.
- Tailwind for styling. No CSS-in-JS libraries.
- Path alias `@/*` → `src/*` (set during `create-next-app`).
- One file per route.
- No global state libraries (Redux, Zustand) until Sprint 2 — local state + URL state is enough.

### Python / FastAPI

- All inputs and outputs validated by Pydantic models.
- All third-party clients (`OpenAI`, `TavilyClient`) instantiated once at module import, configured via env.
- All public functions in `core/` typed with explicit annotations.
- Errors are raised, not returned. FastAPI converts to HTTP responses via exception handlers.
- Test files mirror source structure (`core/orchestrator.py` → `tests/test_orchestrator.py`).
- Use `pytest`. No magic test discovery — use explicit `test_*.py` filenames.

### Git / commits

- `main` is the working branch. Direct commits OK during bootstrap and Sprint 1.
- Conventional commit prefixes: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`.
- One logical change per commit.
- Push when ready (no remote yet — establish remote when first deploy is needed).

### Naming

- Files: `kebab-case` for Next.js routes/components, `snake_case` for Python.
- Symbols: `PascalCase` for TS types and Python classes, `camelCase` for TS functions/vars, `snake_case` for Python functions/vars.

## Environment variables

### `apps/web/.env.local`

```
WR_SHARED_PASSWORD=<set this before running>
WR_API_BASE_URL=http://localhost:8000
WR_SESSION_SECRET=<random 32-byte hex>
```

### `apps/api/.env`

```
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
DATABASE_URL=postgresql://...   # Sprint 2+
```

`WR_SHARED_PASSWORD` is the shared password. Optionally store the bcrypt hash as `WR_SHARED_PASSWORD_HASH` and compare against that — preferred for Sprint 2+, optional for Sprint 1.

`WR_SESSION_SECRET` is used to sign the auth cookie. Rotate if compromised.

**Never commit any of these.** `.env*` is in `.gitignore`.

## Auth (Sprint 1)

```ts
// apps/web/src/middleware.ts (sketch)
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const PUBLIC_PATHS = ['/login', '/api/login'];

export function middleware(req: NextRequest) {
  const path = req.nextUrl.pathname;
  if (PUBLIC_PATHS.some(p => path.startsWith(p))) {
    return NextResponse.next();
  }
  const session = req.cookies.get('wr_session')?.value;
  if (!session || !verifySession(session)) {
    return NextResponse.redirect(new URL('/login', req.url));
  }
  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
```

`POST /api/login` reads the password from the form, compares against `WR_SHARED_PASSWORD` using `crypto.timingSafeEqual`, and on success sets a signed `wr_session` cookie (HMAC-SHA256 with `WR_SESSION_SECRET`). Cookie attrs: `HttpOnly`, `Secure` (in production), `SameSite=Lax`, `Path=/`.

## Local dev workflow

```bash
# Terminal 1 — API
cd apps/api && uv run uvicorn api:app --reload --port 8000

# Terminal 2 — Web
cd apps/web && npm run dev

# Visit
open http://localhost:3000
```

## Testing strategy

- **Unit tests** in `packages/core/tests/` — fast, no network. Mock `tavily-python` and `openai` at the module boundary.
- **API integration tests** in `apps/api/tests/` — hit the FastAPI app via `TestClient`. Mock the `core` orchestrator at the route boundary.
- **Web tests** — minimal in Sprint 1. Add Playwright in Sprint 3 if needed.
- **Smoke test** — one end-to-end test that runs a real Scout query against real APIs. Gated behind `RUN_LIVE=1` env var so it doesn't run in CI by default.

## Deploy (deferred)

No deploy in Sprint 1. Local-only is fine. When deploy is needed:

- **Web:** Vercel (one-click for Next.js, free tier covers internal use).
- **API:** Fly.io or Render. Avoid Vercel's serverless functions for the Python side — they're awkward for long-running search/extraction.
- **DB:** Supabase or Neon (managed Postgres).

This needs an ADR when it happens.

## Versions checklist (Sprint 1 baseline)

When scaffolding, lock to these majors at minimum:

| Tool | Min version | Why |
|---|---|---|
| Node | 20 LTS | Next.js 14+ requires Node 18.17+; LTS is safer. |
| Python | 3.12 | Modern type syntax, `@override`, performance. |
| Next.js | 14 | App Router stable, Server Actions. |
| FastAPI | 0.110+ | Pydantic v2 support. |
| Pydantic | 2.x | Models in `core/` use v2 syntax. |
| openai | 1.x (latest) | Structured outputs, latest models. |
| tavily-python | latest | API stability matters. |
| Postgres | 15+ | Generated columns, performance. |

Pin exact versions in lockfiles after scaffolding.
