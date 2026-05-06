import Link from 'next/link';

export default function ScoutPage() {
  return (
    <main className="min-h-screen bg-zinc-950 px-6 py-10 text-zinc-50">
      <section className="mx-auto flex w-full max-w-5xl flex-col gap-8 rounded-[2rem] border border-white/10 bg-white/5 p-8 shadow-2xl shadow-black/20 backdrop-blur sm:p-10">
        <div className="space-y-3">
          <p className="text-sm font-medium uppercase tracking-[0.22em] text-emerald-300">Scout</p>
          <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">Search workspace</h1>
          <p className="max-w-3xl text-base leading-7 text-zinc-300 sm:text-lg">
            The protected workspace is live. The next slice will connect this screen to the query
            API and return ranked leads.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <section className="rounded-3xl border border-white/10 bg-zinc-950/70 p-6 md:col-span-2">
            <p className="text-sm font-medium uppercase tracking-[0.18em] text-zinc-400">Start a query</p>
            <form className="mt-4 grid gap-5" action="#" method="post">
              <div className="flex flex-col gap-3 text-sm text-zinc-200">
                <label className="block font-medium" htmlFor="query">
                  What are you looking for?
                </label>
                <input
                  className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-zinc-50 outline-none ring-0 placeholder:text-zinc-500 focus:border-emerald-400"
                  defaultValue="K-12 IT directors in Albuquerque"
                  id="query"
                  name="query"
                />
              </div>
              <div className="flex flex-col gap-3 text-sm text-zinc-200">
                <label className="block font-medium" htmlFor="location">
                  Where should we look?
                </label>
                <input
                  className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-zinc-50 outline-none ring-0 placeholder:text-zinc-500 focus:border-emerald-400"
                  defaultValue="New Mexico"
                  id="location"
                  name="location"
                />
              </div>
              <button
                className="inline-flex h-12 items-center justify-center rounded-full bg-emerald-400 px-6 text-sm font-semibold text-emerald-950 transition hover:bg-emerald-300 disabled:cursor-not-allowed disabled:bg-emerald-300/60"
                disabled
                type="submit"
              >
                Search coming next
              </button>
            </form>
          </section>

          <aside className="rounded-3xl border border-emerald-400/20 bg-emerald-400/10 p-6">
            <p className="text-sm font-medium uppercase tracking-[0.18em] text-emerald-200">What’s next</p>
            <ul className="mt-4 space-y-3 text-sm leading-6 text-zinc-200">
              <li>• API proxy route</li>
              <li>• Live lead scoring</li>
              <li>• Result rendering</li>
            </ul>
          </aside>
        </div>

        <div>
          <Link
            className="inline-flex h-12 items-center justify-center rounded-full border border-white/15 px-6 text-sm font-semibold text-zinc-50 transition hover:bg-white/10"
            href="/"
          >
            Back to home
          </Link>
        </div>
      </section>
    </main>
  );
}
