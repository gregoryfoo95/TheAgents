import React, { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'

interface UseLayoutStateReturn {
  mobileOpen: boolean
  anchorEl: HTMLElement | null
  handleDrawerToggle: () => void
  handleProfileMenuOpen: (event: React.MouseEvent<HTMLElement>) => void
  handleProfileMenuClose: () => void
  handleLogout: (logoutFn: () => void) => void
}

export const useLayoutState = (): UseLayoutStateReturn => {
  const navigate = useNavigate()
  const [mobileOpen, setMobileOpen] = useState<boolean>(false)
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null)

  const handleDrawerToggle = useCallback(() => {
    setMobileOpen(prev => !prev)
  }, [])

  const handleProfileMenuOpen = useCallback((event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget)
  }, [])

  const handleProfileMenuClose = useCallback(() => {
    setAnchorEl(null)
  }, [])

  const handleLogout = useCallback((logoutFn: () => void) => {
    logoutFn()
    navigate('/')
    setAnchorEl(null)
  }, [navigate])

  return {
    mobileOpen,
    anchorEl,
    handleDrawerToggle,
    handleProfileMenuOpen,
    handleProfileMenuClose,
    handleLogout,
  }
}