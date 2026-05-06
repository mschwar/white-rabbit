'use client';

import { useEffect, useState } from 'react';
import { fetchRecipes, fetchRecipeRuns, type RecipeItem, type RecipeRunItem } from '@/lib/scout';

export default function RecipesLibrary() {
  const [recipes, setRecipes] = useState<RecipeItem[]>([]);
  const [selectedRecipeId, setSelectedRecipeId] = useState<string | null>(null);
  const [runs, setRuns] = useState<RecipeRunItem[]>([]);
  const [isLoadingRecipes, setIsLoadingRecipes] = useState(true);
  const [isLoadingRuns, setIsLoadingRuns] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

  return (
    <main className="min-h-screen bg-zinc-950 px-6 py-10 text-zinc-50">
      <section className="mx-auto flex w-full max-w-6xl flex-col gap-8 rounded-[2rem] border border-white/10 bg-white/5 p-8 shadow-2xl shadow-black/20 backdrop-blur sm:p-10">
        <div className="space-y-3">
          <p className="text-sm font-medium uppercase tracking-[0.22em] text-emerald-300">Recipes</p>
          <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">Recipe library</h1>
          <p className="max-w-3xl text-base leading-7 text-zinc-300 sm:text-lg">
            Saved Full runs show up here as reusable recipes. Select one to inspect its run history.
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
              <h2 className="text-xl font-semibold tracking-tight text-zinc-50">Runs</h2>
              {isLoadingRuns ? <span className="text-sm text-emerald-200">Loading…</span> : null}
            </div>

            {selectedRecipeId ? (
              <div className="mt-4 space-y-3">
                {runs.length === 0 && !isLoadingRuns ? (
                  <p className="text-sm leading-6 text-zinc-200">No runs recorded for this recipe yet.</p>
                ) : null}

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
            ) : (
              <p className="mt-4 text-sm leading-6 text-zinc-200">Select a recipe to see its runs.</p>
            )}
          </aside>
        </div>
      </section>
    </main>
  );
}
