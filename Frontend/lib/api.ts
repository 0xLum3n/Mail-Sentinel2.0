const API_BASE_URL = (process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1').replace(/\/$/, '')

export type TokenPair = {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export type AuthUser = {
  id: string
  email: string
  first_name: string
  last_name: string
  is_active: boolean
  is_email_verified: boolean
  created_at: string
}

export type RegisterResponse = {
  user: AuthUser
  organization_id: string
  tokens: TokenPair
}

export type IndicatorResponse = {
  type: 'IP' | 'URL' | 'DOMAIN' | 'HASH' | 'EMAIL'
  value: string
  verdict: string
  confidence_score: number | null
  source: string | null
  context: string | null
  enrichment: Record<string, unknown>
}

export type EmailAnalysisResponse = {
  id: string
  email_id: string
  status: string
  risk_score: number | null
  severity: string | null
  threat_type: string | null
  verdict: string | null
  confidence_score: number | null
  summary: string | null
  auth_results: { spf: string; dkim: string; dmarc: string }
  engine_version: string | null
  ai_provider: string | null
  ai_model: string | null
  started_at: string | null
  completed_at: string | null
  created_at: string
  findings: Array<{ code: string | null; title: string; description: string; severity: string; source: string; weight: number; evidence: Record<string, unknown> }>
  indicators: IndicatorResponse[]
  mitre_mappings: Array<{ tactic: string; technique_id: string | null; technique_name: string; confidence_score: number | null }>
  metadata_json: Record<string, unknown>
}

export type EmailResponse = {
  id: string
  message_hash: string
  original_filename: string | null
  source: string
  subject: string | null
  sender_email: string | null
  recipient_email: string | null
  reply_to_email: string | null
  received_at: string | null
  created_at: string
  analyses: EmailAnalysisResponse[]
}

export type SOCChatResponse = {
  message: string
  provider: string
  model: string
  response_id: string | null
  usage: Record<string, unknown> | null
}

export class APIError extends Error {
  status: number
  constructor(message: string, status: number) {
    super(message)
    this.name = 'APIError'
    this.status = status
  }
}

function readToken(): string | null {
  if (typeof window === 'undefined') return null
  return window.localStorage.getItem('mail-sentinel.access-token')
}

function saveTokens(tokens: TokenPair) {
  window.localStorage.setItem('mail-sentinel.access-token', tokens.access_token)
  window.localStorage.setItem('mail-sentinel.refresh-token', tokens.refresh_token)
  window.localStorage.setItem('mail-sentinel.token-expires-at', String(Date.now() + tokens.expires_in * 1000))
}

export function hasAccessToken() {
  return Boolean(readToken())
}

export function clearAuth() {
  if (typeof window === 'undefined') return
  window.localStorage.removeItem('mail-sentinel.access-token')
  window.localStorage.removeItem('mail-sentinel.refresh-token')
  window.localStorage.removeItem('mail-sentinel.token-expires-at')
}

async function request<T>(path: string, init: RequestInit = {}, retry = true): Promise<T> {
  const headers = new Headers(init.headers)
  if (!(init.body instanceof FormData)) headers.set('Content-Type', 'application/json')
  const token = readToken()
  if (token) headers.set('Authorization', `Bearer ${token}`)

  const response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers })
  if (response.ok) {
    if (response.status === 204) return undefined as T
    return response.json() as Promise<T>
  }

  let detail = `Request failed with status ${response.status}`
  try {
    const payload = await response.json() as { detail?: string }
    if (payload.detail) detail = payload.detail
  } catch { /* non-JSON error */ }

  if (response.status === 401 && retry && typeof window !== 'undefined') {
    const refreshToken = window.localStorage.getItem('mail-sentinel.refresh-token')
    if (refreshToken) {
      const refreshed = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      })
      if (refreshed.ok) {
        const pair = await refreshed.json() as TokenPair
        saveTokens(pair)
        return request<T>(path, init, false)
      }
      clearAuth()
    }
  }

  throw new APIError(detail, response.status)
}

export async function login(email: string, password: string) {
  const tokens = await request<TokenPair>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
  saveTokens(tokens)
  return tokens
}

export async function register(input: { email: string; password: string; first_name: string; last_name: string; organization_name: string }) {
  const result = await request<RegisterResponse>('/auth/register', {
    method: 'POST',
    body: JSON.stringify(input),
  })
  saveTokens(result.tokens)
  return result
}

export async function logout() {
  const refreshToken = typeof window !== 'undefined' ? window.localStorage.getItem('mail-sentinel.refresh-token') : null
  try {
    if (refreshToken) {
      await request('/auth/logout', { method: 'POST', body: JSON.stringify({ refresh_token: refreshToken }) }, false)
    }
  } finally {
    clearAuth()
  }
}

export async function uploadEmail(file: File) {
  const form = new FormData()
  form.append('file', file)
  return request<EmailResponse>('/emails', { method: 'POST', body: form })
}

export async function analyzeEmail(emailId: string) {
  return request<EmailResponse>(`/emails/${encodeURIComponent(emailId)}/analyze`, { method: 'POST' })
}

export async function getEmail(emailId: string) {
  return request<EmailResponse>(`/emails/${encodeURIComponent(emailId)}`)
}

export async function sendSOCChat(input: { emailId: string; message: string; history: Array<{ role: 'user' | 'assistant'; content: string }> }) {
  return request<SOCChatResponse>('/ai/chat', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}
