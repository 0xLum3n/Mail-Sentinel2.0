'use client'

import { useEffect, type ReactNode } from 'react'

export default function Template({ children }: { children: ReactNode }) {
  useEffect(() => {
    const root = document.documentElement
    let frame = 0
    let currentX = window.innerWidth * 0.5
    let currentY = window.innerHeight * 0.35
    let targetX = currentX
    let targetY = currentY
    const render = () => {
      currentX += (targetX - currentX) * 0.16
      currentY += (targetY - currentY) * 0.16
      root.style.setProperty('--cursor-x', `${currentX}px`)
      root.style.setProperty('--cursor-y', `${currentY}px`)
      frame = requestAnimationFrame(render)
    }
    const handlePointerMove = (event: PointerEvent) => {
      targetX = event.clientX
      targetY = event.clientY
    }
    window.addEventListener('pointermove', handlePointerMove, { passive: true })
    frame = requestAnimationFrame(render)
    return () => {
      window.removeEventListener('pointermove', handlePointerMove)
      cancelAnimationFrame(frame)
    }
  }, [])

  return (
    <div className="page-transition">
      <div className="cursor-glow" aria-hidden="true" />
      <div className="page-content">{children}</div>
    </div>
  )
}
