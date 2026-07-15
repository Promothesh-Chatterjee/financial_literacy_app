"use client"
import { useEffect, useState } from 'react'
import AIChatModal from './AIChatModal'

function useISTTime() {
  const [now, setNow] = useState(new Date())
  useEffect(() => {
    const t = setInterval(() => setNow(new Date()), 1000)
    return () => clearInterval(t)
  }, [])
  // convert to IST by adding 5.5 hours
  const utc = now.getTime() + now.getTimezoneOffset() * 60000
  const ist = new Date(utc + 5.5 * 3600000)
  return ist
}

export default function Header() {
  const ist = useISTTime()
  const [user, setUser] = useState<{email?:string} | null>(null)
  const [netWorth, setNetWorth] = useState<number | null>(null)
  const [todaysPnl, setTodaysPnl] = useState<number | null>(null)
  const [open, setOpen] = useState(false)

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/me`, { credentials: 'include' })
      .then(r => r.ok ? r.json() : null)
      .then(data => setUser(data))
      .catch(() => setUser(null))

    fetch(`${process.env.NEXT_PUBLIC_API_URL}/portfolio/summary`, { credentials: 'include' })
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        if (data) {
          setNetWorth(data.net_worth)
          setTodaysPnl(data.todays_pnl)
        }
      })
      .catch(() => {})
  }, [])

  // Market status logic
  const hrs = ist.getHours()
  const mins = ist.getMinutes()
  const timeMinutes = hrs * 60 + mins
  const preOpenStart = 9 * 60
  const preOpenEnd = 9 * 60 + 15
  const openStart = preOpenEnd
  const openEnd = 15 * 60 + 30

  let marketStatus = 'Market Closed'
  if (timeMinutes >= preOpenStart && timeMinutes < preOpenEnd) marketStatus = 'Pre-Open'
  else if (timeMinutes >= openStart && timeMinutes < openEnd) marketStatus = 'Market Open'

  const isWeekend = ist.getDay() === 0 || ist.getDay() === 6
  if (isWeekend) marketStatus = 'Market Closed - Weekend'

  return (
    <header className="w-full bg-white shadow p-4 flex items-center justify-between">
      <div className="flex items-center gap-4">
        <div className="font-semibold">{user?.email ? `Hi, ${user.email.split('@')[0]}` : 'Hi'}</div>
        <div className="text-sm text-slate-500">Net worth: <span className="font-medium">{netWorth !== null ? `₹${netWorth.toLocaleString('en-IN')}` : '—'}</span></div>
        <div className="text-sm text-slate-500">Today's P&L: <span className={`${(todaysPnl ?? 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>{todaysPnl !== null ? `₹${todaysPnl.toLocaleString('en-IN')}` : '—'}</span></div>
      </div>

      <div className="flex items-center gap-4">
        <div className="text-sm text-slate-600">{ist.toLocaleTimeString('en-IN')}</div>
        <div className="px-2 py-1 bg-slate-100 rounded text-sm">{marketStatus}</div>
        <div className="w-8 h-8 bg-slate-200 rounded-full" />
        <div className="w-8 h-8 bg-indigo-600 text-white rounded-full flex items-center justify-center cursor-pointer" onClick={() => setOpen(true)}>AI</div>
      </div>
      <AIChatModal open={open} onClose={() => setOpen(false)} />
    </header>
  )
}
