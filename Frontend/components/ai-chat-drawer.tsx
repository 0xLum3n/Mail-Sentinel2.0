'use client'

import { Bot, LockKeyhole, Send, Sparkles, X } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { sendSOCChat } from '@/lib/api'

const prompts = ['Summarize this investigation', 'Explain this phishing signal', 'What should I investigate next?', 'Draft an incident update']
type ChatMessage = { id: string; role: 'user' | 'assistant'; content: string }

export default function AIChatDrawer({ open, onClose, emailId }: { open: boolean; onClose: () => void; emailId?: string }) {
  const [input, setInput] = useState('')
  const [isVisible, setIsVisible] = useState(open)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const history = useMemo(() => messages.map(({ role, content }) => ({ role, content })), [messages])

  useEffect(() => {
    if (open) setIsVisible(true)
    else if (isVisible) {
      const timer = window.setTimeout(() => setIsVisible(false), 420)
      return () => window.clearTimeout(timer)
    }
  }, [open, isVisible])

  useEffect(() => {
    if (open) setError('')
  }, [open, emailId])

  if (!isVisible) return null

  const submit = async (text = input) => {
    const content = text.trim()
    if (!content || busy) return
    if (!emailId) {
      setError('Select or analyze an email investigation before asking the analyst.')
      return
    }

    setError('')
    setInput('')
    const userMessage: ChatMessage = { id: crypto.randomUUID(), role: 'user', content }
    setMessages((current) => [...current, userMessage])
    setBusy(true)
    try {
      const result = await sendSOCChat({ emailId, message: content, history })
      setMessages((current) => [...current, { id: crypto.randomUUID(), role: 'assistant', content: result.message }])
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'The analyst could not respond.')
    } finally {
      setBusy(false)
    }
  }

  const clearConversation = () => {
    if (busy) return
    setMessages([])
    setError('')
  }

  return <div className={`chat-overlay ${open ? 'chat-overlay-open' : 'chat-overlay-closing'}`} onClick={onClose}>
    <aside className={`chat-drawer ai-chat-drawer ${open ? 'chat-drawer-open' : 'chat-drawer-closing'}`} onClick={(event) => event.stopPropagation()}>
      <div className="chat-head"><div><span><Sparkles size={13} /> AI SOC ANALYST</span><h2>Ask the analyst</h2></div><button onClick={onClose} aria-label="Close chat"><X size={18} /></button></div>
      <p>Connect the dots across your investigations, indicators, and threat posture. The analyst receives the selected investigation as structured security evidence.</p>
      <div className="quick-prompts">{prompts.map((prompt) => <button key={prompt} onClick={() => submit(prompt)} disabled={busy || !emailId}>{prompt}</button>)}</div>
      {!emailId && <div className="chat-error" role="status">Analyze an email first to give the analyst investigation context.</div>}
      {error && <div className="chat-error" role="alert">{error}<button onClick={() => setError('')}>Dismiss</button></div>}
      <div className="messages" aria-live="polite">
        {messages.length === 0 && <div className="chat-empty"><Bot size={25} /><strong>Ready when you are</strong><span>Ask about the active investigation or choose a prompt above.</span></div>}
        {messages.map((message) => <div className={message.role === 'user' ? 'message user-message' : 'message ai-message'} key={message.id}><span>{message.content}</span></div>)}
        {busy && <div className="message ai-message typing"><i /><i /><i /><span>Analyzing evidence…</span></div>}
      </div>
      <form className="prompt-box" onSubmit={(event) => { event.preventDefault(); void submit() }}>
        <input value={input} onChange={(event) => setInput(event.target.value)} disabled={busy || !emailId} placeholder={emailId ? 'Ask the analyst anything...' : 'Analyze an email first'} aria-label="Ask the AI SOC analyst" />
        <button type="submit" disabled={busy || !input.trim() || !emailId} aria-label="Send question"><Send size={16} /></button>
      </form>
      <div className="drawer-note"><LockKeyhole size={12} /> Responses are generated from the selected investigation · <button type="button" onClick={clearConversation} disabled={busy}>Clear</button></div>
    </aside>
  </div>
}
