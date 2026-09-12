'use client'

import Link from 'next/link'
import AIChatDrawer from '@/components/ai-chat-drawer'
import { useEffect, useMemo, useRef, useState } from 'react'
import {
  Activity,
  AlertTriangle,
  GitBranch,
  BriefcaseBusiness,
  AtSign,
  PlaySquare,
  MessageCircle,
  ArrowUpRight,
  Check,
  ChevronDown,
  CircleDot,
  Clock3,
  FileSearch,
  Fingerprint,
  Globe2,
  Inbox,
  LayoutDashboard,
  Mail,
  Menu,
  MessageSquareText,
  Radar,
  Search,
  ShieldCheck,
  Sparkles,
  Upload,
} from 'lucide-react'

const threats = [
  { time: '12:42:18', type: 'Credential theft', source: '185.220.101.14', severity: 'Critical', score: 96, country: 'NL' },
  { time: '12:38:04', type: 'Malware delivery', source: 'mail-freight.co', severity: 'High', score: 82, country: 'RU' },
  { time: '12:31:47', type: 'Suspicious login', source: '45.12.88.201', severity: 'Medium', score: 61, country: 'US' },
  { time: '12:18:26', type: 'Phishing attempt', source: 'sharepoint-alerts.com', severity: 'High', score: 78, country: 'CN' },
]

const investigations = [
  { id: 'INV-2481', title: 'Executive impersonation campaign', status: 'Active', owner: 'M. Chen', time: '8 min ago' },
  { id: 'INV-2478', title: 'OAuth consent anomaly', status: 'Review', owner: 'A. Patel', time: '24 min ago' },
  { id: 'INV-2472', title: 'Payroll redirect attempt', status: 'Resolved', owner: 'J. Rivera', time: '1 hr ago' },
]

function BrandMark() {
  return <img className="brand-logo" src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/image-gDrpBHhVlVUcfGTYoG8zp5E1qldTaP.png" alt="Mail Sentinel logo" />
}

function SectionLabel({ children }: { children: React.ReactNode }) {
  return <div className="section-label"><span className="label-line" />{children}<span className="label-line" /></div>
}

function useCountUp(target: number, duration = 900) {
  const [value, setValue] = useState(0)

  useEffect(() => {
    let frame = 0
    const start = performance.now()
    const tick = (now: number) => {
      const progress = Math.min((now - start) / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3)
      setValue(Math.round(target * eased))
      if (progress < 1) frame = requestAnimationFrame(tick)
    }
    frame = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(frame)
  }, [target, duration])

  return value
}

function ScoreRing({ score }: { score: number }) {
  const animatedScore = useCountUp(score)
  return <div className="score-ring" style={{ '--score': `${animatedScore * 3.6}deg` } as React.CSSProperties}><div><strong>{animatedScore}</strong><span>RISK</span></div></div>
}

const carouselSlides = [
  { image: 'https://hebbkx1anhila5yf.public.blob.vercel-storage.com/image-Aoglzt1mdX2KXdDET1REUCfZZhr4nk.png', eyebrow: 'THREAT INTELLIGENCE', title: 'See the signals before they become incidents.', text: 'Map every suspicious pattern across your digital perimeter.' },
  { image: 'https://hebbkx1anhila5yf.public.blob.vercel-storage.com/image-IFov92RXmJ9MFJVuWnuXxD3R4kkkkA.png', eyebrow: 'SECURITY OPERATIONS', title: 'One team. One clear view of risk.', text: 'Turn collaboration into faster, more confident decisions.' },
  { image: 'https://hebbkx1anhila5yf.public.blob.vercel-storage.com/image-Mf24hp8awLEroQuDfnGUlM6cz69BAp.png', eyebrow: 'INFRASTRUCTURE DEFENSE', title: 'Protect the systems that power everything.', text: 'Keep critical infrastructure visible, resilient, and ready.' },
  { image: 'https://hebbkx1anhila5yf.public.blob.vercel-storage.com/image-nh1g3kWuhr1ppPp2C2wzTQcVavtSIt.png', eyebrow: 'LIVE TELEMETRY', title: 'Every event. Prioritized in real time.', text: 'Surface the highest-risk activity without the noise.' },
  { image: 'https://hebbkx1anhila5yf.public.blob.vercel-storage.com/image-4mHzoKortyGcLdrSXicUEKE8QmUixY.png', eyebrow: 'DIGITAL SIGNALS', title: 'Track every interaction that matters.', text: 'Turn scattered activity into clear, actionable intelligence.' },
]

