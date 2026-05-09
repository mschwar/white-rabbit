# Decision Log (ADRs)

Locked architectural and product decisions. Append new entries; **never edit historical ones**. If you believe a locked decision is wrong, surface it to Matt and (if accepted) write a *new* ADR that supersedes it. The old entry stays for the record.

Format: ADR-NNN — Title. Date. Status: Locked / Superseded by ADR-XXX. Context. Decision. Consequences.

---

## ADR-001 — Greenfield repo with modular code reuse

**Date:** 2026-05-05
**Status:** Locked

**Context.** The Scotty demo at `/Users/mschwar/Documents/proxy-lead` is Streamlit-based, fixture-coupled, and entangles demo concerns with real-search logic. Extending it to be a self-serve product would import that entanglement. Building from scratch lets us design recipe storage, the three-score model, and operator-time tracking from the start.

**Decision.** New repo at `/Users/mschwar/Documents/white-rabbit`. Lift load-bearing Python primitives from the demo (Tavily client, OpenAI extraction, Pydantic models, cost calculation) into `packages/core`. Throw away the Streamlit UI, fixtures, and orchestration. Build the new app on top of `packages/core`.

**Consequences.** Two repos to maintain (demo + product). Some upfront cost rebuilding orchestration. In exchange: clean schema, no demo-mode debt, free choice of frontend framework and auth model.

---

## ADR-002 — Stack: Next.js + Python (FastAPI) + Postgres

**Date:** 2026-05-05
**Status:** Locked

**Context.** Streamlit can't support real auth, multi-user state, or a real product UI. The Python ecosystem is where the search/extraction libraries already live (tavily-python, openai). Mixing them needs an HTTP boundary.

**Decision.**

- **Web layer:** Next.js (App Router, TypeScript, Tailwind, ESLint). Renders UI, handles auth, calls the Python API.
- **API layer:** Python (FastAPI). Owns all third-party calls (Tavily, OpenAI, future search vendors). Returns JSON.
- **Storage:** Postgres. Specific host TBD (Supabase, Neon, or local Docker — see open question in `STATUS.md`).
- **Communication:** Web ↔ API over HTTP. Web never holds API keys to upstream vendors.

**Consequences.** Two runtimes to operate. Two `node_modules` and one `.venv`. In exchange: frontend stays clean, Python keeps its native search libraries, API keys are server-side, future swap of either side is feasible.

---

## ADR-003 — Auth: shared password (Sprint 1 only)

**Date:** 2026-05-05
**Status:** Locked

**Context.** Three operators (Matt, Thomas, Lee) need access. Building real auth (per-user accounts, sessions, password reset, MFA) is weeks of work that doesn't validate any product hypothesis. The kill/keep gate at 90 days will tell us whether to invest.

**Decision.** Single shared password gates the entire app. Read from env var `WR_SHARED_PASSWORD` (or its bcrypt hash, `WR_SHARED_PASSWORD_HASH`). Next.js middleware checks a session cookie set by `POST /login`. Use `crypto.timingSafeEqual` for the comparison.

**Consequences.** No per-user attribution at the data layer in Sprint 1 — recipes are owned by "the team" not individuals. If we need per-operator KPIs (e.g., minutes-per-usable-lead by operator), we'll either (a) infer from session metadata if available, or (b) ship a "who are you" picker after login that's not an auth boundary, just an analytics tag. Real auth waits for the kill/keep gate.

---

## ADR-004 — Scotty demo frozen indefinitely

**Date:** 2026-05-05
**Status:** Locked

**Context.** The demo at `/Users/mschwar/Documents/proxy-lead` works, has shipped collateral (FAQ PDF, POC offer template, presenter scripts), and serves the customer-facing job. Rewriting it as part of v2 risks breaking what's working without a forcing function.

**Decision.** No code changes to the demo repo. It stays at its current state. Sunset only when the v2 product can demonstrably do the demo job *better* than the existing app — and that's a future decision, not a current one.

**Consequences.** v2 cannot share code with the demo via imports — only via copy. The two repos drift over time. Acceptable cost; the alternative (forcing them to share) would couple them again and undo ADR-001.

---

## ADR-005 — Shared internal API token for web-to-API boundary

**Date:** 2026-05-09
**Status:** Locked

**Context.** The rebuild audit found the backend endpoints could be called directly even though the UI was password-gated. The product does not need per-user auth yet, but it does need the web app and API to agree on one internal boundary so the protected routes cannot bypass the shell.

**Decision.** Protect the backend boundary with a shared internal token in `WR_API_INTERNAL_TOKEN`. The Next.js proxy adds the token as `x-white-rabbit-internal-token` on protected API calls, and FastAPI rejects protected endpoints without that token. `GET /health` remains public.

**Consequences.** Local and deployed environments must provision the token alongside the shared password. Direct calls to the protected backend now fail without the token, and tests must cover both allowed proxy traffic and denied direct traffic. This keeps the boundary simple until the product has a stronger reason for per-user auth or ingress-only enforcement.

---

## How to add a new ADR

1. Pick the next ADR number (ADR-006, ADR-007, …).
2. Add an entry at the bottom of this file with the same format.
3. Set Status to "Locked" once Matt confirms.
4. If the new ADR overrides an old one, mark the old one's Status as "Superseded by ADR-NNN" but **do not delete or rewrite its body**.

ADRs are about "we considered alternatives and chose this." If the choice is trivial or reversible (e.g., a logging library), it doesn't need an ADR — just code it and note in commit message.
