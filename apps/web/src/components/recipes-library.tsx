'use client';

import { useEffect, useMemo, useState } from 'react';
import {
  fetchRecipes,
  fetchRecipeRuns,
  fetchRecipeScoreboard,
  type RecipeItem,
  type RecipeRunItem,
  type RecipeScoreboardItem,
} from '@/lib/scout';

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
}

function formatMaybeNumber(value: number | null): string {
  return value == null ? 'n/a' : value.toFixed(2);
}

export default function RecipesLibrary() {
  const [recipes, setRecipes] = useState<RecipeItem[]>([]);
  const [selectedRecipeId, setSelectedRecipeId] = useState<string | null>(null);
  const [runs, setRuns] = useState<RecipeRunItem[]>([]);
  const [scoreboard, setScoreboard] = useState<RecipeScoreboardItem | null>(null);
  const [isLoadingRecipes, setIsLoadingRecipes] = useState(true);
  const [isLoadingRuns, setIsLoadingRuns] = useState(false);
  const [isLoadingScoreboard, setIsLoadingScoreboard] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectedRecipe = useMemo(
    () => recipes.find((recipe) => recipe.id === selectedRecipeId) ?? null,
    [recipes, selectedRecipeId],
  );

  useEffect(() => {
    let active = true;
    setIsLoadingRecipes(true);
    fetchRecipes()
      .then((items) => {
        if (!active) return;
        setRecipes(items);
        setError(null);
        if (items[0]) {
          setSelectedRecipeId(items[0].id);
        }
      })
      .catch((err) => {
        if (!active) return;
        setError(err instanceof Error ? err.message : 'Failed to load recipes.');
      })
      .finally(() => {
        if (active) setIsLoadingRecipes(false);
      });

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    if (!selectedRecipeId) {
      setRuns([]);
      return;
    }

    let active = true;
    setIsLoadingRuns(true);
    fetchRecipeRuns(selectedRecipeId)
      .then((items) => {
        if (!active) return;
        setRuns(items);
      })
      .catch((err) => {
        if (!active) return;
        setError(err instanceof Error ? err.message : 'Failed to load runs.');
      })
      .finally(() => {
        if (active) setIsLoadingRuns(false);
      });

    return () => {
      active = false;
    };
  }, [selectedRecipeId]);

  useEffect(() => {
    if (!selectedRecipeId) {
      setScoreboard(null);
      return;
    }

    let active = true;
    setIsLoadingScoreboard(true);
    fetchRecipeScoreboard(selectedRecipeId)
      .then((item) => {
        if (!active) return;
        setScoreboard(item);
      })
      .catch((err) => {
        if (!active) return;
        setError(err instanceof Error ? err.message : 'Failed to load scoreboard.');
      })
      .finally(() => {
        if (active) setIsLoadingScoreboard(false);
      });

    return () => {
      active = false;
    };
  }, [selectedRecipeId]);

  const feedbackLabels = [
    ['usable', 'Usable'],
    ['wrong_persona', 'Wrong persona'],
    ['bad_source', 'Bad source'],
    ['bad_contact', 'Bad contact'],
    ['duplicate', 'Duplicate'],
  ] as const;

  return (
    <main className="min-h-screen bg-zinc-950 px-6 py-10 text-zinc-50">
      <section className="mx-auto flex w-full max-w-6xl flex-col gap-8 rounded-[2rem] border border-white/10 bg-white/5 p-8 shadow-2xl shadow-black/20 backdrop-blur sm:p-10">
        <div className="space-y-3">
          <p className="text-sm font-medium uppercase tracking-[0.22em] text-emerald-300">Recipes</p>
          <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">Recipe library</h1>
          <p className="max-w-3xl text-base leading-7 text-zinc-300 sm:text-lg">
            Saved Full runs show up here as reusable recipes. Select one to inspect its run history and scoreboard.
          </p>
        </div>

        {error ? (
          <div className="rounded-2xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">
            {error}
          </div>
        ) : null}

        <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
          <section className="rounded-3xl border border-white/10 bg-zinc-950/70 p-6">
            <div className="flex items-center justify-between gap-3">
              <h2 className="text-xl font-semibold tracking-tight">Saved recipes</h2>
              {isLoadingRecipes ? <span className="text-sm text-zinc-400">Loading…</span> : null}
            </div>

            <div className="mt-4 grid gap-4">
              {recipes.length === 0 && !isLoadingRecipes ? (
                <p className="text-sm leading-6 text-zinc-400">No saved recipes yet. Run a Full search first.</p>
              ) : null}

              {recipes.map((recipe) => (
                <button
                  key={recipe.id}
                  className={`rounded-3xl border p-4 text-left transition ${
                    selectedRecipeId === recipe.id
                      ? 'border-emerald-400/40 bg-emerald-400/10'
                      : 'border-white/10 bg-white/5 hover:bg-white/10'
                  }`}
                  onClick={() => setSelectedRecipeId(recipe.id)}
                  type="button"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <h3 className="text-lg font-semibold text-zinc-50">{recipe.name}</h3>
                      <p className="mt-1 text-sm text-zinc-300">{recipe.query}</p>
                      <p className="mt-1 text-xs uppercase tracking-[0.18em] text-zinc-500">
                        Created {new Date(recipe.created_at).toLocaleString()}
                      </p>
                    </div>
                    <span className="rounded-full border border-white/10 px-3 py-1 text-xs text-zinc-300">
                      {recipe.filters?.location ? String(recipe.filters.location) : 'No location filter'}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </section>

          <aside className="rounded-3xl border border-emerald-400/20 bg-emerald-400/10 p-6">
            <div className="flex items-center justify-between gap-3">
              <h2 className="text-xl font-semibold tracking-tight text-zinc-50">Scoreboard</h2>
              {isLoadingScoreboard ? <span className="text-sm text-emerald-200">Loading…</span> : null}
            </div>

            {selectedRecipe ? (
              <div className="mt-4 space-y-4">
                <div className="rounded-2xl border border-white/10 bg-zinc-950/70 p-4">
                  <p className="text-xs uppercase tracking-[0.18em] text-zinc-400">Selected recipe</p>
                  <h3 className="mt-1 text-lg font-semibold text-zinc-50">{selectedRecipe.name}</h3>
                  <p className="mt-1 text-sm text-zinc-300">{selectedRecipe.query}</p>
                </div>

                {scoreboard ? (
                  <div className="grid gap-3 sm:grid-cols-2">
                    <div className="rounded-2xl border border-white/10 bg-zinc-950/70 p-4">
                      <p className="text-xs uppercase tracking-[0.18em] text-zinc-400">Leads returned</p>
                      <p className="mt-2 text-2xl font-semibold text-zinc-50">{scoreboard.total_leads_returned}</p>
                    </div>
                    <div className="rounded-2xl border border-white/10 bg-zinc-950/70 p-4">
                      <p className="text-xs uppercase tracking-[0.18em] text-zinc-400">Usable leads</p>
                      <p className="mt-2 text-2xl font-semibold text-zinc-50">{scoreboard.usable_lead_count}</p>
                    </div>
                    <div className="rounded-2xl border border-white/10 bg-zinc-950/70 p-4">
                      <p className="text-xs uppercase tracking-[0.18em] text-zinc-400">API cost spent</p>
                      <p className="mt-2 text-2xl font-semibold text-zinc-50">
                        {formatCurrency(scoreboard.total_api_cost_usd)}
                      </p>
                    </div>
                    <div className="rounded-2xl border border-white/10 bg-zinc-950/70 p-4">
                      <p className="text-xs uppercase tracking-[0.18em] text-zinc-400">Operator minutes</p>
                      <p className="mt-2 text-2xl font-semibold text-zinc-50">
                        {scoreboard.total_operator_minutes.toFixed(1)}
                      </p>
                    </div>
                    <div className="rounded-2xl border border-white/10 bg-zinc-950/70 p-4">
                      <p className="text-xs uppercase tracking-[0.18em] text-zinc-400">Minutes / usable lead</p>
                      <p className="mt-2 text-2xl font-semibold text-zinc-50">
                        {formatMaybeNumber(scoreboard.minutes_per_usable_lead)}
                      </p>
                    </div>
                    <div className="rounded-2xl border border-white/10 bg-zinc-950/70 p-4">
                      <p className="text-xs uppercase tracking-[0.18em] text-zinc-400">API cost / usable lead</p>
                      <p className="mt-2 text-2xl font-semibold text-zinc-50">
                        {scoreboard.api_cost_per_usable_lead == null
                          ? 'n/a'
                          : formatCurrency(scoreboard.api_cost_per_usable_lead)}
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="rounded-2xl border border-white/10 bg-zinc-950/70 p-4 text-sm text-zinc-300">
                    {isLoadingScoreboard ? 'Loading scoreboard…' : 'No scoreboard data yet.'}
                  </div>
                )}

                {scoreboard ? (
                  <div className="rounded-2xl border border-white/10 bg-zinc-950/70 p-4">
                    <p className="text-xs uppercase tracking-[0.18em] text-zinc-400">Feedback breakdown</p>
                    <div className="mt-3 flex flex-wrap gap-2 text-sm text-zinc-200">
                      {feedbackLabels.map(([key, label]) => (
                        <span key={key} className="rounded-full border border-white/10 px-3 py-1">
                          {label}: {scoreboard.feedback_counts[key] ?? 0}
                        </span>
                      ))}
                    </div>
                  </div>
                ) : null}

                <div className="space-y-3">
                  <div className="flex items-center justify-between gap-3">
                    <h3 className="text-lg font-semibold tracking-tight text-zinc-50">Runs</h3>
                    {isLoadingRuns ? <span className="text-sm text-emerald-200">Loading…</span> : null}
                  </div>

                  {runs.length === 0 && !isLoadingRuns ? (
                    <p className="text-sm leading-6 text-zinc-200">No runs recorded for this recipe yet.</p>
                  ) : null}

                  <div className="space-y-3">
                    {runs.map((run) => (
                      <article key={run.id} className="rounded-2xl border border-white/10 bg-zinc-950/70 p-4">
                        <p className="text-xs uppercase tracking-[0.18em] text-zinc-400">{run.mode}</p>
                        <p className="mt-1 text-sm text-zinc-100">{run.lead_count} leads</p>
                        <p className="mt-1 text-sm text-zinc-300">
                          Started {new Date(run.started_at).toLocaleString()}
                        </p>
                        <p className="mt-1 text-sm text-zinc-300">
                          Operator minutes: {run.operator_minutes ?? 'not closed yet'}
                        </p>
                      </article>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <p className="mt-4 text-sm leading-6 text-zinc-200">Select a recipe to see its scoreboard and runs.</p>
            )}
          </aside>
        </div>
      </section>
    </main>
  );
}