function SecurityCarousel() {
  const [active, setActive] = useState(0)
  const [paused, setPaused] = useState(false)

  useEffect(() => {
    if (paused) return
    const timer = window.setInterval(() => setActive((current) => (current + 1) % carouselSlides.length), 10000)
    return () => window.clearInterval(timer)
  }, [paused])

  return <section className="security-carousel" aria-label="Security capabilities" onMouseEnter={() => setPaused(true)} onMouseLeave={() => setPaused(false)} onFocus={() => setPaused(true)} onBlur={(event) => { if (!event.currentTarget.contains(event.relatedTarget)) setPaused(false) }}>
    <div className="carousel-track" style={{ transform: `translateX(-${active * 100}%)` }}>
      {carouselSlides.map((slide, index) => <article className="carousel-slide" key={slide.title} aria-hidden={active !== index}><img src={slide.image} alt="" /><div className="carousel-shade" /><div className="carousel-copy"><span>{slide.eyebrow}</span><h2>{slide.title}</h2><p>{slide.text}</p></div></article>)}
    </div>
    <div className="carousel-controls"><div className="carousel-dots" role="tablist" aria-label="Choose security capability">{carouselSlides.map((slide, index) => <button key={slide.title} className={active === index ? 'is-active' : ''} onClick={() => setActive(index)} role="tab" aria-selected={active === index} aria-label={`Show slide ${index + 1}`} />)}</div><span className="carousel-count">0{active + 1} / 05</span></div>
  </section>
}

