'use client'

import { useSyncExternalStore } from 'react'
import { clearAuth, hasAccessToken } from '@/lib/api'

let authenticated = false
const listeners = new Set<() => void>()
const emit = () => listeners.forEach((listener) => listener())

export function refreshAuthState() {
  authenticated = hasAccessToken()
  emit()
}

export function setAuthenticated(value: boolean) {
  authenticated = value
  emit()
}

export function signOutLocal() {
  clearAuth()
  setAuthenticated(false)
}

export function useAuth() {
  return useSyncExternalStore(
    (listener) => {
      listeners.add(listener)
      return () => listeners.delete(listener)
    },
    () => authenticated,
    () => false,
  )
}
