import Link from 'next/link';

export default function Home() {
  return (
    <main className="min-h-screen bg-zinc-950 px-6 py-10 text-zinc-50">
      <section className="mx-auto flex w-full max-w-5xl flex-col gap-8 rounded-[2rem] border border-white/10 bg-white/5 p-8 shadow-2xl shadow-black/20 backdrop-blur sm:p-10">
        <div className="flex flex-col gap-3">
          <p className="text-sm font-medium uppercase tracking-[0.22em] text-emerald-300">
            White Rabbit
          </p>
          <h1 className="max-w-2xl text-4xl font-semibold tracking-tight sm:text-5xl">
            Scout workspace is gated and ready for the next query slice.
          </h1>
          <p className="max-w-2xl text-base leading-7 text-zinc-300 sm:text-lg">
            Shared-password auth is live. Use the login page to reach the protected workspace,
            then move into the Scout page or the recipe library.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <article className="rounded-3xl border border-white/10 bg-zinc-950/70 p-6">
            <p className="text-sm font-medium uppercase tracking-[0.18em] text-zinc-400">Current state</p>
            <ul className="mt-4 space-y-3 text-sm leading-6 text-zinc-200">
              <li>• Login page posts to the shared auth endpoint.</li>
              <li>• Middleware protects the app and API routes.</li>
              <li>• Logout clears the session cookie.</li>
            </ul>
          </article>

          <article className="rounded-3xl border border-emerald-400/20 bg-emerald-400/10 p-6">
            <p className="text-sm font-medium uppercase tracking-[0.18em] text-emerald-200">Next steps</p>
            <p className="mt-4 text-sm leading-6 text-zinc-200">
              The next missing slice is the Scout query form and API proxy. For now, the protected
              shell gives Thomas a place to land after login.
            </p>
          </article>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row">
          <Link
            className="inline-flex h-12 items-center justify-center rounded-full bg-emerald-400 px-6 text-sm font-semibold text-emerald-950 transition hover:bg-emerald-300"
            href="/scout"
          >
            Open Scout workspace
          </Link>
          <Link
            className="inline-flex h-12 items-center justify-center rounded-full border border-white/15 px-6 text-sm font-semibold text-zinc-50 transition hover:bg-white/10"
            href="/recipes"
          >
            Open recipe library
          </Link>
          <Link
            className="inline-flex h-12 items-center justify-center rounded-full border border-white/15 px-6 text-sm font-semibold text-zinc-50 transition hover:bg-white/10"
            href="/login?next=/scout"
          >
            Go to login
          </Link>
          <a
            className="inline-flex h-12 items-center justify-center rounded-full border border-white/15 px-6 text-sm font-semibold text-zinc-50 transition hover:bg-white/10"
            href="/api/logout"
          >
            Sign out
          </a>
        </div>
      </section>
    </main>
  );
}