export default function SOCDashboard() {
  const [mobileOpen, setMobileOpen] = useState(false)
  const blockedCount = useCountUp(1284)
  const detectionSeconds = useCountUp(134)
  const identityCount = useCountUp(8492)
  const [analystOpen, setAnalystOpen] = useState(false)
  const [email, setEmail] = useState('')
  const uploadInputRef = useRef<HTMLInputElement>(null)
  const [uploadedFileName, setUploadedFileName] = useState('')
  const [analyzing, setAnalyzing] = useState(false)
  const [analyzed, setAnalyzed] = useState(false)
  const [contact, setContact] = useState({ name: '', email: '', message: '' })
  const [contactSent, setContactSent] = useState(false)
  const [contactError, setContactError] = useState('')

  function submitContact(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const emailIsValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(contact.email)
    if (!contact.name.trim() || !emailIsValid || !contact.message.trim()) {
      setContactError('Please enter your name, a valid email address, and a message.')
      setContactSent(false)
      return
    }
    setContactError('')
    setContactSent(true)
  }

  const analysisLabel = useMemo(() => analyzing ? 'Running forensic pipeline' : analyzed ? 'Analysis complete' : 'Paste an email to analyze', [analyzing, analyzed])

  function runAnalysis() {
    if (!email.trim()) return
    setAnalyzing(true)
    setAnalyzed(false)
    window.setTimeout(() => { setAnalyzing(false); setAnalyzed(true) }, 1200)
  }

  return (
    <main className="home-shell">
      <div className="ambient ambient-one" /><div className="ambient ambient-two" />
      <header className="topbar">
        <a className="brand" href="#overview" aria-label="Aegis home"><BrandMark /><span>Mail Sentinel</span></a>
        <nav className={mobileOpen ? 'nav-links nav-open' : 'nav-links'} aria-label="Primary navigation">
          <Link href="/" className="active" onClick={() => setMobileOpen(false)}>Overview</Link><Link href="/dashboard" onClick={() => setMobileOpen(false)}>Dashboard</Link><Link href="/pricing" onClick={() => setMobileOpen(false)}>Pricing</Link><Link href="/about" onClick={() => setMobileOpen(false)}>About Us</Link><Link href="/signin" onClick={() => setMobileOpen(false)}>Sign in</Link>
        </nav>
        <div className="top-actions"><span className="live-status"><i /> Guest</span><button className="icon-button mobile-menu" onClick={() => setMobileOpen(!mobileOpen)} aria-label="Toggle navigation"><Menu size={18} /></button><Link className="profile-button" href="/signin" aria-label="Open profile"><img src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/image-obQs8MPF1X7LlhSZAM3UBAG3XKS0TA.png" alt="Guest profile" /></Link></div>
      </header>

      <div className="content-wrap">
        <section className="hero" id="overview">
          <div className="hero-copy"><SectionLabel>SECURITY OPERATIONS CENTER</SectionLabel><h1>See the threat<br /><em>before</em> it sees you.</h1><p>Autonomous threat intelligence and email forensics for teams who cannot afford to miss what matters.</p><div className="hero-actions"><button className="primary-button" onClick={() => document.getElementById('email-analysis')?.scrollIntoView({ behavior: 'smooth' })}>Analyze an email <ArrowUpRight size={16} /></button><button className="secondary-button" onClick={() => setAnalystOpen(true)}><Sparkles size={16} /> Ask the analyst</button></div></div>
          <div className="hero-visual"><div className="orbital"><div className="orbital-core"><Radar size={30} /><span>AEGIS<br />ONLINE</span></div><div className="orbit orbit-a" /><div className="orbit orbit-b" /><div className="signal signal-a"><AlertTriangle size={14} /><span>Threat detected</span></div><div className="signal signal-b"><Globe2 size={14} /><span>24 origins tracked</span></div></div></div>
        </section>

        <SecurityCarousel />

        <section className="metrics-grid" aria-label="Security metrics">
          <article className="metric-card featured"><div className="metric-heading"><span>Overall risk posture</span><ShieldCheck size={17} /></div><div className="metric-content"><ScoreRing score={34} /><div><strong className="metric-value">Low risk</strong><p>Down 12% from last week</p><span className="metric-trend">● Healthy baseline</span></div></div></article>
          <article className="metric-card"><div className="metric-heading"><span>Threats blocked</span><AlertTriangle size={17} /></div><strong className="metric-number metric-number-red">{blockedCount.toLocaleString()}</strong><div className="sparkline"><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /></div><p className="metric-foot">+18.4% <span>vs. previous period</span></p></article>
          <article className="metric-card"><div className="metric-heading"><span>Mean time to detect</span><Clock3 size={17} /></div><strong className="metric-number metric-number-red">{Math.floor(detectionSeconds / 60)}m {detectionSeconds % 60}s</strong><div className="progress-track"><span style={{ width: '78%' }} /></div><p className="metric-foot">78% faster <span>than industry average</span></p></article>
          <article className="metric-card"><div className="metric-heading"><span>Monitored identities</span><Fingerprint size={17} /></div><strong className="metric-number metric-number-red">{identityCount.toLocaleString()}</strong><div className="avatar-stack"><i>AL</i><i>JC</i><i>MO</i><i>+8k</i></div><p className="metric-foot">All protected <span>across 6 workspaces</span></p></article>
        </section>

        <div className="section-heading"><div><SectionLabel>LIVE TELEMETRY</SectionLabel><h2>Threat activity</h2></div><button className="filter-button">Last 24 hours <ChevronDown size={14} /></button></div>
        <section className="telemetry-grid" id="threat-map">
          <article className="panel activity-panel"><div className="panel-header"><div><h3>Detection volume</h3><p>Events aggregated from 42 sources</p></div><span className="live-pill"><i /> Live</span></div><div className="chart"><div className="chart-y"><span>400</span><span>300</span><span>200</span><span>100</span><span>0</span></div><div className="chart-area"><div className="grid-lines" /><svg viewBox="0 0 700 210" preserveAspectRatio="none" aria-label="Detection volume chart" role="img"><defs><linearGradient id="area" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stopColor="#7674ff" stopOpacity=".36" /><stop offset="1" stopColor="#7674ff" stopOpacity="0" /></linearGradient></defs><path d="M0 174 C30 160, 48 170, 72 144 S110 142, 135 151 S168 104, 197 128 S235 126, 258 91 S292 100, 315 112 S350 62, 380 87 S415 112, 441 75 S469 103, 495 56 S530 74, 557 87 S585 36, 617 54 S653 28, 700 38 L700 210 L0 210Z" fill="url(#area)" pathLength="1" /><path d="M0 174 C30 160, 48 170, 72 144 S110 142, 135 151 S168 104, 197 128 S235 126, 258 91 S292 100, 315 112 S350 62, 380 87 S415 112, 441 75 S469 103, 495 56 S530 74, 557 87 S585 36, 617 54 S653 28, 700 38" fill="none" stroke="#8583ff" strokeWidth="2" pathLength="1" /></svg><div className="chart-x"><span>00:00</span><span>04:00</span><span>08:00</span><span>12:00</span><span>Now</span></div></div></div></article>
          <article className="panel threat-list"><div className="panel-header"><div><h3>Latest detections</h3><p>Prioritized by Aegis risk engine</p></div><button className="text-button">View all <ArrowUpRight size={14} /></button></div><div className="detection-table">{threats.map((threat) => <div className="detection-row" key={threat.time}><span className={`severity-dot ${threat.severity.toLowerCase()}`} /><div className="detection-main"><strong>{threat.type}</strong><span>{threat.source}</span></div><span className="country">{threat.country}</span><span className={`severity-text ${threat.severity.toLowerCase()}`}>{threat.severity}</span><time>{threat.time}</time></div>)}</div></article>
        </section>

        <section className="analysis-section" id="email-analysis"><div className="section-heading"><div><SectionLabel>FORENSIC ANALYSIS</SectionLabel><h2>Inspect the signal.</h2></div><span className="analysis-status"><CircleDot size={15} /> {analysisLabel}</span></div><div className="analysis-grid"><article className="panel email-drop"><div className="drop-icon"><Mail size={24} /></div><h3>Analyze a suspicious email</h3><p>Paste raw headers or upload an .eml file. Aegis will trace sender intent, infrastructure, and every linked indicator.</p><textarea value={email} onChange={(event) => setEmail(event.target.value)} placeholder="Paste email content or headers here..." aria-label="Email content" /><div className="drop-actions"><button className="primary-button" onClick={() => { if (email.trim()) runAnalysis(); window.location.href = '/dashboard/email-analysis' }} disabled={analyzing}>{analyzing ? 'Analyzing...' : 'Run analysis'} <ArrowUpRight size={16} /></button><input ref={uploadInputRef} className="file-input-hidden" type="file" accept=".eml,.txt" onChange={(event) => { const file = event.target.files?.[0]; if (!file) return; setUploadedFileName(file.name); const reader = new FileReader(); reader.onload = () => setEmail(String(reader.result ?? '')); reader.readAsText(file) }} /><button className="upload-button" type="button" onClick={() => uploadInputRef.current?.click()}><Upload size={15} /> {uploadedFileName || 'Upload .eml'}</button></div></article><article className="panel pipeline"><div className="panel-header"><div><h3>Analysis pipeline</h3><p>Deep inspection across 7 layers</p></div><FileSearch size={19} /></div><div className="pipeline-list">{['Header authentication', 'Sender reputation', 'URL & attachment detonation', 'Threat graph correlation', 'AI verdict'].map((stage, index) => <div className={`pipeline-stage ${analyzed && index < 5 ? 'complete' : analyzing && index === 2 ? 'scanning' : ''}`} key={stage}><span className="stage-check">{analyzed && index < 5 ? <Check size={13} /> : analyzing && index === 2 ? <Activity size={13} /> : index + 1}</span><div><strong>{stage}</strong><small>{analyzed && index < 5 ? index === 4 ? 'High confidence phishing' : 'Verified successfully' : analyzing && index === 2 ? 'Scanning indicators...' : 'Awaiting input'}</small></div></div>)}</div></article></div></section>

        <section className="contact-section" id="contact"><div className="section-heading"><div><SectionLabel>DIRECT LINE</SectionLabel><h2>Contact us</h2></div><p className="contact-intro">For commissions, project inquiries, or security questions, send a message to the Mail Sentinel team.</p></div><form className="contact-form" onSubmit={submitContact} noValidate><label>Name<input value={contact.name} onChange={(event) => setContact({ ...contact, name: event.target.value })} placeholder="Your name" required /></label><label>Email<input type="email" value={contact.email} onChange={(event) => setContact({ ...contact, email: event.target.value })} placeholder="you@company.com" required /></label><label className="contact-message">Message<textarea value={contact.message} onChange={(event) => setContact({ ...contact, message: event.target.value })} placeholder="Tell us how we can help..." required minLength={10} /></label><div className="contact-submit"><button className="primary-button" type="submit">Submit <ArrowUpRight size={16} /></button>{contactError && <p className="contact-error" role="alert">{contactError}</p>}{contactSent && <p className="contact-success" role="status">Your message is sent to administrator. Thank You !</p>}</div></form></section>
        <footer className="home-footer"><div><a className="brand" href="#overview"><BrandMark /><span>Mail Sentinel</span></a><p>Built for the teams defending what matters.</p></div><div className="social-links" aria-label="Social media links"><a href="https://wa.me/15551234567" target="_blank" rel="noreferrer" aria-label="WhatsApp"><MessageCircle size={17} /></a><a href="https://github.com" target="_blank" rel="noreferrer" aria-label="GitHub"><GitBranch size={17} /></a><a href="https://linkedin.com" target="_blank" rel="noreferrer" aria-label="LinkedIn"><BriefcaseBusiness size={17} /></a><a href="https://x.com" target="_blank" rel="noreferrer" aria-label="X"><AtSign size={17} /></a><a href="https://youtube.com" target="_blank" rel="noreferrer" aria-label="YouTube"><PlaySquare size={17} /></a></div><small>© 2025 Aegis Security Systems</small></footer>
      </div>

      <button className="analyst-fab" onClick={() => setAnalystOpen(true)} aria-label="Open AI SOC analyst"><Sparkles size={21} /><span>AI analyst</span></button>
      <AIChatDrawer open={analystOpen} onClose={() => setAnalystOpen(false)} />
    </main>
  )
}
