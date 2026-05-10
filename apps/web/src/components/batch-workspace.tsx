'use client';

import { FormEvent, useEffect, useRef, useState } from 'react';
import {
  type BatchQueryItem,
  type BatchJobItem,
  buildBatchPayload,
  parseBatchCsv,
  submitBatch,
  fetchBatchJobs,
} from '@/lib/batch';

export default function BatchWorkspace() {
  const [name, setName] = useState('');
  const [queries, setQueries] = useState<BatchQueryItem[]>([
    { query: 'Healthcare IT directors in Phoenix', filters: { location: 'Arizona' } },
    { query: 'Financial services CISOs in New York', filters: { location: 'New York' } },
  ]);
  const [capQueries, setCapQueries] = useState(10);
  const [capMaxLeads, setCapMaxLeads] = useState(1000);
  const [capMaxSpend, setCapMaxSpend] = useState(10.0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<BatchJobItem | null>(null);
  const [jobs, setJobs] = useState<BatchJobItem[]>([]);
  const [isLoadingJobs, setIsLoadingJobs] = useState(true);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    let active = true;
    fetchBatchJobs()
      .then((items) => {
        if (!active) return;
        setJobs(items);
      })
      .catch(() => {
        // non-fatal: history is optional
      })
      .finally(() => {
        if (active) setIsLoadingJobs(false);
      });
    return () => {
      active = false;
    };
  }, []);

  function handleAddRow() {
    setQueries((prev) => [...prev, { query: '' }]);
  }

  function handleRemoveRow(index: number) {
    setQueries((prev) => prev.filter((_, i) => i !== index));
  }

  function handleChangeQuery(index: number, value: string) {
    setQueries((prev) => {
      const next = [...prev];
      next[index] = { ...next[index], query: value };
      return next;
    });
  }

  function handleChangeLocation(index: number, value: string) {
    setQueries((prev) => {
      const next = [...prev];
      next[index] = { ...next[index], filters: value ? { location: value } : undefined };
      return next;
    });
  }

  function handleFileUpload(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      const text = String(reader.result ?? '');
      try {
        const parsed = parseBatchCsv(text);
        if (parsed.length > 0) {
          setQueries(parsed);
          setError(null);
        } else {
          setError('CSV parsed but no valid query rows found. Expected columns: query, location (optional), recipe_name (optional).');
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to parse CSV.');
      }
    };
    reader.readAsText(file);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const validQueries = queries.filter((q) => q.query.trim());
    if (validQueries.length === 0) {
      setError('Add at least one query.');
      return;
    }
    if (!name.trim()) {
      setError('Enter a batch name.');
      return;
    }

    setIsSubmitting(true);
    setError(null);
    setResult(null);

    try {
      const payload = buildBatchPayload(name.trim(), validQueries, {
        cap_queries: capQueries,
        cap_max_leads: capMaxLeads,
        cap_max_spend_usd: capMaxSpend,
      });
      const job = await submitBatch(payload);
      setResult(job);
      setJobs((prev) => [job, ...prev]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Batch submission failed.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="min-h-screen bg-zinc-950 px-6 py-10 text-zinc-50">
      <section className="mx-auto flex w-full max-w-6xl flex-col gap-8 rounded-[2rem] border border-white/10 bg-white/5 p-8 shadow-2xl shadow-black/20 backdrop-blur sm:p-10">
        <div className="space-y-3">
          <p className="text-sm font-medium uppercase tracking-[0.22em] text-emerald-300">Batch</p>
          <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">Bulk run workspace</h1>
          <p className="max-w-3xl text-base leading-7 text-zinc-300 sm:text-lg">
            Run multiple recipes in sequence with caps. Each query becomes a stored Full recipe.
          </p>
        </div>

        <div className="rounded-3xl border border-amber-400/30 bg-amber-500/10 px-5 py-4 text-amber-100">
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-amber-200">
            Internal evaluation only
          </p>
          <p className="mt-2 max-w-3xl text-sm leading-6">
            This route stays out of the primary operator flow while the launch gate is red. Use
            it only for Matt-run internal evaluation, not for Thomas or Lee daily prospecting.
          </p>
        </div>

        {error ? (
          <div className="rounded-2xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">
            {error}
          </div>
        ) : null}

        <div className="grid gap-6 lg:grid-cols-[1fr_0.9fr]">
          <section className="rounded-3xl border border-white/10 bg-zinc-950/70 p-6">
            <p className="text-sm font-medium uppercase tracking-[0.18em] text-zinc-400">Configure batch</p>
            <form className="mt-4 grid gap-5" onSubmit={handleSubmit}>
              <div className="flex flex-col gap-3 text-sm text-zinc-200">
                <label className="block font-medium" htmlFor="batchName">
                  Batch name
                </label>
                <input
                  className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-zinc-50 outline-none ring-0 placeholder:text-zinc-500 focus:border-emerald-400"
                  id="batchName"
                  name="batchName"
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Monday prospecting sweep"
                  value={name}
                />
              </div>

              <div className="grid gap-4 sm:grid-cols-3">
                <div className="flex flex-col gap-2 text-sm text-zinc-200">
                  <label className="font-medium" htmlFor="capQueries">
                    Max queries
                  </label>
                  <input
                    className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-zinc-50 outline-none focus:border-emerald-400"
                    id="capQueries"
                    inputMode="numeric"
                    min={1}
                    name="capQueries"
                    onChange={(e) => setCapQueries(Number(e.target.value))}
                    type="number"
                    value={capQueries}
                  />
                </div>
                <div className="flex flex-col gap-2 text-sm text-zinc-200">
                  <label className="font-medium" htmlFor="capMaxLeads">
                    Max leads
                  </label>
                  <input
                    className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-zinc-50 outline-none focus:border-emerald-400"
                    id="capMaxLeads"
                    inputMode="numeric"
                    min={1}
                    name="capMaxLeads"
                    onChange={(e) => setCapMaxLeads(Number(e.target.value))}
                    type="number"
                    value={capMaxLeads}
                  />
                </div>
                <div className="flex flex-col gap-2 text-sm text-zinc-200">
                  <label className="font-medium" htmlFor="capMaxSpend">
                    Max spend (USD)
                  </label>
                  <input
                    className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-zinc-50 outline-none focus:border-emerald-400"
                    id="capMaxSpend"
                    inputMode="decimal"
                    min={0.1}
                    name="capMaxSpend"
                    onChange={(e) => setCapMaxSpend(Number(e.target.value))}
                    step={0.1}
                    type="number"
                    value={capMaxSpend}
                  />
                </div>
              </div>

              <div className="flex flex-col gap-3">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium text-zinc-200">Queries ({queries.length})</p>
                  <div className="flex gap-2">
                    <button
                      className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium text-zinc-300 transition hover:bg-white/10"
                      onClick={handleAddRow}
                      type="button"
                    >
                      + Add row
                    </button>
                    <label className="cursor-pointer rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium text-zinc-300 transition hover:bg-white/10">
                      Upload CSV
                      <input
                        accept=".csv"
                        className="hidden"
                        onChange={handleFileUpload}
                        ref={fileInputRef}
                        type="file"
                      />
                    </label>
                  </div>
                </div>

                <div className="grid gap-3">
                  {queries.map((item, index) => (
                    <div key={index} className="flex gap-2">
                      <input
                        className="flex-1 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-zinc-50 outline-none placeholder:text-zinc-500 focus:border-emerald-400"
                        onChange={(e) => handleChangeQuery(index, e.target.value)}
                        placeholder="Query"
                        value={item.query}
                      />
                      <input
                        className="w-40 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-zinc-50 outline-none placeholder:text-zinc-500 focus:border-emerald-400"
                        onChange={(e) => handleChangeLocation(index, e.target.value)}
                        placeholder="Location"
                        value={item.filters?.location ?? ''}
                      />
                      <button
                        className="rounded-full border border-white/10 bg-white/5 px-3 py-2 text-xs font-medium text-zinc-300 transition hover:bg-rose-500/20 hover:text-rose-300"
                        onClick={() => handleRemoveRow(index)}
                        type="button"
                      >
                        Remove
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              <button
                className="inline-flex h-12 items-center justify-center rounded-full bg-emerald-400 px-6 text-sm font-semibold text-emerald-950 transition hover:bg-emerald-300 disabled:cursor-not-allowed disabled:bg-emerald-300/60"
                disabled={isSubmitting}
                type="submit"
              >
                {isSubmitting ? 'Running batch…' : 'Run batch'}
              </button>
            </form>
          </section>

          <aside className="rounded-3xl border border-emerald-400/20 bg-emerald-400/10 p-6">
            <p className="text-sm font-medium uppercase tracking-[0.18em] text-emerald-200">What&apos;s wired now</p>
            <ul className="mt-4 space-y-3 text-sm leading-6 text-zinc-200">
              <li>• CSV upload with query + location columns</li>
              <li>• Caps: max queries, max leads, max spend</li>
              <li>• Each query creates a stored Full recipe</li>
              <li>• Sequential execution with per-run error handling</li>
            </ul>
          </aside>
        </div>

        {result && (
          <section className="rounded-3xl border border-emerald-400/30 bg-emerald-400/10 p-6">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-sm font-medium uppercase tracking-[0.18em] text-emerald-300">Batch result</p>
                <h2 className="mt-1 text-xl font-semibold text-zinc-50">{result.name}</h2>
              </div>
              <span
                className={`rounded-full border px-3 py-1 text-xs font-medium ${
                  result.status === 'completed'
                    ? 'border-emerald-400/30 bg-emerald-400/20 text-emerald-200'
                    : 'border-amber-400/30 bg-amber-400/20 text-amber-200'
                }`}
              >
                {result.status}
              </span>
            </div>
            <div className="mt-4 grid gap-3 sm:grid-cols-3">
              <div className="rounded-2xl border border-white/10 bg-zinc-950/70 p-4">
                <p className="text-xs uppercase tracking-[0.18em] text-zinc-400">Total leads</p>
                <p className="mt-2 text-2xl font-semibold text-zinc-50">{result.total_leads}</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-zinc-950/70 p-4">
                <p className="text-xs uppercase tracking-[0.18em] text-zinc-400">Total cost</p>
                <p className="mt-2 text-2xl font-semibold text-zinc-50">
                  ${result.total_cost_usd.toFixed(4)}
                </p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-zinc-950/70 p-4">
                <p className="text-xs uppercase tracking-[0.18em] text-zinc-400">Runs</p>
                <p className="mt-2 text-2xl font-semibold text-zinc-50">{result.runs.length}</p>
              </div>
            </div>
            <div className="mt-4 grid gap-3">
              {result.runs.map((run) => (
                <div
                  key={run.id}
                  className={`rounded-2xl border p-4 ${
                    run.status === 'completed'
                      ? 'border-white/10 bg-zinc-950/70'
                      : 'border-rose-500/20 bg-rose-500/10'
                  }`}
                >
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-sm font-medium text-zinc-50">{run.query}</p>
                    <span className="rounded-full border border-white/10 px-3 py-1 text-xs text-zinc-300">
                      {run.status}
                    </span>
                  </div>
                  <p className="mt-1 text-sm text-zinc-300">
                    {run.lead_count} leads · ${run.cost_usd.toFixed(4)}
                  </p>
                  {run.error_message ? (
                    <p className="mt-1 text-sm text-rose-300">{run.error_message}</p>
                  ) : null}
                </div>
              ))}
            </div>
          </section>
        )}

        <section className="rounded-3xl border border-white/10 bg-zinc-950/70 p-6">
          <div className="flex items-center justify-between gap-3">
            <h2 className="text-xl font-semibold tracking-tight">Batch history</h2>
            {isLoadingJobs ? <span className="text-sm text-zinc-400">Loading…</span> : null}
          </div>
          {jobs.length === 0 && !isLoadingJobs ? (
            <p className="mt-4 text-sm leading-6 text-zinc-400">No batch jobs yet.</p>
          ) : null}
          <div className="mt-4 grid gap-4">
            {jobs.map((job) => (
              <div
                key={job.id}
                className="rounded-2xl border border-white/10 bg-white/5 p-4"
              >
                <div className="flex items-center justify-between gap-3">
                  <h3 className="text-lg font-semibold text-zinc-50">{job.name}</h3>
                  <span
                    className={`rounded-full border px-3 py-1 text-xs font-medium ${
                      job.status === 'completed'
                        ? 'border-emerald-400/30 bg-emerald-400/20 text-emerald-200'
                        : 'border-amber-400/30 bg-amber-400/20 text-amber-200'
                    }`}
                  >
                    {job.status}
                  </span>
                </div>
                <p className="mt-1 text-sm text-zinc-300">
                  {job.total_leads} leads · ${job.total_cost_usd.toFixed(4)} · {job.runs.length} runs
                </p>
                <p className="mt-1 text-xs text-zinc-500">
                  Created {new Date(job.created_at).toLocaleString()}
                </p>
              </div>
            ))}
          </div>
        </section>
      </section>
    </main>
  );
}
