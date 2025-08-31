// Petronas Green and Cyan color palette
export const PETRONAS_COLORS = {
  // Primary Petronas Green shades
  GREEN: {
    50: '#f0fdf9',   // Very light mint
    100: '#ccfdf7',  // Light mint
    200: '#99f8e7',  // Light cyan-green
    300: '#5eead4',  // Medium cyan-green
    400: '#2dd4bf',  // Bright cyan-green
    500: '#14b8a6',  // Primary Petronas green
    600: '#0d9488',  // Dark Petronas green
    700: '#0f766e',  // Darker green
    800: '#115e59',  // Very dark green
    900: '#134e4a',  // Deepest green
  },
  // Complementary Cyan shades
  CYAN: {
    50: '#ecfeff',   // Very light cyan
    100: '#cffafe',  // Light cyan
    200: '#a5f3fc',  // Light blue-cyan
    300: '#67e8f9',  // Medium cyan
    400: '#22d3ee',  // Bright cyan
    500: '#06b6d4',  // Primary cyan
    600: '#0891b2',  // Dark cyan
    700: '#0e7490',  // Darker cyan
    800: '#155e75',  // Very dark cyan
    900: '#164e63',  // Deepest cyan
  },
  // Supporting colors
  ACCENT: {
    TEAL: '#14b8a6',     // Primary accent
    EMERALD: '#10b981',  // Secondary accent
    MINT: '#6ee7b7',     // Light accent
  }
} as const

// Brand gradients using Petronas colors
export const BRAND_GRADIENTS = {
  PRIMARY: `linear-gradient(135deg, ${PETRONAS_COLORS.CYAN[500]} 0%, ${PETRONAS_COLORS.GREEN[600]} 100%)`,
  SECONDARY: `linear-gradient(135deg, ${PETRONAS_COLORS.GREEN[400]} 0%, ${PETRONAS_COLORS.CYAN[400]} 100%)`,
  ACCENT: `linear-gradient(135deg, ${PETRONAS_COLORS.GREEN[500]} 0%, ${PETRONAS_COLORS.GREEN[700]} 100%)`,
  LIGHT: `linear-gradient(135deg, ${PETRONAS_COLORS.GREEN[100]} 0%, ${PETRONAS_COLORS.CYAN[100]} 100%)`,
  DARK: `linear-gradient(135deg, ${PETRONAS_COLORS.GREEN[800]} 0%, ${PETRONAS_COLORS.CYAN[800]} 100%)`,
} as const