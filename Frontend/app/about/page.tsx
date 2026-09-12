import Link from 'next/link'
import { ArrowLeft, ArrowUpRight, GitBranch, BriefcaseBusiness, Sparkles } from 'lucide-react'

const team = [
  { name: 'Arjun Mehta', role: 'Security Engineering', image: '/team-arjun.png', contribution: 'Detection engine & threat graph', bio: 'Arjun designed the forensic pipeline that turns messy email artifacts into clear, explainable signals for security teams.', github: 'https://github.com', linkedin: 'https://linkedin.com' },
  { name: 'Maya Chen', role: 'Product & Research', image: '/team-maya.png', contribution: 'Analyst experience & research', bio: 'Maya shaped the calm, focused workspace and led the research behind Aegis\' human-centered investigation flows.', github: 'https://github.com', linkedin: 'https://linkedin.com' },
]

export default function AboutPage() {
  return <main className="about-shell">
    <header className="about-nav"><Link className="brand" href="/"><img className="brand-logo" src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/image-gDrpBHhVlVUcfGTYoG8zp5E1qldTaP.png" alt="Mail Sentinel logo" /><span>Mail Sentinel</span></Link><Link className="about-back" href="/"><ArrowLeft size={14} /> Back to overview</Link></header>
    <section className="about-hero"><span className="about-kicker"><Sparkles size={13} /> THE PEOPLE BEHIND THE SIGNAL</span><h1>Built by people who<br /><em>care about clarity.</em></h1><p>We started Aegis after watching capable teams drown in noisy alerts. Our journey is about making security intelligence feel focused, explainable, and human.</p></section>
    <section className="journey-section"><div className="section-label"><span className="label-line" /> OUR JOURNEY <span className="label-line" /></div><div className="journey-grid"><article><strong>01</strong><h2>See the signal</h2><p>We began with one question: what if every alert came with the context needed to act?</p></article><article><strong>02</strong><h2>Connect the dots</h2><p>We built a forensic system that links senders, infrastructure, identities, and intent in one view.</p></article><article><strong>03</strong><h2>Give time back</h2><p>Today, Aegis helps modern teams move from uncertainty to confident action without the noise.</p></article></div></section>
    <section className="team-section"><div className="section-label"><span className="label-line" /> THE FOUNDING TEAM <span className="label-line" /></div><div className="team-grid">{team.map((person) => <article className="team-card" key={person.name}><img src={person.image} alt={`${person.name}, ${person.role}`} /><div className="team-copy"><span className="about-kicker">{person.role}</span><h2>{person.name}</h2><strong>{person.contribution}</strong><p>{person.bio}</p><div className="team-links"><a href={person.github} target="_blank" rel="noreferrer" aria-label={`${person.name} on GitHub`}><GitBranch size={16} /> GitHub</a><a href={person.linkedin} target="_blank" rel="noreferrer" aria-label={`${person.name} on LinkedIn`}><BriefcaseBusiness size={16} /> LinkedIn</a></div></div><ArrowUpRight className="team-arrow" size={17} /></article>)}</div></section>
    <footer className="about-footer"><span>Mail Sentinel</span><span>Defending what matters, together.</span><Link href="/signin">Join the workspace <ArrowUpRight size={14} /></Link></footer>
  </main>
}
