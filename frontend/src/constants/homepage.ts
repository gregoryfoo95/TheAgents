import {
  Search as SearchIcon,
  Psychology as BrainIcon,
  Scale as ScaleIcon,
  Message as MessageIcon,
  Security as ShieldIcon,
} from '@mui/icons-material'

export const HERO_GRADIENTS = {
  PRIMARY: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  TEXT_PRIMARY: 'linear-gradient(45deg, #ffffff 30%, #f0f9ff 90%)',
  TEXT_SECONDARY: 'linear-gradient(45deg, #a78bfa 30%, #c084fc 90%)',
  BUTTON_PRIMARY: 'linear-gradient(45deg, #ffffff 30%, #f8fafc 90%)',
  BUTTON_HOVER: 'linear-gradient(45deg, #f8fafc 30%, #ffffff 90%)',
} as const

export const SECTION_GRADIENTS = {
  FEATURES: 'linear-gradient(180deg, #f8fafc 0%, #ffffff 100%)',
  CTA: 'linear-gradient(135deg, #f093fb 0%, #f5576c 50%, #4facfe 100%)',
  CARD: 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
  ICON: 'linear-gradient(135deg, #667eea, #764ba2)',
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