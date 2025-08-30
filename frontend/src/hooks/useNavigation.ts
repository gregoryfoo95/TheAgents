import { useMemo } from 'react'
import { User } from '../types'
import { NavigationItem } from '../components/Navigation'
import { PUBLIC_NAVIGATION, USER_NAVIGATION, AGENT_NAVIGATION } from '../constants/navigation'

interface UseNavigationReturn {
  publicNavigation: NavigationItem[]
  userNavigation: NavigationItem[]
}

export const useNavigation = (user: User | null): UseNavigationReturn => {
  const publicNavigation = useMemo(() => PUBLIC_NAVIGATION, [])
  
  const userNavigation = useMemo(() => {
    if (!user) return []
    
    const baseUserNavigation = [...USER_NAVIGATION]
    
    if (user.user_type === 'agent') {
      baseUserNavigation.push(...AGENT_NAVIGATION)
    }
    
    return baseUserNavigation
  }, [user?.user_type])

  return {
    publicNavigation,
    userNavigation,
  }
}