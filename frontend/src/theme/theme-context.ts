import { createContext } from 'react'

export type Theme = 'light' | 'dark'

export const THEME_KEY = 'techdigest_theme'

export interface ThemeContextValue {
  theme: Theme
  toggleTheme: () => void
}

export const ThemeContext = createContext<ThemeContextValue | undefined>(undefined)
