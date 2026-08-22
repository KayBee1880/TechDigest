import { createContext } from 'react'
import type { User } from '../api/types'

export const TOKEN_KEY = 'techdigest_token'
export const USER_KEY = 'techdigest_user'

export interface AuthContextValue {
  user: User | null
  token: string | null
  setSession: (user: User, token: string) => void
  clearSession: () => void
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined)
