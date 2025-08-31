// Logo.tsx
import React, { useId, useMemo } from 'react'

interface LogoProps {
  width?: number
  height?: number
  className?: string
  animate?: boolean
  lightOnDark?: boolean  // set true if your header/bg is dark
}

export const Logo: React.FC<LogoProps> = ({
  width = 256,
  height = 256,
  className,
  animate = true,
  lightOnDark = false,
}) => {
  // Base path (visible ring uses this; motion path references same d)
  const ORBIT_D =
    'M56 152c24-38 74-58 116-46 32 10 38 30 26 46-18 24-74 46-120 32'

  // Unique IDs so multiple <Logo/> don’t clash
  const rid = useId()
  const uid = useMemo(() => rid.replace(/:/g, ''), [rid])
  const gradId = `brandGradient-${uid}`
  const qGradId = `qubitGradient-${uid}`
  const shadowId = `logoShadow-${uid}`
  const mpathId = `mpath-${uid}`

  // Scale orbit stroke for tiny sizes
  const baseStroke = 10
  const scale = Math.min(width, height) / 256
  const strokeWidth = Math.max(2, Math.round(baseStroke * scale))

  // Color for the “A”
  const aFill = lightOnDark ? '#FFFFFF' : '#0B1020'
  const vectorFill = lightOnDark ? '#0B1020' : '#FFFFFF' // for the small state vector tip

  return (
    <svg
      width={width}
      height={height}
      viewBox="0 0 256 256"
      xmlns="http://www.w3.org/2000/svg"
      role="img"
      aria-label="Agent logo with orbiting quantum qubit"
      className={className}
      preserveAspectRatio="xMidYMid meet"
    >
      <defs>
        <linearGradient id={gradId} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#22C55E" />
          <stop offset="1" stopColor="#22D3EE" />
        </linearGradient>

        <radialGradient id={qGradId} cx="50%" cy="40%" r="70%">
          <stop offset="0" stopColor="#22D3EE" />
          <stop offset="1" stopColor="#22C55E" />
        </radialGradient>

        <filter id={shadowId} x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="0" dy="2" stdDeviation="3" floodOpacity="0.25" />
        </filter>

        {/* Motion path for animateMotion */}
        <path id={mpathId} d={ORBIT_D} />
      </defs>

      {/* The bold A */}
      <path
        d="M128 40c6 0 11 3 13 9l77 168a12 12 0 0 1-11 17h-34a12 12 0 0 1-11-7l-15-34H109l-15 34a12 12 0 0 1-11 7H49a12 12 0 0 1-11-17l77-168c2-6 7-9 13-9zm-18 108h36l-18-41-18 41z"
        fill={aFill}
        filter={`url(#${shadowId})`}
      />

      {/* Visible orbit ring */}
      <path
        d={ORBIT_D}
        fill="none"
        stroke={`url(#${gradId})`}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeDasharray="180 40"
      />

      {/* Qubit group (either animated along the path or placed at start) */}
      <g>
        <g transform="translate(192,120)">
          {/* We start the qubit at a visible point; animateMotion will override its position when enabled */}
          {/* Sphere */}
          <circle r="12" fill={`url(#${qGradId})`} />
          <circle
            r="12"
            fill="none"
            stroke="#FFFFFF"
            strokeOpacity="0.25"
            strokeWidth={1}
          />
          {/* Equator (tilted) */}
          <ellipse
            rx="9"
            ry="5"
            fill="none"
            stroke="#FFFFFF"
            strokeOpacity="0.55"
            strokeWidth={1.5}
            transform="rotate(-15)"
          />
          {/* Meridian */}
          <path
            d="M0 -9.5 A 9.5 9.5 0 1 0 0 9.5"
            fill="none"
            stroke="#FFFFFF"
            strokeOpacity="0.35"
            strokeWidth={1.2}
          />
          {/* State vector (|ψ⟩) */}
          <g transform="rotate(-35)">
            <line
              x1="0"
              y1="0"
              x2="9"
              y2="-3"
              stroke={aFill}
              strokeWidth={2}
              strokeLinecap="round"
            />
            <circle cx="9" cy="-3" r="1.9" fill={aFill === '#FFFFFF' ? vectorFill : '#0B1020'} />
          </g>

          {/* Gentle spin */}
          {animate && (
            <animateTransform
              attributeName="transform"
              type="rotate"
              from="0"
              to="360"
              dur="6s"
              repeatCount="indefinite"
            />
          )}
        </g>

        {/* Orbit motion */}
        {animate && (
          <animateMotion dur="3.2s" repeatCount="indefinite" rotate="auto">
            <mpath xlinkHref={`#${mpathId}`} href={`#${mpathId}`} />
          </animateMotion>
        )}
      </g>
    </svg>
  )
}
