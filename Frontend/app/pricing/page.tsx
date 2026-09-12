'use client'

import Link from 'next/link'
import { ArrowRight, Check, Shield } from 'lucide-react'
import { useState } from 'react'

const plans = [
  { name: 'Signal', price: '$49', description: 'For lean teams building a serious security practice.', features: ['3 workspaces', 'Email forensics', '7-day event retention', 'AI analyst summaries'] },
  { name: 'Sentinel', price: '$149', description: 'For security teams that need full situational awareness.', features: ['Unlimited workspaces', 'Live threat telemetry', '90-day event retention', 'Investigation case management'], featured: true },
  { name: 'Command', price: 'Custom', description: 'For organizations with complex environments and compliance needs.', features: ['Everything in Sentinel', 'Custom retention policies', 'Priority response workflows', 'Dedicated security advisor'] },
]

export default function PricingPage() {
  const [selected, setSelected] = useState('Sentinel')
  return <main className="subpage-shell"><header className="topbar"><Link className="brand" href="/"><img className="brand-logo" src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/image-gDrpBHhVlVUcfGTYoG8zp5E1qldTaP.png" alt="Mail Sentinel logo" /><span>Mail Sentinel</span></Link><nav className="nav-links"><Link href="/">Overview</Link><Link href="/dashboard">Dashboard</Link><Link href="/pricing" className="active">Pricing</Link><Link href="/signin">Sign in</Link></nav><Link className="secondary-button" href="/signin">Get started <ArrowRight size={14} /></Link></header><section className="subpage-hero"><span className="eyebrow"><Shield size={14} /> SIMPLE, PREDICTABLE COVERAGE</span><h1>Choose the layer<br /><em>your team needs.</em></h1><p>Start with the signals that matter, then expand into a complete security operations command center.</p></section><section className="pricing-grid">{plans.map((plan) => <article className={`price-card ${plan.featured ? 'featured' : ''}`} key={plan.name}><div className="price-top"><span className="plan-kicker">{plan.featured ? 'MOST POPULAR' : 'AEGIS / PLAN'}</span><h2>{plan.name}</h2><p>{plan.description}</p><strong>{plan.price}{plan.price !== 'Custom' && <small>/ month</small>}</strong></div><ul>{plan.features.map((feature) => <li key={feature}><Check size={15} />{feature}</li>)}</ul><button className={plan.featured ? 'primary-button' : 'secondary-button'} onClick={() => setSelected(plan.name)}>{selected === plan.name ? 'Selected' : `Choose ${plan.name}`} <ArrowRight size={14} /></button></article>)}</section><p className="pricing-note">All plans include encrypted workspaces, role-based access, and a 14-day evaluation. <Link href="/signin">Create your account</Link> to begin.</p></main>
}
