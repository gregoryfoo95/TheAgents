import HomeIcon from '@mui/icons-material/Home'
import SearchIcon from '@mui/icons-material/Search'
import ScaleIcon from '@mui/icons-material/Scale'
import DashboardIcon from '@mui/icons-material/Dashboard'
import MessageIcon from '@mui/icons-material/Message'
import EventIcon from '@mui/icons-material/Event'
import AddIcon from '@mui/icons-material/Add'
import TrendingUpIcon from '@mui/icons-material/TrendingUp'
import { NavigationItem } from '../components/Navigation'

export const PUBLIC_NAVIGATION: NavigationItem[] = [
  { name: 'Home', href: '/', icon: HomeIcon },
  { name: 'Properties', href: '/properties', icon: SearchIcon },
  { name: 'Stock Predictor', href: '/stocks', icon: TrendingUpIcon },
  { name: 'Lawyers', href: '/lawyers', icon: ScaleIcon },
]

export const USER_NAVIGATION: NavigationItem[] = [
  { name: 'Dashboard', href: '/dashboard', icon: DashboardIcon },
  { name: 'Messages', href: '/dashboard/chat', icon: MessageIcon },
  { name: 'Bookings', href: '/dashboard/bookings', icon: EventIcon },
]

export const AGENT_NAVIGATION: NavigationItem[] = [
  { name: 'Add Property', href: '/dashboard/properties/create', icon: AddIcon }
]