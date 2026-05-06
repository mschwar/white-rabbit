'use client';

import { FormEvent, useState } from 'react';
import {
  buildScoutPayload,
  DEFAULT_SCOUT_LOCATION,
  DEFAULT_SCOUT_QUERY,
  formatScore,
  type ScoutResponse,
} from '@/lib/scout';

function formatElapsedSeconds(seconds: number): string {
  return `${seconds.toFixed(2)}s`;
}

export default function ScoutWorkspace() {
  const [query, setQuery] = useState(DEFAULT_SCOUT_QUERY);
  const [location, setLocation] = useState(DEFAULT_SCOUT_LOCATION);
  const [results, setResults] = useState<ScoutResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const payload = buildScoutPayload(query, location);
    if (!payload) {
      setError('Enter a query before searching.');
      setResults(null);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/scout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        let message = `Scout search failed (${response.status}).`;
        try {
          const body = (await response.json()) as { error?: string; detail?: string };
          message = body.error ?? body.detail ?? message;
        } catch {
          const text = await response.text();
          if (text) {
            message = text;
          }
        }
        throw new Error(message);
      }

      const data = (await response.json()) as ScoutResponse;
      setResults(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Scout search failed.';
      setError(message);
      setResults(null);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-zinc-950 px-6 py-10 text-zinc-50">
      <section className="mx-auto flex w-full max-w-6xl flex-col gap-8 rounded-[2rem] border border-white/10 bg-white/5 p-8 shadow-2xl shadow-black/20 backdrop-blur sm:p-10">
        <div className="space-y-3">
          <p className="text-sm font-medium uppercase tracking-[0.22em] text-emerald-300">Scout</p>
          <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">Query workspace</h1>
          <p className="max-w-3xl text-base leading-7 text-zinc-300 sm:text-lg">
            Thomas can enter a prospecting query, send it through the Next.js proxy, and review the
            returned leads without touching the API directly.
          </p>
        </div>

        <div className="grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
          <section className="rounded-3xl border border-white/10 bg-zinc-950/70 p-6">
            <p className="text-sm font-medium uppercase tracking-[0.18em] text-zinc-400">Start a query</p>
            <form className="mt-4 grid gap-5" onSubmit={handleSubmit}>
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
                {isLoading ? 'Searching…' : 'Run Scout search'}
              </button>
            </form>
          </section>

          <aside className="rounded-3xl border border-emerald-400/20 bg-emerald-400/10 p-6">
            <p className="text-sm font-medium uppercase tracking-[0.18em] text-emerald-200">What’s wired now</p>
            <ul className="mt-4 space-y-3 text-sm leading-6 text-zinc-200">
              <li>• Next.js proxy route at <code>/api/scout</code></li>
              <li>• FastAPI <code>POST /scout</code> contract</li>
              <li>• Three-score lead cards with metrics</li>
            </ul>
          </aside>
        </div>

        <section className="rounded-3xl border border-white/10 bg-zinc-950/70 p-6">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="text-sm font-medium uppercase tracking-[0.18em] text-zinc-400">Results</p>
              <h2 className="mt-1 text-2xl font-semibold tracking-tight">Returned leads</h2>
            </div>
            {results ? (
              <p className="text-sm text-zinc-400">
                {results.leads.length} leads · {formatElapsedSeconds(results.metrics.elapsed_seconds)} · $
                {results.metrics.estimated_cost_usd.toFixed(4)}
              </p>
            ) : null}
          </div>

          {results ? (
            <div className="mt-6 grid gap-4">
              {results.leads.map((lead, index) => (
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
