'use client'

import { useEffect } from 'react'

export function CursorSpotlight() {
  useEffect(() => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches || !window.matchMedia('(pointer: fine)').matches) return

    let frame = 0
    let x = window.innerWidth * 0.5
    let y = window.innerHeight * 0.35
    let nextX = x
    let nextY = y

    const render = () => {
      x += (nextX - x) * 0.14
      y += (nextY - y) * 0.14
      document.documentElement.style.setProperty('--cursor-x', `${x}px`)
      document.documentElement.style.setProperty('--cursor-y', `${y}px`)
      frame = requestAnimationFrame(render)
    }

    const handlePointerMove = (event: PointerEvent) => {
      nextX = event.clientX
      nextY = event.clientY
    }

    window.addEventListener('pointermove', handlePointerMove, { passive: true })
    frame = requestAnimationFrame(render)

    return () => {
      window.removeEventListener('pointermove', handlePointerMove)
      cancelAnimationFrame(frame)
    }
  }, [])

  return <div className="cursor-spotlight" aria-hidden="true" />
}
