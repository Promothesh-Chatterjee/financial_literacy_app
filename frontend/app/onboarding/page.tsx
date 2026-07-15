"use client"
import { useState } from 'react'
import { useRouter } from 'next/navigation'

export default function Onboarding() {
  const [step, setStep] = useState(0)
  const [fullName, setFullName] = useState('')
  const [employment, setEmployment] = useState('Salaried')
  const [salary, setSalary] = useState('')
  const [objectives, setObjectives] = useState<string[]>([])
  const [risk, setRisk] = useState('Moderate')
  const [starting, setStarting] = useState('100000')
  const router = useRouter()

  const objectiveOptions = [
    'Wealth Creation',
    'Retirement Planning',
    'Tax Saving',
    'Emergency Fund',
    'Short-Term Trading',
    'Learning Basics',
  ]

  function toggleObjective(opt: string) {
    setObjectives(prev => (prev.includes(opt) ? prev.filter(x => x !== opt) : [...prev, opt]))
  }

  async function submit() {
    const payload = {
      full_name: fullName,
      employment_status: employment,
      annual_salary: salary ? Number(salary) : null,
      objectives,
      risk_profile: risk,
      starting_capital: Number(starting),
    }
    // read csrf token from cookie and include as header
    const getCookie = (name: string) => document.cookie.split('; ').find(row => row.startsWith(name + '='))?.split('=')[1]
    const csrf = getCookie('csrf_token')
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/onboarding/complete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...(csrf ? { 'x-csrf-token': csrf } : {}) },
      credentials: 'include',
      body: JSON.stringify(payload),
    })
    if (res.ok) router.push('/')
    else alert('Failed to complete onboarding')
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h2 className="text-2xl font-bold mb-4">Onboarding</h2>
      {step === 0 && (
        <div className="space-y-4">
          <label>Full name</label>
          <input className="w-full p-2 border rounded" value={fullName} onChange={e => setFullName(e.target.value)} />
          <button onClick={() => setStep(1)} className="px-4 py-2 bg-indigo-600 text-white rounded">Next</button>
        </div>
      )}
      {step === 1 && (
        <div className="space-y-4">
          <label>Employment status</label>
          <select className="w-full p-2 border rounded" value={employment} onChange={e => setEmployment(e.target.value)}>
            <option>Student</option>
            <option>Salaried</option>
            <option>Self-Employed</option>
            <option>Unemployed</option>
          </select>
          <label>Annual salary / available funds</label>
          <input className="w-full p-2 border rounded" value={salary} onChange={e => setSalary(e.target.value)} />
          <button onClick={() => setStep(2)} className="px-4 py-2 bg-indigo-600 text-white rounded">Next</button>
        </div>
      )}
      {step === 2 && (
        <div className="space-y-4">
          <label>Objectives</label>
          <div className="grid grid-cols-2 gap-2">
            {objectiveOptions.map(opt => (
              <button type="button" key={opt} onClick={() => toggleObjective(opt)} className={`p-2 border rounded ${objectives.includes(opt) ? 'bg-indigo-100' : ''}`}>
                {opt}
              </button>
            ))}
          </div>
          <button onClick={() => setStep(3)} className="px-4 py-2 bg-indigo-600 text-white rounded">Next</button>
        </div>
      )}
      {step === 3 && (
        <div className="space-y-4">
          <label>Risk profile</label>
          <select className="w-full p-2 border rounded" value={risk} onChange={e => setRisk(e.target.value)}>
            <option>Conservative</option>
            <option>Moderate</option>
            <option>Aggressive</option>
          </select>
          <label>Starting virtual capital (INR)</label>
          <input className="w-full p-2 border rounded" value={starting} onChange={e => setStarting(e.target.value)} />
          <div className="flex gap-2">
            <button onClick={() => setStep(2)} className="px-4 py-2 border rounded">Back</button>
            <button onClick={submit} className="px-4 py-2 bg-green-600 text-white rounded">Complete Onboarding</button>
          </div>
        </div>
      )}
    </div>
  )
}
