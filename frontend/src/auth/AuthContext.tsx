import { createContext, useContext, useState, type ReactNode } from 'react'
import type { User } from '../api/types'

const TOKEN_KEY = 'techdigest_token'
const USER_KEY = 'techdigest_user'

interface AuthContextValue {
  user: User | null
  token: string | null
  setSession: (user: User, token: string) => void
  clearSession: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

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

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
