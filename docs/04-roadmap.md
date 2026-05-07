# 04 — Roadmap

## Sprint 1 — Scaffold (current)

**Goal.** Thomas can run his first real Scout query through the new product end-to-end on his laptop.

**In scope.**

1. `apps/web` scaffolded with Next.js (App Router, TypeScript, Tailwind, ESLint, src dir).
2. `apps/api` scaffolded with FastAPI (uv-managed, Python 3.12+, Pydantic, openai, tavily-python).
3. `packages/core` populated with lifted modules per `docs/05-reuse.md`:
   - `models.py` (extended with three scores)
   - `cost.py` (with current 2026 prices, not stale 2025 prices)
   - `search.py` (Tavily primitive)
   - `orchestrator.py` (rewritten without LangChain)
4. Shared-password auth via Next.js middleware. Env: `WR_SHARED_PASSWORD`. Implemented in `apps/web` as login/logout routes, cookie middleware, and protected home/Scout shells.
5. End-to-end: form in Next.js → `POST /api/scout` → FastAPI `/scout` → orchestrator → Tavily + OpenAI → leads with three scores → JSON back → render.
6. Smoke tests: orchestrator returns valid LeadList for a known query; auth middleware rejects bad password.

**Out of scope (Sprint 1).**

- Postgres / persistence (Sprint 2).
- Recipe storage (Sprint 2).
- Scout vs. Full distinction in the UI (Sprint 2 — Sprint 1 only ships Scout).
- Five-button feedback per lead (Sprint 2).
- Operator-time logging (Sprint 2).
- Per-recipe scoreboard (Sprint 3).
- Deploy (Sprint 3 or later — local-only is fine for Sprint 1).
- HubSpot CSV export (defer until first user asks).
- Bulk / batch processing (Sprint 4).

**Definition of done.** Documented in `STATUS.md` "Definition of done for Sprint 1." Thomas runs one query, sees ranked leads with three scores and explanations, in under 30 seconds.

---

## Sprint 2 — Persistence + Recipes

**Goal.** Every Full run produces a stored recipe. Lee/Thomas can mark feedback per lead.

**In scope.**

1. Postgres provisioned. Schema: `recipe`, `recipe_run`, `lead`, `lead_feedback`. (See schema sketch below.)
2. Scout vs. Full distinction:
   - Scout: 10–20 leads, no recipe stored.
   - Full: requires explicit confirmation with cost estimate; up to 100 leads; recipe stored on completion.
3. Five-button feedback per lead: `usable` / `wrong persona` / `bad source` / `bad contact` / `duplicate`. Required to close out a Full run.
4. Operator-time logging: timer that starts when results render, stops when run is closed out. Self-report fallback ("I spent N minutes").
5. Recipe library page: list saved recipes, reload, re-run.

**Out of scope.**

- Recipe sharing across operators (Sprint 3 — also needs ADR on "team" vs "owner").
- Per-recipe scoreboard analytics (Sprint 3).
- Recipe editing (Sprint 3 — Sprint 2 ships read + re-run only).

### Schema sketch (Postgres, Sprint 2)

```sql
create table recipe (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  query text not null,
  filters jsonb default '{}'::jsonb,
  source_mix jsonb default '{}'::jsonb,
  weights jsonb default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table recipe_run (
  id uuid primary key default gen_random_uuid(),
  recipe_id uuid references recipe(id) on delete cascade,
  mode text not null check (mode in ('scout', 'full')),
  started_at timestamptz not null default now(),
  ended_at timestamptz,
  operator_minutes numeric,
  api_cost_breakdown jsonb default '{}'::jsonb,
  lead_count integer not null default 0
);

create table lead (
  id uuid primary key default gen_random_uuid(),
  run_id uuid not null references recipe_run(id) on delete cascade,
  data jsonb not null,
  fit_score numeric,
  evidence_score numeric,
  contact_score numeric,
  gate_passed boolean,
  rank integer
);

create table lead_feedback (
  lead_id uuid primary key references lead(id) on delete cascade,
  label text not null check (label in ('usable', 'wrong_persona', 'bad_source', 'bad_contact', 'duplicate')),
  created_at timestamptz not null default now()
);
```

This is a sketch. Sprint 2 may refine. Refinements append a new ADR.

---

## Sprint 3 — Operator scoreboard + sort controls

**Goal.** Per-recipe metrics surface so the team can see what works.

**In scope.**

- Per-recipe scoreboard: API cost spent, leads returned, usable count, **minutes per usable lead**, **API cost per usable lead**. Shipped in `feature/sprint3-recipe-scoreboard`.
- Sort-by-score controls in the lead view (sort by Fit, Evidence, Contact, or pass/fail gate). Shipped in `feature/sprint3-sort-controls`.
- Friday-of-week recipe-review export (a printable / shareable summary of the week's recipes). Shipped in `feature/sprint3-friday-export`.

---

## Sprint 4 — Batch + bulk

**Goal.** Run multiple recipes in sequence overnight or on a schedule.

**In scope.**

- CSV / JSON ingestion of multiple queries.
- Sequential execution with the cap structure (caps on source searches, extracted pages, LLM calls, elapsed time, estimated spend).
- Per-batch summary.

---

## 90-day kill/keep gate

The gate determines whether to invest in self-serve, multi-tenant, and external customer access. **All** of these must hold:

1. **Thomas usage retention.** Thomas runs the tool ≥ 3× per week through week 12 (not just initial enthusiasm in weeks 1-2).
2. **Recipe volume.** ≥ 30 distinct recipes saved across Lee + Thomas.
3. **Headline KPI.** Median **minutes of operator review per usable lead < 10** (Thomas's runs specifically).
4. **Customer-facing proof.** ≥ 2 paid boutique briefings delivered by Matt with customer-confirmed "usable" rating ≥ 75%.
5. **Recipe reuse.** At least one recipe pattern reused across two different ICPs without rebuild.
6. **Public content.** Lee or Thomas has published ≥ 1 piece of public content about using the tool.

If any miss at 90 days: rethink. Most likely failure modes:

- Thomas stops using it after week 2 (friction-heavy vs. his current flow).
- Recipes don't generalize across ICPs (every customer needs a custom build → no operating leverage).
- Content motion never materializes (Lee/Thomas didn't post → no marketing flywheel).

If the gate passes: open Sprint 5 work — multi-user accounts, real billing, public landing page, customer onboarding flow.

If it fails: do **not** automatically scale down. Diagnose which criterion failed and decide per cause. Some failures (no content) might be solved with a commercial arrangement; some (no recipe reuse) might mean the boutique model itself doesn't have leverage.

---

## What's NOT on the roadmap (and shouldn't be without an ADR)

- Self-serve external signup
- Multi-tenant / per-org / per-team account hierarchy
- Billing / subscription
- Public marketing site (separate from the README)
- Mobile app
- Browser extension
- Slack/Teams integration
- Email enrichment via paid providers (Apollo, Hunter, etc.)
- LinkedIn scraping (legal + TOS minefield)

Each of these can be discussed but only as a future sprint with an ADR justifying it.
