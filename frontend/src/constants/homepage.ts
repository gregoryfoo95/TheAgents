import {
  Search as SearchIcon,
  Psychology as BrainIcon,
  Scale as ScaleIcon,
  Message as MessageIcon,
  Security as ShieldIcon,
} from '@mui/icons-material'
import { BRAND_GRADIENTS, PETRONAS_COLORS } from './colors'

export const HERO_GRADIENTS = {
  PRIMARY: BRAND_GRADIENTS.PRIMARY,
  TEXT_PRIMARY: 'linear-gradient(45deg, #ffffff 30%, #f0fdf9 90%)',
  TEXT_SECONDARY: `linear-gradient(45deg, ${PETRONAS_COLORS.CYAN[300]} 30%, ${PETRONAS_COLORS.GREEN[300]} 90%)`,
  BUTTON_PRIMARY: 'linear-gradient(45deg, #ffffff 30%, #f0fdf9 90%)',
  BUTTON_HOVER: 'linear-gradient(45deg, #f0fdf9 30%, #ffffff 90%)',
} as const

export const SECTION_GRADIENTS = {
  FEATURES: `linear-gradient(180deg, ${PETRONAS_COLORS.GREEN[50]} 0%, #ffffff 100%)`,
  CTA: BRAND_GRADIENTS.SECONDARY,
  CARD: `linear-gradient(145deg, #ffffff 0%, ${PETRONAS_COLORS.GREEN[50]} 100%)`,
  ICON: BRAND_GRADIENTS.PRIMARY,
} as const

export const FEATURES_DATA = [
  {
    icon: BrainIcon,
    title: 'AI-Powered Valuations',
    description: 'Get accurate property valuations powered by machine learning and market data analysis.',
  },
  {
    icon: SearchIcon,
    title: 'Smart Search',
    description: 'Find your perfect property with intelligent filters and personalized recommendations.',
  },
  {
    icon: ScaleIcon,
    title: 'Legal Support',
    description: 'Connect with verified lawyers for seamless transaction support and documentation.',
  },
  {
    icon: MessageIcon,
    title: 'Direct Communication',
    description: 'Chat directly with buyers, sellers, and lawyers in secure, integrated messaging.',
  },
  {
    icon: ShieldIcon,
    title: 'Secure Transactions',
    description: 'End-to-end security with verified users and protected payment processing.',
  },
] as const

export const MASCOT_ANIMATIONS = ['jump', 'bounce', 'float', 'wiggle'] as const

export const ANIMATION_CONFIG = {
  MOVE_INTERVAL_BASE: 3500,
  MOVE_INTERVAL_RANDOM: 2000,
  TRANSITION_DURATION: '2s',
  CLICK_THRESHOLD: 5,
} as const