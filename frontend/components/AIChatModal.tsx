"use client"
import { useState } from 'react'

export default function AIChatModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [messages, setMessages] = useState<string[]>([])
  const [input, setInput] = useState('')

  if (!open) return null

  function send() {
    if (!input) return
    setMessages(prev => [...prev, `You: ${input}`])
    setMessages(prev => [...prev, `AI: (placeholder) I can help with portfolio insights.`])
    setInput('')
  }

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center">
      <div className="bg-white w-11/12 md:w-1/2 p-4 rounded">
        <div className="flex justify-between items-center">
          <h3 className="text-lg font-semibold">AI Helpdesk (placeholder)</h3>
          <button onClick={onClose} className="text-slate-600">Close</button>
        </div>
        <div className="h-64 overflow-auto border my-3 p-2">
          {messages.map((m, i) => (
            <div key={i} className="mb-2">{m}</div>
          ))}
        </div>
        <div className="flex gap-2">
          <input value={input} onChange={e => setInput(e.target.value)} className="flex-1 p-2 border rounded" />
          <button onClick={send} className="px-4 py-2 bg-indigo-600 text-white rounded">Send</button>
        </div>
      </div>
    </div>
  )
}
