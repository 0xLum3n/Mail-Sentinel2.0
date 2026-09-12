'use client'

import { useSyncExternalStore } from 'react'

export type AnalysisCase = {
  id: string
  emailId?: string
  timestamp: string
  source: string
  subject: string
  sender: string
  recipient: string
  risk: number
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  threatType: string
  auth: { spf: string; dkim: string; dmarc: string }
  iocs: { type: 'IP' | 'URL' | 'DOMAIN' | 'HASH'; value: string; verdict: string }[]
  mitre: { tactic: string; technique: string }[]
  timeline: { label: string; detail: string; latency: string }[]
}

const demoCase: AnalysisCase = {
  id: 'MS-2026-7848', timestamp: new Date().toISOString(), source: 'Demo case', subject: 'URGENT: Verify Your Account Within 24 Hours', sender: 'billing@secure-payments.example', recipient: 'analyst@mailsentinel.local', risk: 92, severity: 'CRITICAL', threatType: 'PHISHING',
  auth: { spf: 'FAIL', dkim: 'FAIL', dmarc: 'FAIL' },
  iocs: [{ type: 'DOMAIN', value: 'secure-payments.example', verdict: 'Malicious' }, { type: 'URL', value: 'https://secure-payments.example/verify', verdict: 'Phishing' }, { type: 'IP', value: '198.51.100.88', verdict: 'Suspicious' }],
  mitre: [{ tactic: 'Initial Access', technique: 'T1566.002 Phishing: Spearphishing Link' }, { tactic: 'Credential Access', technique: 'T1056.002 Input Capture' }],
  timeline: [{ label: 'Message created', detail: 'mail-client.local', latency: '—' }, { label: 'External relay', detail: '198.51.100.88 · Frankfurt', latency: '1.8s' }, { label: 'Recipient server', detail: 'mx.mailsentinel.local', latency: '0.4s' }],
}

let state: { cases: AnalysisCase[]; activeCaseId: string; settings: { thresholds: { medium: number; high: number; critical: number } } } = {
  cases: [demoCase], activeCaseId: demoCase.id, settings: { thresholds: { medium: 30, high: 60, critical: 80 } },
}
const listeners = new Set<() => void>()
const emit = () => listeners.forEach((listener) => listener())
export const analysisStore = {
  getState: () => state,
  subscribe: (listener: () => void) => { listeners.add(listener); return () => listeners.delete(listener) },
  ingest: (input: Partial<AnalysisCase>) => {
    const next = { ...demoCase, ...input, id: input.id ?? `MS-2026-${Math.floor(1000 + Math.random() * 8999)}`, timestamp: input.timestamp ?? new Date().toISOString(), source: input.source ?? 'Email upload' }
    state = { ...state, cases: [next, ...state.cases], activeCaseId: next.id }
    emit()
    return next
  },
  setActive: (id: string) => { state = { ...state, activeCaseId: id }; emit() },
  setThreshold: (key: 'medium' | 'high' | 'critical', value: number) => { state = { ...state, settings: { thresholds: { ...state.settings.thresholds, [key]: value } } }; emit() },
}

const serverSnapshot = state
export function useAnalysisStore() { return useSyncExternalStore(analysisStore.subscribe, analysisStore.getState, () => serverSnapshot) }
