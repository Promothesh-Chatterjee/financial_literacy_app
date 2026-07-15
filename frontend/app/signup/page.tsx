"use client"
import { useState } from 'react'
import { useRouter } from 'next/navigation'

export default function Signup() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const router = useRouter()

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
      credentials: 'include',
    })
    if (res.ok) {
      router.push('/onboarding')
    } else {
      const data = await res.json()
      setError(data.detail || 'Signup failed')
    }
  }

  return (
    <div className="max-w-md mx-auto p-6">
      <h2 className="text-2xl font-bold mb-4">Sign up</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input className="w-full p-2 border rounded" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} />
        <input className="w-full p-2 border rounded" placeholder="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} />
        {error && <div className="text-red-600">{error}</div>}
        <button className="px-4 py-2 bg-indigo-600 text-white rounded">Create account</button>
      </form>
    </div>
  )
}
