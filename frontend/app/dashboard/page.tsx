"use client"

import { useEffect, useState } from 'react'

export default function Dashboard() {
  const [summary, setSummary] = useState<any>(null)
  const [ticker, setTicker] = useState('RELIANCE.NS')
  const [quantity, setQuantity] = useState('1')
  const [action, setAction] = useState<'BUY' | 'SELL'>('BUY')
  const [message, setMessage] = useState('')

  useEffect(() => {
    fetchPortfolio()
  }, [])

  async function fetchPortfolio() {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/portfolio/summary`, {
      credentials: 'include',
    })
    if (res.ok) {
      setSummary(await res.json())
    }
  }

  function getCookie(name: string) {
    return document.cookie.split('; ').find(row => row.startsWith(name + '='))?.split('=')[1]
  }

  async function placeOrder() {
    setMessage('')
    const csrf = getCookie('csrf_token')
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/trade/order`, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        ...(csrf ? { 'x-csrf-token': csrf } : {}),
      },
      body: JSON.stringify({ ticker, action, quantity: Number(quantity) }),
    })
    if (res.ok) {
      const data = await res.json()
      setMessage(`Order executed: ${data.quantity} ${data.ticker} ${data.action} at ₹${data.price}`)
      fetchPortfolio()
    } else {
      const data = await res.json()
      setMessage(`Order failed: ${data.detail || 'Unknown error'}`)
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="rounded-xl bg-white p-6 shadow-sm border">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="mt-2 text-slate-600">Track your portfolio and place risk-free trades with virtual capital.</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
        <div className="space-y-4 rounded-xl bg-white p-6 shadow-sm border">
          <h2 className="text-xl font-semibold">Portfolio summary</h2>
          {summary ? (
            <div className="space-y-3">
              <div>Cash balance: <strong>₹{summary.cash.toLocaleString('en-IN')}</strong></div>
              <div>Holdings value: <strong>₹{summary.holdings_value.toLocaleString('en-IN')}</strong></div>
              <div>Net worth: <strong>₹{summary.net_worth.toLocaleString('en-IN')}</strong></div>
              <div>Today's P&L: <strong className={summary.todays_pnl >= 0 ? 'text-green-600' : 'text-red-600'}>₹{summary.todays_pnl.toLocaleString('en-IN')}</strong></div>
              <div>
                <h3 className="font-semibold">Holdings</h3>
                <div className="mt-2 space-y-2">
                  {summary.holdings.length ? summary.holdings.map((item: any) => (
                    <div key={item.ticker} className="rounded-lg border p-3 bg-slate-50">
                      <div className="font-semibold">{item.ticker}</div>
                      <div className="text-sm text-slate-600">Qty: {item.quantity} • Current: ₹{item.current_price} • Value: ₹{item.value.toLocaleString('en-IN')}</div>
                    </div>
                  )) : <div className="text-slate-500">No holdings yet.</div>}
                </div>
              </div>
            </div>
          ) : (
            <div>Loading portfolio…</div>
          )}
        </div>

        <div className="rounded-xl bg-white p-6 shadow-sm border">
          <h2 className="text-xl font-semibold">Place trade</h2>
          <div className="space-y-4 mt-4">
            <div>
              <label className="block text-sm font-medium text-slate-700">Ticker</label>
              <input className="w-full p-2 border rounded" value={ticker} onChange={e => setTicker(e.target.value)} />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">Action</label>
              <select className="w-full p-2 border rounded" value={action} onChange={e => setAction(e.target.value as 'BUY' | 'SELL')}>
                <option value="BUY">BUY</option>
                <option value="SELL">SELL</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">Quantity</label>
              <input type="number" min="1" className="w-full p-2 border rounded" value={quantity} onChange={e => setQuantity(e.target.value)} />
            </div>
            <button onClick={placeOrder} className="w-full px-4 py-2 bg-indigo-600 text-white rounded">Execute trade</button>
            {message && <div className="text-sm text-slate-700">{message}</div>}
          </div>
        </div>
      </div>
    </div>
  )
}
