'use client'

import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { useEffect, useRef, useState } from 'react'
import AIChatDrawer from '@/components/ai-chat-drawer'
import { Activity, BarChart3, Bot, Check, ChevronRight, CircleHelp, FileJson, FileText, Globe2, Inbox, LayoutDashboard, Mail, Menu, Radar, Search, Settings, ShieldAlert, Upload } from 'lucide-react'
import { analysisStore, useAnalysisStore, type AnalysisCase } from '@/lib/analysis-store'
import { analyzeEmail, APIError, uploadEmail, type EmailResponse } from '@/lib/api'

const navItems = [
  { label: 'Dashboard', slug: 'dashboard', icon: LayoutDashboard },
  { label: 'Email Analysis', slug: 'email-analysis', icon: Mail },
  { label: 'Investigations', slug: 'investigations', icon: Search },
  { label: 'Threat Intelligence', slug: 'threat-intelligence', icon: Radar },
  { label: 'Forensic Timeline', slug: 'forensic-timeline', icon: Activity },
  { label: 'Reports', slug: 'reports', icon: FileText },
  { label: 'Settings', slug: 'settings', icon: Settings },
]

const investigations = [
  ['MS-2026-7824', "Enter To Win Fall Children's Books", 'LOW', '15', 'PHISHING 55%', 'kirkusreviews.com'],
  ['MS-2026-7848', 'URGENT: Verify Your Account Within 24 Hours', 'CRITICAL', '100', 'PHISHING 95%', 'secure-payments.example'],
  ['MS-2026-5051', 'FINAL NOTICE: Unauthorized transaction', 'CRITICAL', '100', 'PHISHING 98%', 'paypal-secure-checkpoint.top'],
  ['MS-2026-1748', 'Q3 architecture review moved to Thursday 10:00', 'LOW', '0', 'LEGITIMATE 3%', 'northwind-labs.com'],
]

