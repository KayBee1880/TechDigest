import { useState, type ReactNode } from 'react'
import type { User } from '../api/types'
import { AuthContext, TOKEN_KEY, USER_KEY } from './auth-context'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_KEY))
  const [user, setUser] = useState<User | null>(() => {
    const stored = localStorage.getItem(USER_KEY)
    return stored ? (JSON.parse(stored) as User) : null
  })

  function setSession(newUser: User, newToken: string) {
    setUser(newUser)
    setToken(newToken)
    localStorage.setItem(TOKEN_KEY, newToken)
    localStorage.setItem(USER_KEY, JSON.stringify(newUser))
  }

  function clearSession() {
    setUser(null)
    setToken(null)
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  }

  return (
    <AuthContext.Provider value={{ user, token, setSession, clearSession }}>
      {children}
    </AuthContext.Provider>
  )
}

