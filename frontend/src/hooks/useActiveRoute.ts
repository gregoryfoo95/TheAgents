import { useCallback } from 'react'
import { useLocation } from 'react-router-dom'

interface UseActiveRouteReturn {
  isActive: (href: string) => boolean
}

export const useActiveRoute = (): UseActiveRouteReturn => {
  const location = useLocation()

  const isActive = useCallback((href: string): boolean => {
    if (href === '/') return location.pathname === '/'
    return location.pathname.startsWith(href)
  }, [location.pathname])

  return { isActive }
}