function Brand() { return <Link href="/" className="ms-brand" aria-label="Mail Sentinel home"><img className="brand-logo" src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/image-gDrpBHhVlVUcfGTYoG8zp5E1qldTaP.png" alt="Mail Sentinel logo" /><span><b>Mail Sentinel</b><small>SOC CONSOLE</small></span></Link> }
function Risk({ level, score }: { level: string; score: string }) { return <span className={`ms-risk ${level.toLowerCase()}`}><i />{level} · {score}</span> }

export default function SecurityDashboard() {
  const pathname = usePathname()
  const router = useRouter()
  const active = navItems.find((item) => item.slug === pathname.split('/').filter(Boolean).at(-1))?.label ?? 'Dashboard'
  const [chatOpen, setChatOpen] = useState(false)
  const [demo, setDemo] = useState(true)
  const [navOpen, setNavOpen] = useState(false)
  const [navVisible, setNavVisible] = useState(false)
  const analysisState = useAnalysisStore()
  const cases = analysisState.cases
  const activeCase = cases.find((item) => item.id === analysisState.activeCaseId) ?? cases[0]
  useEffect(() => {
    const syncNavigation = () => {
      const desktop = window.innerWidth > 800
      setNavVisible(desktop)
      setNavOpen(desktop)
    }
    syncNavigation()
    window.addEventListener('resize', syncNavigation)
    return () => window.removeEventListener('resize', syncNavigation)
  }, [])
  const closeNav = () => {
    if (window.innerWidth > 800) return
    setNavOpen(false)
    window.setTimeout(() => setNavVisible(false), 420)
  }
  const toggleNav = () => { if (navOpen) closeNav(); else { setNavVisible(true); setNavOpen(true) } }

  return <main className="mail-app">
    {navVisible && <button className={`mobile-nav-backdrop ${navOpen ? 'nav-backdrop-open' : 'nav-backdrop-closing'}`} aria-label="Close navigation" onClick={closeNav} />}
    {navVisible && <aside className={`mail-sidebar ${navOpen ? 'mobile-sidebar-open' : 'mobile-sidebar-closing'}`} onClick={(event) => event.stopPropagation()}>
      <Brand />
      <nav className="mail-nav" aria-label="SOC console navigation">{navItems.map(({ label, slug, icon: Icon }) => <Link href={slug === 'dashboard' ? '/dashboard' : `/dashboard/${slug}`} key={label} onClick={closeNav} className={active === label ? 'selected' : ''}><Icon size={16} /><span>{label}</span>{active === label && <b />}</Link>)}</nav>
      <div className="signed-in"><small>SIGNED IN</small><strong>SOC Analyst</strong><code>analyst@mailsentinel.local</code></div>
    </aside>}
    <section className="mail-main">
      <header className="mail-header"><div className="desktop-header-brand"><b>Mail Sentinel</b><small>AI Email Security &amp; Forensic Intelligence</small></div><div className="header-actions"><span className="engine"><i /> ENGINE ONLINE</span><span className="demo">Signed As :</span><button className="account-profile" aria-label="Switch analyst"><img src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/image-gDrpBHhVlVUcfGTYoG8zp5E1qldTaP.png" alt="SOC Analyst profile" /><span>SOC Analyst</span></button></div></header>
      <div className="dashboard-menu-row"><button className="mobile-menu" aria-label={navOpen ? 'Close navigation' : 'Open navigation'} aria-expanded={navOpen} onClick={toggleNav}><Menu size={17} /></button></div>
      <div key={pathname} className="mail-content page-transition">
        <div className="mail-title"><div><h1>{active}</h1><p>{active === 'Dashboard' ? 'Aggregate view of every email investigation processed by the detection engine.' : active === 'Threat Intelligence' ? 'Aggregated indicators from stored investigations and observed infrastructure.' : `Review and manage ${active.toLowerCase()} across your security workspace.`}</p></div><div className="title-actions"><span className="demo-label">INCLUDING DEMO CASES</span><button className="analyze-btn" onClick={() => router.push('/dashboard/email-analysis')}><Mail size={15} /> Analyze an email</button></div></div>
        {active === 'Dashboard' && <DashboardView cases={cases} demo={demo} setDemo={setDemo} />}
        {active === 'Email Analysis' && <EmailView />}
        {active === 'Investigations' && <InvestigationView cases={cases} />}
        {active === 'Threat Intelligence' && <ThreatView cases={cases} />}
        {active === 'Reports' && <ReportsView cases={cases} />}
        {active === 'Settings' && <SettingsView demo={demo} setDemo={setDemo} />}
        {active === 'Forensic Timeline' && <TimelineView cases={cases} />}
      </div>
    </section>
    <button className="chat-fab" onClick={() => setChatOpen(true)} aria-label="Open AI analyst"><Bot size={19} /></button>
    <AIChatDrawer open={chatOpen} onClose={() => setChatOpen(false)} emailId={activeCase?.emailId} />
  </main>
}

function DashboardView({ cases, demo, setDemo }: { cases: AnalysisCase[]; demo: boolean; setDemo: (value: boolean) => void }) { const critical = cases.filter((item) => item.severity === 'CRITICAL').length; const high = cases.filter((item) => item.risk >= 60).length; return <>
  <div className="stat-grid"><Stat label="TOTAL INVESTIGATIONS" value={String(cases.length)} note="Live synchronized cases" icon={<Activity />} /><Stat label="HIGH RISK EMAILS" value={String(high)} note="Score 60 or above" tone="yellow" icon={<ShieldAlert />} /><Stat label="CRITICAL THREATS" value={String(critical)} note="Score 80 or above" tone="pink" icon={<ShieldAlert />} /><Stat label="SUSPICIOUS URLS" value="20" note="Static analysis only" tone="pink" icon={<Globe2 />} /><Stat label="OBSERVED IPS" value="13" note="Distinct addresses" icon={<Globe2 />} /></div>
  <div className="dash-grid"><Panel title="THREAT DISTRIBUTION" subtitle="Investigations by risk level"><div className="donut"><div><b>24</b><small>CASES</small></div></div><div className="legend"><span className="critical">CRITICAL</span><span className="high">HIGH</span><span className="low">LOW</span><span className="medium">MEDIUM</span></div></Panel><Panel title="THREATS OVER TIME" subtitle="Last 30 days"><LineChart /></Panel><Panel title="TOP SUSPICIOUS DOMAINS" subtitle="Ranked by highest observed score"><div className="bars">{['paypal-secure-checkpoint.top','northwind-labs.com','example-test.com','secure-payments.example','secure-alerts-microsoft.com'].map((x, i) => <div key={x}><span>{x}</span><i style={{ width: `${[96, 72, 48, 38, 31][i]}%` }} /></div>)}</div></Panel><Panel title="RISK CATEGORIES" subtitle="Total indicator weight per category"><RadarChart /></Panel></div>
</> }
function Stat({ label, value, note, tone = '', icon }: { label: string; value: string; note: string; tone?: string; icon: React.ReactNode }) { return <article className="stat-card"><div><small>{label}</small>{icon}</div><strong className={tone}>{value}</strong><p>{note}</p></article> }
function Panel({ title, subtitle, children }: { title: string; subtitle: string; children: React.ReactNode }) { return <article className="ms-panel"><header><div><h2>{title}</h2><p>{subtitle}</p></div></header><div className="panel-body">{children}</div></article> }
function LineChart() { return <div className="line-chart"><div className="line-grid" /><svg viewBox="0 0 600 190" preserveAspectRatio="none"><path d="M0 45 C80 75 140 90 210 115 S340 145 410 142 S520 155 600 158" fill="none" stroke="#4ba4ec" strokeWidth="3" /><path d="M0 95 C80 112 140 126 210 145 S340 167 410 166 S520 171 600 173" fill="none" stroke="#f63e6e" strokeWidth="3" /></svg><div className="axis"><span>08-29</span><span>08-31</span><span>09-01</span></div></div> }
function RadarChart() { return <div className="radar-chart"><div className="radar-ring r1" /><div className="radar-ring r2" /><div className="radar-shape" /><span>network</span><span>sender</span><span>url</span><span>authentication</span><span>content</span></div> }
function EmailView() {
  const inputRef = useRef<HTMLInputElement>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [fileError, setFileError] = useState('')
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState<EmailResponse | null>(null)

  const validateFile = (file?: File) => {
    if (!file) return
    const extension = `.${file.name.split('.').pop()?.toLowerCase() ?? ''}`
    if (file.size > 5 * 1024 * 1024) { setSelectedFile(null); setFileError('File is too large. Maximum allowed size is 5 MB.'); return }
    if (!['.eml', '.txt', '.nine'].includes(extension)) { setSelectedFile(null); setFileError('Unsupported file type. Use .eml, .txt, or .nine.'); return }
    setFileError(''); setSelectedFile(file); setResult(null)
  }

  const runSelectedAnalysis = async () => {
    if (!selectedFile || busy) return
    setBusy(true); setFileError('')
    try {
      const uploaded = await uploadEmail(selectedFile)
      const analyzed = await analyzeEmail(uploaded.id)
      setResult(analyzed)
      const latest = analyzed.analyses.at(-1)
      const indicatorCases = latest?.indicators ?? []
      const mapped: AnalysisCase = {
        id: `MS-${analyzed.id.slice(0, 8).toUpperCase()}`,
        emailId: analyzed.id,
        timestamp: analyzed.created_at,
        source: 'Email upload',
        subject: analyzed.subject ?? '(No subject)',
        sender: analyzed.sender_email ?? 'unknown',
        recipient: analyzed.recipient_email ?? 'unknown',
        risk: latest?.risk_score ?? 0,
        severity: normalizeSeverity(latest?.severity),
        threatType: latest?.threat_type ?? 'UNKNOWN',
        auth: latest?.auth_results ?? { spf: 'UNKNOWN', dkim: 'UNKNOWN', dmarc: 'UNKNOWN' },
        iocs: indicatorCases.filter((item) => item.type !== 'EMAIL').map((item) => ({ type: item.type as 'IP' | 'URL' | 'DOMAIN' | 'HASH', value: item.value, verdict: item.verdict })),
        mitre: latest?.mitre_mappings.map((item) => ({ tactic: item.tactic, technique: `${item.technique_id ? `${item.technique_id} ` : ''}${item.technique_name}` })) ?? [],
        timeline: [],
      }
      analysisStore.setActive(mapped.id)
      analysisStore.ingest(mapped)
      analysisStore.setActive(mapped.id)
    } catch (error) {
      setFileError(error instanceof APIError ? error.message : 'The email could not be analyzed. Check that the backend is running and you are signed in.')
    } finally { setBusy(false) }
  }

  return <div className="view-grid"><Panel title="UPLOAD MESSAGE" subtitle="Maximum size 5 MB · .eml, .txt, .nine"><div className="upload-zone"><UploadIcon /><strong>{selectedFile ? selectedFile.name : 'Drag & drop a raw email file here'}</strong><small>{selectedFile ? `${(selectedFile.size / 1024).toFixed(1)} KB · File accepted and ready for analysis` : 'The message is uploaded to your configured Mail Sentinel backend for secure analysis.'}</small><input ref={inputRef} type="file" accept=".eml,.txt,.nine" className="file-input-hidden" onChange={(event) => validateFile(event.target.files?.[0])} /><button type="button" onClick={() => { setFileError(''); inputRef.current?.click() }}>Browse files</button>{selectedFile && <button type="button" className="analyze-btn" onClick={() => void runSelectedAnalysis()} disabled={busy}>{busy ? 'Analyzing…' : 'Analyze selected email'}</button>}{fileError && <span className="upload-error" role="alert">{fileError}</span>}</div><div className="examples"><small>EXAMPLE EMAILS</small>{['Legitimate corporate email','Brand impersonation phishing email','Highly suspicious credential-stealing email'].map((x, i) => <div key={x}><div><b>{x}</b><p>{i === 0 ? 'Internal schedule notice with aligned SPF, DKIM and DMARC.' : 'Lookalike domain with authentication and URL indicators.'}</p></div><button onClick={() => analysisStore.ingest({ subject: x, source: 'Demo case', threatType: i === 0 ? 'LEGITIMATE' : 'PHISHING', risk: i === 0 ? 12 : i === 1 ? 78 : 96, severity: i === 0 ? 'LOW' : i === 1 ? 'HIGH' : 'CRITICAL' })}>▷ Analyze</button></div>)}</div></Panel><Panel title="ANALYSIS RESULT" subtitle={result?.subject ?? 'Awaiting a message'}>{result?.analyses.length ? <AnalysisResultCard result={result} /> : <div className="empty-state"><Inbox size={28} /><b>No analysis yet</b><p>Results appear here the moment the detection engine returns, then the case is stored for later review.</p></div>}</Panel></div>
}

function normalizeSeverity(value?: string | null): AnalysisCase['severity'] {
  return value === 'CRITICAL' || value === 'HIGH' || value === 'MEDIUM' ? value : 'LOW'
}

function AnalysisResultCard({ result }: { result: EmailResponse }) {
  const latest = result.analyses.at(-1)
  if (!latest) return null
  return <div className="analysis-result"><div className="result-head"><Risk level={normalizeSeverity(latest.severity)} score={String(latest.risk_score ?? 0)} /><strong>{latest.verdict ?? 'Unknown'}</strong></div><p>{latest.summary ?? 'Analysis completed without a summary.'}</p><div className="result-grid"><span><small>SPF</small><b>{latest.auth_results.spf}</b></span><span><small>DKIM</small><b>{latest.auth_results.dkim}</b></span><span><small>DMARC</small><b>{latest.auth_results.dmarc}</b></span><span><small>AI</small><b>{latest.ai_provider ? 'ENRICHED' : 'NOT CONFIGURED'}</b></span></div><small>{latest.indicators.length} indicators · {latest.findings.length} findings · {latest.mitre_mappings.length} MITRE mappings</small></div>
}
function InvestigationView({ cases }: { cases: AnalysisCase[] }) { return <Panel title="INVESTIGATIONS" subtitle="Every analysis is stored as a case and can be reopened at any time."><div className="table-tools"><Search size={15} /><input placeholder="Search case, subject, sender or domain" /></div><div className="case-table">{cases.map((row) => <div className="case-row" key={row.id} onClick={() => analysisStore.setActive(row.id)} role="button" tabIndex={0} onKeyDown={(event) => { if (event.key === 'Enter' || event.key === ' ') analysisStore.setActive(row.id) }}><code>{row.id}</code><strong>{row.subject}</strong><span>{row.iocs[0]?.value ?? 'No IOC'}</span><Risk level={row.severity} score={String(row.risk)} /><small>{row.threatType} {row.risk}%</small><time>{new Date(row.timestamp).toLocaleString()}</time><ChevronRight size={15} /></div>)}</div></Panel> }
function ThreatView({ cases }: { cases: AnalysisCase[] }) { const iocs = cases.flatMap((item) => item.iocs); return <div className="view-grid"><Panel title="OBSERVED IP ADDRESSES" subtitle="Aggregated across live investigations"><IndicatorTable type="ip" rows={iocs.filter((item) => item.type === 'IP').map((item) => item.value)} /></Panel><Panel title="LINKED DOMAINS" subtitle="Ranked by maximum observed URL risk"><IndicatorTable type="domain" rows={iocs.filter((item) => item.type === 'DOMAIN' || item.type === 'URL').map((item) => item.value)} /></Panel></div> }
function IndicatorTable({ type, rows: inputRows }: { type: 'ip' | 'domain'; rows?: string[] }) { const rows = inputRows?.length ? inputRows : type === 'ip' ? ['91.215.85.142','198.51.100.88','45.155.205.199','209.85.220.41','203.0.113.77','143.244.89.175'] : ['185.220.101.44','secure-microsoft-login.verify-account-update.xyz','bit.ly','www.paypal.com','example-test.com','workspace.northwind-labs.com']; return <div className="indicator-list">{rows.map((row, i) => <div key={row}><code>{row}</code><span>{type === 'ip' ? ['Amsterdam, Netherlands','Frankfurt am Main, Germany','Moscow, Russia'][i % 3] : `${74 - i * 9}/100`}</span><small>{i + 2}× seen</small></div>)}</div> }
function downloadReport(row: AnalysisCase, format: 'json' | 'csv') { const payload = format === 'json' ? JSON.stringify(row, null, 2) : `type,value,verdict\n${row.iocs.map((ioc) => `${ioc.type},${ioc.value},${ioc.verdict}`).join('\n')}`; const blob = new Blob([payload], { type: format === 'json' ? 'application/json' : 'text/csv' }); const url = URL.createObjectURL(blob); const anchor = document.createElement('a'); anchor.href = url; anchor.download = `${row.id}.${format}`; anchor.click(); URL.revokeObjectURL(url) }
function ReportsView({ cases }: { cases: AnalysisCase[] }) { return <Panel title="AVAILABLE REPORTS" subtitle="Generate downloadable JSON or CSV reports for any investigation."><div className="report-list">{cases.map((row) => <div key={row.id}><div><code>{row.id}</code><strong>{row.subject}</strong></div><Risk level={row.severity} score={String(row.risk)} /><button onClick={() => downloadReport(row, 'csv')}><FileText size={14} /> CSV</button><button onClick={() => downloadReport(row, 'json')}><FileJson size={14} /> JSON</button></div>)}</div></Panel> }
function SettingsView({ demo, setDemo }: { demo: boolean; setDemo: (value: boolean) => void }) { return <div className="view-grid"><Panel title="DETECTION RULE WEIGHTS" subtitle="Transparent scoring — each fired rule adds its weight to the total"><div className="settings-list">{['Reply-To domain differs from sender','Display name impersonates a known brand','SPF authentication failed','DKIM authentication failed','Suspicious URL detected'].map((x) => <label key={x}><input type="checkbox" defaultChecked /> <span>{x}<small>Rule contributes to the investigation risk score.</small></span><input type="number" defaultValue="20" /></label>)}</div><button className="analyze-btn" onClick={() => alert('Detection weights saved')}>Save weights</button></Panel><Panel title="DEMO MODE" subtitle="Synthetic intelligence for offline demonstrations"><label className="demo-toggle"><input type="checkbox" checked={demo} onChange={(e) => setDemo(e.target.checked)} /> Enable Demo Mode</label><p className="settings-copy">When enabled, public IPs are enriched with deterministic synthetic values and labelled DEMO DATA.</p><div className="system-info"><span>IP_API_KEY <b>not configured</b></span><span>UPLOAD LIMIT <b>5 MB</b></span><span>DATABASE <b className="green">connected</b></span></div></Panel></div> }
function TimelineView({ cases }: { cases: AnalysisCase[] }) { const activeCase = cases[0]; const hops = activeCase?.timeline ?? []; return <Panel title="TRANSPORT CHAIN" subtitle={`Mail routing reconstructed from Received headers · ${activeCase?.id ?? 'No active case'}`}><div className="timeline">{hops.map((hop, i) => <div key={hop.label}><span>{i === 0 ? <Mail size={14} /> : <Globe2 size={14} />}</span><div><b>{hop.label}</b><small>Sun, 16 Aug 2026 19:03:{49 + i * 2} UTC</small><p>{hop.detail} · Transit latency <code>{hop.latency}</code></p></div></div>)}</div></Panel> }
function UploadIcon() { return <div className="upload-icon"><Inbox size={26} /></div> }
function LogOutIcon() { return <span aria-hidden="true">↪</span> }

export { DashboardView }
