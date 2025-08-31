import React, { useState, useEffect, useCallback } from 'react'
import { Box, useTheme } from '@mui/material'
import { SmartToy as RobotIcon } from '@mui/icons-material'
import { MASCOT_ANIMATIONS, ANIMATION_CONFIG } from '../constants/homepage'
import { PETRONAS_COLORS } from '../constants/colors'

interface MascotPosition {
  x: number
  y: number
}

export const AnimatedMascot: React.FC = () => {
  const [position, setPosition] = useState<MascotPosition>({ x: 20, y: 20 })
  const [animation, setAnimation] = useState<string>('bounce')
  const [clickCount, setClickCount] = useState<number>(0)
  const theme = useTheme()

  const getRandomPosition = useCallback((): MascotPosition => ({
    x: Math.random() * 70 + 10, // 10% to 80% from left
    y: Math.random() * 50 + 15, // 15% to 65% from top
  }), [])

  const getRandomAnimation = useCallback((): string => {
    return MASCOT_ANIMATIONS[Math.floor(Math.random() * MASCOT_ANIMATIONS.length)]
  }, [])

  // Random movement and animation changes
  useEffect(() => {
    const moveInterval = setInterval(() => {
      setPosition(getRandomPosition())
      setAnimation(getRandomAnimation())
    }, ANIMATION_CONFIG.MOVE_INTERVAL_BASE + Math.random() * ANIMATION_CONFIG.MOVE_INTERVAL_RANDOM)
    
    return () => clearInterval(moveInterval)
  }, [getRandomPosition, getRandomAnimation])

  // Initial random position
  useEffect(() => {
    setPosition(getRandomPosition())
  }, [getRandomPosition])

  const handleClick = useCallback(() => {
    setClickCount(prev => prev + 1)
    setPosition(getRandomPosition())
    setAnimation('jump')
    
    // Special effects for multiple clicks
    if (clickCount >= ANIMATION_CONFIG.CLICK_THRESHOLD) {
      setAnimation('wiggle')
      setClickCount(0)
    }
  }, [clickCount, getRandomPosition])

  return (
    <Box
      className={`robot-mascot ${animation}`}
      sx={{
        position: 'absolute',
        left: `${position.x}%`,
        top: `${position.y}%`,
        transition: `left ${ANIMATION_CONFIG.TRANSITION_DURATION} ease-in-out, top ${ANIMATION_CONFIG.TRANSITION_DURATION} ease-in-out`,
        cursor: 'pointer',
        zIndex: 2,
      }}
      onClick={handleClick}
      title={`Click me! I'm your AI assistant! (Clicks: ${clickCount})`}
    >
      <RobotIcon
        sx={{
          fontSize: { xs: 50, md: 60 },
          color: '#ffffff',
          background: clickCount >= 3 
            ? `linear-gradient(135deg, ${PETRONAS_COLORS.CYAN[400]}, ${PETRONAS_COLORS.GREEN[400]})` 
            : `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
          borderRadius: '50%',
          padding: 2,
          boxShadow: clickCount >= 3 
            ? `0 8px 24px ${theme.palette.mode === 'light' ? 'rgba(6, 182, 212, 0.6)' : 'rgba(6, 182, 212, 0.8)'}` 
            : `0 8px 24px ${theme.palette.mode === 'light' ? 'rgba(20, 184, 166, 0.4)' : 'rgba(20, 184, 166, 0.6)'}`,
          border: `3px solid ${theme.palette.mode === 'light' ? 'rgba(255, 255, 255, 0.3)' : 'rgba(255, 255, 255, 0.2)'}`,
          transition: 'all 0.3s ease',
          '&:hover': {
            transform: 'scale(1.1) rotate(5deg)',
          },
        }}
      />
    </Box>
  )
}