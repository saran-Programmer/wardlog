import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { getMe } from '../api/users'
import type { UserResponse } from '../types/auth'

interface UserContextValue {
  user: UserResponse | null
  isLoading: boolean
  setUser: (user: UserResponse) => void
}

const UserContext = createContext<UserContextValue | undefined>(undefined)

export function UserProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    getMe()
      .then(setUser)
      .catch((err) => console.error('Failed to load user profile', err))
      .finally(() => setIsLoading(false))
  }, [])

  return <UserContext.Provider value={{ user, isLoading, setUser }}>{children}</UserContext.Provider>
}

export function useUser(): UserContextValue {
  const context = useContext(UserContext)
  if (!context) {
    throw new Error('useUser must be used within a UserProvider')
  }
  return context
}
