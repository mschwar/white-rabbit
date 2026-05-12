import Link from 'next/link';
import { BrandWordmark } from '@/components/brand-identity';

type LoginPageSearchParams = {
  error?: string;
  next?: string;
};

type LoginPageProps = {
  searchParams?: LoginPageSearchParams | Promise<LoginPageSearchParams>;
};

export default async function LoginPage({ searchParams }: LoginPageProps) {
  const resolvedSearchParams = await Promise.resolve(searchParams);
  const nextPath = resolvedSearchParams?.next?.startsWith('/') ? resolvedSearchParams.next : '/';
  const hasError = resolvedSearchParams?.error === '1';

  return (
    <main className="flex min-h-screen items-center justify-center bg-[#050916] px-6 py-12 text-zinc-50">
      <section className="w-full max-w-md rounded-lg border border-white/10 bg-white/[0.04] p-8 shadow-[0_24px_70px_rgba(0,0,0,0.32)] backdrop-blur">
        <div className="space-y-3">
          <BrandWordmark caption="Operator workspace" inverted size="login" />
          <h1 className="text-3xl font-semibold tracking-tight">Shared-password access</h1>
          <p className="text-sm leading-6 text-zinc-300">
            Enter the shared workspace password to continue.
          </p>
        </div>

        {hasError ? (
          <p className="mt-6 rounded-2xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">
            That password did not work. Try again.
          </p>
        ) : null}

        <form className="mt-6 space-y-4" action="/api/login" method="post">
          <input type="hidden" name="next" value={nextPath} />
          <div className="flex flex-col gap-3 text-sm font-medium text-zinc-200">
            <label className="block" htmlFor="password">
              Password
            </label>
            <input
              autoComplete="current-password"
              autoFocus
              className="w-full rounded-md border border-white/10 bg-[#0a1226] px-4 py-3 text-base text-zinc-50 outline-none ring-0 placeholder:text-zinc-500 focus:border-[#2d7bff] focus:ring-2 focus:ring-[#2d7bff]/25"
              id="password"
              name="password"
              placeholder="Enter shared password"
              type="password"
            />
          </div>

          <button
            className="flex w-full items-center justify-center rounded-md bg-[#2d7bff] px-4 py-3 text-sm font-semibold text-white transition hover:bg-[#1f65d8]"
            type="submit"
          >
            Unlock workspace
          </button>
        </form>

        <p className="mt-6 text-xs leading-5 text-zinc-400">
          Use the live workspace after signing in.{' '}
          <Link className="underline decoration-zinc-500 underline-offset-4" href="/login?next=/scout">
            Try the Scout workspace after login
          </Link>.
        </p>
      </section>
    </main>
  );
}
