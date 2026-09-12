'use client'

import Link from 'next/link'
import { ArrowRight, LockKeyhole, ShieldCheck } from 'lucide-react'
import { FormEvent, useState } from 'react'
import { APIError, login, register } from '@/lib/api'
import { setAuthenticated } from '@/lib/auth'

export default function SignInPage() {
  const [mode, setMode] = useState<'signin' | 'signup'>('signin')
  const [submitted, setSubmitted] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (busy) return
    setBusy(true); setError('')
    const data = new FormData(event.currentTarget)
    const email = String(data.get('email') ?? '').trim()
    const password = String(data.get('password') ?? '')
    try {
      if (mode === 'signup') {
        const fullName = String(data.get('name') ?? '').trim().split(/\s+/)
        const first_name = fullName.shift() || 'SOC'
        const last_name = fullName.join(' ') || 'Analyst'
        await register({ email, password, first_name, last_name, organization_name: `${first_name}'s Security Workspace` })
      } else {
        await login(email, password)
      }
      setAuthenticated(true)
      setSubmitted(true)
      window.setTimeout(() => { window.location.href = '/dashboard' }, 250)
    } catch (caught) {
      setError(caught instanceof APIError ? caught.message : 'Unable to reach the Mail Sentinel backend.')
      setSubmitted(false)
    } finally { setBusy(false) }
  }

  return <main className="auth-shell"><div className="auth-glow" /><header className="auth-nav"><Link className="brand" href="/"><img className="brand-logo" src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/image-gDrpBHhVlVUcfGTYoG8zp5E1qldTaP.png" alt="Mail Sentinel logo" /><span>Mail Sentinel</span></Link><Link href="/pricing" className="auth-back">View plans <ArrowRight size={14} /></Link></header><section className="auth-card"><span className="eyebrow"><ShieldCheck size={14} /> SECURE ACCESS</span><h1>{mode === 'signin' ? 'Welcome back.' : 'Build your first line of defense.'}</h1><p>{mode === 'signin' ? 'Sign in to your security workspace and continue where you left off.' : 'Create a workspace for your team and start seeing the signal.'}</p><form onSubmit={submit}>{mode === 'signup' && <label>Full name<input required name="name" placeholder="Morgan Chen" /></label>}<label>Work email<input required type="email" name="email" placeholder="you@company.com" /></label><label>Password<input required minLength={8} type="password" name="password" placeholder="8+ characters" /></label>{error && <p className="upload-error" role="alert">{error}</p>}<button className="primary-button" type="submit" disabled={busy}>{submitted ? 'Access granted' : busy ? 'Connecting…' : mode === 'signin' ? 'Sign in to Aegis' : 'Create workspace'} <ArrowRight size={15} /></button></form><div className="auth-divider"><span />or<span /></div><button className="sso-button" onClick={() => setError('SSO is not connected yet. Use email and password for the current backend integration.')}><LockKeyhole size={15} /> Continue with SSO</button><p className="auth-switch">{mode === 'signin' ? 'New to Aegis?' : 'Already have an account?'} <button onClick={() => { setMode(mode === 'signin' ? 'signup' : 'signin'); setSubmitted(false); setError('') }}>{mode === 'signin' ? 'Create an account' : 'Sign in'}</button></p></section><footer className="auth-footer">Your workspace is protected with enterprise-grade encryption.</footer></main>
}
