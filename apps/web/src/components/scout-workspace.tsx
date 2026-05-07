'use client';

import { FormEvent, useState } from 'react';
import {
  buildScoutPayload,
  buildFullPayload,
  closeRecipeRun,
  DEFAULT_SCOUT_LOCATION,
  DEFAULT_SCOUT_QUERY,
  formatScore,
  LEAD_SORT_OPTIONS,
  sortScoutLeads,
  submitLeadFeedback,
  type LeadSortMode,
  type ScoutResponse,
  type FullResponse,
} from '@/lib/scout';

function formatElapsedSeconds(seconds: number): string {
  return `${seconds.toFixed(2)}s`;
}

type Mode = 'scout' | 'full';

export default function ScoutWorkspace() {
  const [query, setQuery] = useState(DEFAULT_SCOUT_QUERY);
  const [location, setLocation] = useState(DEFAULT_SCOUT_LOCATION);
  const [recipeName, setRecipeName] = useState('');
  const [mode, setMode] = useState<Mode>('scout');
  const [results, setResults] = useState<ScoutResponse | null>(null);
  const [fullResult, setFullResult] = useState<FullResponse | null>(null);
  const [queryGuardrail, setQueryGuardrail] = useState<ScoutResponse['query_guardrail']>(null);
  const [operatorMinutes, setOperatorMinutes] = useState('');
  const [closeMessage, setCloseMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [sortMode, setSortMode] = useState<LeadSortMode>('rank');
  const [isClosing, setIsClosing] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const payload = mode === 'scout'
      ? buildScoutPayload(query, location)
      : buildFullPayload(query, location, recipeName);

    if (!payload) {
      setError('Enter a query before searching.');
      setResults(null);
      setFullResult(null);
      return;
    }

    setIsLoading(true);
    setError(null);
    setResults(null);
    setFullResult(null);
    setQueryGuardrail(null);

    try {
      const endpoint = mode === 'scout' ? '/api/scout' : '/api/full';
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const bodyText = await response.text();
        let message = `Search failed (${response.status}).`;
        let guardrail: ScoutResponse['query_guardrail'] = null;

        if (bodyText) {
          try {
            const body = JSON.parse(bodyText) as {
              error?: string;
              detail?: unknown;
              query_guardrail?: ScoutResponse['query_guardrail'];
            };
            guardrail = body.query_guardrail ?? null;
            if (typeof body.detail === 'string') {
              message = body.detail;
            } else if (body.detail && typeof body.detail === 'object') {
              const detail = body.detail as { error?: string; detail?: unknown };
              message = detail.error ?? message;
            }
            message = body.error ?? message;
          } catch {
            message = bodyText;
          }
        }

        setQueryGuardrail(guardrail);
        throw new Error(message);
      }

      if (mode === 'scout') {
        const data = (await response.json()) as ScoutResponse;
        setResults(data);
        setQueryGuardrail(data.query_guardrail ?? null);
      } else {
        const data = (await response.json()) as FullResponse;
        setFullResult(data);
        setResults({ leads: data.leads, metrics: data.metrics, query_guardrail: data.query_guardrail ?? null });
        setQueryGuardrail(data.query_guardrail ?? null);
        setCloseMessage(null);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Search failed.';
      setError(message);
      setResults(null);
      setFullResult(null);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleCloseRun() {
    if (!fullResult) {
      return;
    }

    const parsed = Number.parseFloat(operatorMinutes);
    if (!Number.isFinite(parsed) || parsed <= 0) {
      setCloseMessage('Enter operator minutes greater than 0.');
      return;
    }

    setIsClosing(true);
    setCloseMessage(null);
    try {
      await closeRecipeRun(fullResult.run_id, parsed);
      setCloseMessage(`Run closed with ${parsed.toFixed(1)} operator minutes.`);
    } catch (err) {
      setCloseMessage(err instanceof Error ? err.message : 'Failed to close run.');
    } finally {
      setIsClosing(false);
    }
  }

  const displayedResults = results;
  const displayedLeads = displayedResults ? sortScoutLeads(displayedResults.leads, sortMode) : [];

  return (
    <main className="min-h-screen bg-zinc-950 px-6 py-10 text-zinc-50">
      <section className="mx-auto flex w-full max-w-6xl flex-col gap-8 rounded-[2rem] border border-white/10 bg-white/5 p-8 shadow-2xl shadow-black/20 backdrop-blur sm:p-10">
        <div className="space-y-3">
          <p className="text-sm font-medium uppercase tracking-[0.22em] text-emerald-300">Scout / Full</p>
          <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">Query workspace</h1>
          <p className="max-w-3xl text-base leading-7 text-zinc-300 sm:text-lg">
            Scout: quick preview (10–20 leads, no storage). Full: stored recipe with up to 100 leads.
          </p>
        </div>

        <div className="grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
          <section className="rounded-3xl border border-white/10 bg-zinc-950/70 p-6">
            <p className="text-sm font-medium uppercase tracking-[0.18em] text-zinc-400">Start a query</p>
            <form className="mt-4 grid gap-5" onSubmit={handleSubmit}>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setMode('scout')}
                  className={`flex-1 rounded-full px-4 py-2 text-sm font-semibold transition ${
                    mode === 'scout'
                      ? 'bg-emerald-400 text-emerald-950'
                      : 'bg-white/5 text-zinc-300 hover:bg-white/10'
                  }`}
                >
                  Scout
                </button>
                <button
                  type="button"
                  onClick={() => setMode('full')}
                  className={`flex-1 rounded-full px-4 py-2 text-sm font-semibold transition ${
                    mode === 'full'
                      ? 'bg-emerald-400 text-emerald-950'
                      : 'bg-white/5 text-zinc-300 hover:bg-white/10'
                  }`}
                >
                  Full
                </button>
              </div>

              {mode === 'full' && (
                <div className="flex flex-col gap-3 text-sm text-zinc-200">
                  <label className="block font-medium" htmlFor="recipeName">
                    Recipe name
                  </label>
                  <input
                    className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-zinc-50 outline-none ring-0 placeholder:text-zinc-500 focus:border-emerald-400"
                    id="recipeName"
                    name="recipeName"
                    onChange={(event) => setRecipeName(event.target.value)}
                    placeholder="My K-12 IT director recipe"
                    value={recipeName}
                  />
                </div>
              )}

              <div className="flex flex-col gap-3 text-sm text-zinc-200">
                <label className="block font-medium" htmlFor="query">
                  Prospecting query
                </label>
                <input
                  className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-zinc-50 outline-none ring-0 placeholder:text-zinc-500 focus:border-emerald-400"
                  id="query"
                  name="query"
                  onChange={(event) => setQuery(event.target.value)}
                  placeholder="K-12 IT directors in Albuquerque"
                  value={query}
                />
              </div>
              <div className="flex flex-col gap-3 text-sm text-zinc-200">
                <label className="block font-medium" htmlFor="location">
                  Location / filter
                </label>
                <input
                  className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-zinc-50 outline-none ring-0 placeholder:text-zinc-500 focus:border-emerald-400"
                  id="location"
                  name="location"
                  onChange={(event) => setLocation(event.target.value)}
                  placeholder="New Mexico"
                  value={location}
                />
              </div>
              {error ? (
                <p className="rounded-2xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">
                  {error}
                </p>
              ) : null}
              <button
                className="inline-flex h-12 items-center justify-center rounded-full bg-emerald-400 px-6 text-sm font-semibold text-emerald-950 transition hover:bg-emerald-300 disabled:cursor-not-allowed disabled:bg-emerald-300/60"
                disabled={isLoading}
                type="submit"
              >
                {isLoading ? 'Searching…' : mode === 'scout' ? 'Run Scout search' : 'Run Full search'}
              </button>
            </form>
          </section>

          <aside className="rounded-3xl border border-emerald-400/20 bg-emerald-400/10 p-6">
            <p className="text-sm font-medium uppercase tracking-[0.18em] text-emerald-200">What's wired now</p>
            <ul className="mt-4 space-y-3 text-sm leading-6 text-zinc-200">
              <li>• Next.js proxy routes at <code>/api/scout</code> and <code>/api/full</code></li>
              <li>• FastAPI <code>POST /scout</code> and <code>POST /full</code></li>
              <li>• Recipe storage with <code>GET /recipes</code></li>
              <li>• Three-score lead cards with metrics</li>
            </ul>
          </aside>
        </div>

        {queryGuardrail && queryGuardrail.status !== 'clear' ? (
          <div
            className={`rounded-2xl border px-4 py-3 text-sm ${
              queryGuardrail.status === 'blocked'
                ? 'border-rose-500/30 bg-rose-500/10 text-rose-100'
                : 'border-amber-500/30 bg-amber-500/10 text-amber-100'
            }`}
          >
            <p className="font-semibold">
              {queryGuardrail.status === 'blocked' ? 'Lead-list guardrail' : 'Query could be tighter'}
            </p>
            <p className="mt-1 leading-6">{queryGuardrail.message}</p>
            {queryGuardrail.missing_criteria.length > 0 ? (
              <p className="mt-2 text-xs uppercase tracking-[0.18em] text-current/80">
                Missing: {queryGuardrail.missing_criteria.join(', ')}
              </p>
            ) : null}
            {queryGuardrail.suggestions.length > 0 ? (
              <ul className="mt-2 list-disc space-y-1 pl-5 text-sm leading-6">
                {queryGuardrail.suggestions.map((suggestion) => (
                  <li key={suggestion}>{suggestion}</li>
                ))}
              </ul>
            ) : null}
          </div>
        ) : null}

        {fullResult && (
          <div className="space-y-3 rounded-2xl border border-emerald-400/30 bg-emerald-400/10 px-4 py-3 text-sm text-emerald-200">
            <p>
              Full run saved. Recipe ID: {fullResult.recipe_id} · Run ID: {fullResult.run_id}
            </p>
            <div className="flex flex-wrap items-end gap-3">
              <label className="flex flex-col gap-1 text-xs uppercase tracking-[0.18em] text-emerald-100" htmlFor="operatorMinutes">
                Operator minutes
                <input
                  className="w-40 rounded-2xl border border-white/10 bg-zinc-950/70 px-3 py-2 text-sm text-zinc-50 outline-none placeholder:text-zinc-500"
                  id="operatorMinutes"
                  inputMode="decimal"
                  onChange={(event) => setOperatorMinutes(event.target.value)}
                  placeholder="18.5"
                  value={operatorMinutes}
                />
              </label>
              <button
                className="rounded-full bg-emerald-300 px-4 py-2 text-sm font-semibold text-emerald-950 transition hover:bg-emerald-200 disabled:cursor-not-allowed disabled:bg-emerald-200/60"
                disabled={isClosing}
                onClick={handleCloseRun}
                type="button"
              >
                {isClosing ? 'Closing…' : 'Close run'}
              </button>
              <a className="text-sm underline decoration-emerald-300/40 underline-offset-4" href="/recipes">
                Open recipe library
              </a>
            </div>
            {closeMessage ? <p className="text-xs text-emerald-100">{closeMessage}</p> : null}
          </div>
        )}

        <section className="rounded-3xl border border-white/10 bg-zinc-950/70 p-6">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="text-sm font-medium uppercase tracking-[0.18em] text-zinc-400">Results</p>
              <h2 className="mt-1 text-2xl font-semibold tracking-tight">Returned leads</h2>
            </div>
            {displayedResults ? (
              <div className="flex flex-col gap-2 sm:items-end">
                <label className="text-xs font-medium uppercase tracking-[0.18em] text-zinc-400" htmlFor="leadSortMode">
                  Sort leads
                </label>
                <select
                  className="rounded-2xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-zinc-50 outline-none focus:border-emerald-400"
                  id="leadSortMode"
                  name="leadSortMode"
                  onChange={(event) => setSortMode(event.target.value as LeadSortMode)}
                  value={sortMode}
                >
                  {LEAD_SORT_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
                <p className="text-sm text-zinc-400">
                  {displayedResults.leads.length} leads · {formatElapsedSeconds(displayedResults.metrics.elapsed_seconds)} · $
                  {displayedResults.metrics.estimated_cost_usd.toFixed(4)}
                </p>
              </div>
            ) : null}
          </div>

          {displayedResults ? (
            <div className="mt-6 grid gap-4">
              {displayedLeads.map((lead, index) => (
                <article
                  key={`${lead.name}-${lead.organization}-${index}`}
                  className="rounded-3xl border border-white/10 bg-white/5 p-5"
                >
                  <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                    <div className="space-y-2">
                      <p className="text-xs font-medium uppercase tracking-[0.18em] text-zinc-400">
                        Rank {index + 1} {lead.gate_passed ? '· gate passed' : '· review'}
                      </p>
                      <h3 className="text-xl font-semibold text-zinc-50">{lead.name}</h3>
                      <p className="text-sm text-zinc-300">
                        {lead.title} · {lead.organization}
                      </p>
                      <p className="text-sm text-emerald-300">{lead.email_status}: {lead.email || 'No email found'}</p>
                    </div>

                    <div className="grid gap-2 text-sm text-zinc-300 sm:grid-cols-3 lg:min-w-[20rem]">
                      <div className="rounded-2xl border border-white/10 bg-zinc-950/70 px-3 py-2">
                        <p className="text-xs uppercase tracking-[0.16em] text-zinc-500">Fit</p>
                        <p className="mt-1 font-semibold text-zinc-50">{formatScore(lead.fit_score)}</p>
                      </div>
                      <div className="rounded-2xl border border-white/10 bg-zinc-950/70 px-3 py-2">
                        <p className="text-xs uppercase tracking-[0.16em] text-zinc-500">Evidence</p>
                        <p className="mt-1 font-semibold text-zinc-50">{formatScore(lead.evidence_score)}</p>
                      </div>
                      <div className="rounded-2xl border border-white/10 bg-zinc-950/70 px-3 py-2">
                        <p className="text-xs uppercase tracking-[0.16em] text-zinc-500">Contact</p>
                        <p className="mt-1 font-semibold text-zinc-50">{formatScore(lead.contact_score)}</p>
                      </div>
                    </div>
                  </div>

                  <p className="mt-4 text-sm leading-6 text-zinc-300">{lead.explanation}</p>
                  <p className="mt-3 text-sm leading-6 text-zinc-400">{lead.why_target}</p>
                  <p className="mt-3 text-sm leading-6 text-zinc-200">{lead.icebreaker}</p>
                  <div className="mt-4 flex flex-wrap gap-2">
                    {(['usable', 'wrong_persona', 'bad_source', 'bad_contact', 'duplicate'] as const).map((label) => (
                      <button
                        key={label}
                        onClick={async () => {
                          if (!lead.id) {
                            alert('No lead ID available for feedback.');
                            return;
                          }
                          try {
                            await submitLeadFeedback(lead.id, label);
                            alert(`Feedback submitted: ${label}`);
                          } catch {
                            alert('Failed to submit feedback.');
                          }
                        }}
                        className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium text-zinc-300 transition hover:bg-emerald-400/20 hover:text-emerald-300"
                      >
                        {label.replace('_', ' ')}
                      </button>
                    ))}
                  </div>
                  <a
                    className="mt-4 inline-flex text-sm font-medium text-emerald-300 underline decoration-emerald-300/30 underline-offset-4"
                    href={lead.source_url}
                    rel="noreferrer"
                    target="_blank"
                  >
                    View source
                  </a>
                </article>
              ))}
            </div>
          ) : (
            <p className="mt-6 text-sm leading-6 text-zinc-400">
              Run a query to see ranked leads, score breakdowns, and metrics here.
            </p>
          )}
        </section>
      </section>
    </main>
  );
}
