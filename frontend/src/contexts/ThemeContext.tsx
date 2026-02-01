import { createContext, useContext, useState, useEffect } from 'react'
import type { ReactNode } from 'react'

export type ThemeType = 'light' | 'dark'

interface ThemeContextType {
  theme: ThemeType
  toggleTheme: () => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

interface ThemeProviderProps {
  children: ReactNode
}

export const ThemeProvider = ({ children }: ThemeProviderProps) => {
  const [theme, setTheme] = useState<ThemeType>('light')

  useEffect(() => {
    console.log('[ThemeProvider] Effect running');
    
    // Check for saved theme preference or system preference
    const savedTheme = localStorage.getItem('theme') as ThemeType
    console.log('[ThemeProvider] Saved theme:', savedTheme);
    
    if (savedTheme && (savedTheme === 'light' || savedTheme === 'dark')) {
      console.log('[ThemeProvider] Using saved theme:', savedTheme);
      setTheme(savedTheme)
      updateTheme(savedTheme)
    } else {
      // Use system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      const systemTheme = prefersDark ? 'dark' : 'light'
      console.log('[ThemeProvider] Using system theme:', systemTheme);
      setTheme(systemTheme)
      updateTheme(systemTheme)
    }
  }, [])

  const updateTheme = (newTheme: ThemeType) => {
    console.log('[updateTheme] Setting theme to:', newTheme);
    const html = document.documentElement
    console.log('[updateTheme] HTML element before:', html.className);
    
    if (newTheme === 'dark') {
      html.classList.add('dark')
    } else {
      html.classList.remove('dark')
    }
    
    console.log('[updateTheme] HTML element after:', html.className);
    console.log('[updateTheme] Computed background:', window.getComputedStyle(document.body).backgroundColor);
  }

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark'
    console.log('[toggleTheme] Switching from', theme, 'to', newTheme);
    setTheme(newTheme)
    localStorage.setItem('theme', newTheme)
    updateTheme(newTheme)
  }

  const value = {
    theme,
    toggleTheme
  }

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  )
}

export const useTheme = () => {
  const context = useContext(ThemeContext)
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}
