import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { dataService } from '../services/dataService'
import type { LeagueConfig } from '../types/handball'

interface LeagueContextType {
  leagues: LeagueConfig[]
  selectedLeague: LeagueConfig | null
  setSelectedLeague: (league: LeagueConfig) => void
  loading: boolean
  error: string | null
}

const LeagueContext = createContext<LeagueContextType | undefined>(undefined)

interface LeagueProviderProps {
  children: ReactNode
}

export const LeagueProvider = ({ children }: LeagueProviderProps) => {
  const [leagues, setLeagues] = useState<LeagueConfig[]>([])
  const [selectedLeague, setSelectedLeague] = useState<LeagueConfig | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadLeagues = async () => {
      try {
        setLoading(true)
        const fetchedLeagues = await dataService.getLeagues()
        setLeagues(fetchedLeagues)
        if (fetchedLeagues.length > 0) {
          setSelectedLeague(fetchedLeagues[0])
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load leagues')
      } finally {
        setLoading(false)
      }
    }

    loadLeagues()
  }, [])

  const value = {
    leagues,
    selectedLeague,
    setSelectedLeague,
    loading,
    error
  }

  return (
    <LeagueContext.Provider value={value}>
      {children}
    </LeagueContext.Provider>
  )
}

export const useLeague = () => {
  const context = useContext(LeagueContext)
  if (context === undefined) {
    throw new Error('useLeague must be used within a LeagueProvider')
  }
  return context
}
