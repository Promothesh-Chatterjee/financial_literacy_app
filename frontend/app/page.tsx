import Link from 'next/link'

export default function Home() {
  return (
    <div className="p-8 max-w-3xl mx-auto">
      <h1 className="text-4xl font-bold">FinLit Sim</h1>
      <p className="mt-4 text-slate-600">A virtual stock market learning simulator for young professionals learning investing with risk-free practice.</p>
      <div className="mt-8 grid gap-4 sm:grid-cols-3">
        <Link href="/login" className="rounded-lg border border-slate-200 p-6 text-center hover:bg-slate-50">
          <h2 className="text-xl font-semibold">Log in</h2>
          <p className="mt-2 text-slate-500">Access your portfolio and start trading.</p>
        </Link>
        <Link href="/signup" className="rounded-lg border border-slate-200 p-6 text-center hover:bg-slate-50">
          <h2 className="text-xl font-semibold">Sign up</h2>
          <p className="mt-2 text-slate-500">Create your account and begin onboarding.</p>
        </Link>
        <Link href="/dashboard" className="rounded-lg border border-slate-200 p-6 text-center hover:bg-slate-50">
          <h2 className="text-xl font-semibold">Dashboard</h2>
          <p className="mt-2 text-slate-500">View your net worth, holdings and place simulated trades.</p>
        </Link>
      </div>
    </div>
  )
}
