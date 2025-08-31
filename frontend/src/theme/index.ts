import { createTheme, ThemeOptions, PaletteMode } from '@mui/material/styles'
import { PETRONAS_COLORS, BRAND_GRADIENTS } from '../constants/colors'

// Define custom theme colors
declare module '@mui/material/styles' {
  interface Palette {
    tertiary: Palette['primary']
  }

  interface PaletteOptions {
    tertiary?: PaletteOptions['primary']
  }
}

const getThemeOptions = (mode: PaletteMode): ThemeOptions => ({
  palette: {
    mode,
    primary: {
      main: PETRONAS_COLORS.GREEN[500], // Primary Petronas green
      light: PETRONAS_COLORS.GREEN[400], // Lighter green
      dark: PETRONAS_COLORS.GREEN[600], // Darker green
      contrastText: '#ffffff',
    },
    secondary: {
      main: PETRONAS_COLORS.CYAN[500], // Primary cyan
      light: PETRONAS_COLORS.CYAN[400], // Lighter cyan
      dark: PETRONAS_COLORS.CYAN[600], // Darker cyan
      contrastText: '#ffffff',
    },
    tertiary: {
      main: PETRONAS_COLORS.ACCENT.TEAL, // Accent teal
      light: PETRONAS_COLORS.ACCENT.MINT, // Light mint
      dark: PETRONAS_COLORS.GREEN[700], // Dark green
      contrastText: '#ffffff',
    },
    background: {
      default: mode === 'light' ? PETRONAS_COLORS.GREEN[50] : '#0a1e1b', // Very light mint / Very dark green
      paper: mode === 'light' ? '#ffffff' : '#134e4a', // White / Deep green
    },
    text: {
      primary: mode === 'light' ? PETRONAS_COLORS.GREEN[900] : PETRONAS_COLORS.GREEN[50], // Deep green / Light mint
      secondary: mode === 'light' ? PETRONAS_COLORS.GREEN[700] : PETRONAS_COLORS.GREEN[200], // Dark green / Light green
    },
    divider: mode === 'light' ? PETRONAS_COLORS.GREEN[200] : PETRONAS_COLORS.GREEN[700], // Light green / Dark green
    ...(mode === 'dark' && {
      action: {
        hover: 'rgba(255, 255, 255, 0.08)',
        selected: 'rgba(255, 255, 255, 0.12)',
      },
    }),
  },
  typography: {
    fontFamily: [
      'Inter',
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
    h1: {
      fontSize: '3rem',
      fontWeight: 800,
      lineHeight: 1.1,
    },
    h2: {
      fontSize: '2.25rem',
      fontWeight: 700,
      lineHeight: 1.2,
    },
    h3: {
      fontSize: '1.875rem',
      fontWeight: 600,
      lineHeight: 1.3,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 600,
      lineHeight: 1.4,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 500,
      lineHeight: 1.5,
    },
    h6: {
      fontSize: '1.125rem',
      fontWeight: 500,
      lineHeight: 1.6,
    },
  },
  shape: {
    borderRadius: 8,
  },
  spacing: 8,
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
          borderRadius: 8,
          padding: '10px 20px',
        },
        contained: {
          boxShadow: 'none',
          '&:hover': {
            boxShadow: mode === 'light' 
              ? '0 4px 8px rgba(0, 0, 0, 0.12)' 
              : '0 4px 8px rgba(0, 0, 0, 0.3)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: mode === 'light' 
            ? '0 1px 3px rgba(0, 0, 0, 0.1)' 
            : '0 4px 6px rgba(0, 0, 0, 0.3)',
          '&:hover': {
            boxShadow: mode === 'light' 
              ? '0 4px 12px rgba(0, 0, 0, 0.15)' 
              : '0 8px 16px rgba(0, 0, 0, 0.4)',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
            ...(mode === 'dark' && {
              backgroundColor: 'rgba(255, 255, 255, 0.05)',
            }),
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 6,
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: mode === 'light' 
            ? 'rgba(255, 255, 255, 0.95)' 
            : 'rgba(19, 78, 74, 0.95)', // Deep green with transparency
          color: mode === 'light' ? PETRONAS_COLORS.GREEN[900] : PETRONAS_COLORS.GREEN[50],
          borderBottomColor: mode === 'light' ? PETRONAS_COLORS.GREEN[200] : PETRONAS_COLORS.GREEN[700],
        },
      },
    },
  },
})

export const createAppTheme = (mode: PaletteMode) => createTheme(getThemeOptions(mode))

// Default light theme for backwards compatibility
export const theme = createAppTheme('light')
export default theme