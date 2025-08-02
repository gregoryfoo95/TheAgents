# TanStack Query Hooks

This directory contains all the TanStack Query hooks for data fetching and caching in the frontend application.

## Features

### ✅ Complete Migration
- **Replaced old API calls** with TanStack Query hooks
- **Automatic caching** with configurable stale times
- **Optimistic updates** for better UX
- **Error handling** with toast notifications
- **Background refetching** and cache invalidation

### 🚀 Performance Benefits
- **Intelligent caching** reduces redundant API calls
- **Infinite queries** for large lists (properties)
- **Parallel queries** when multiple data sources needed
- **Optimistic mutations** for instant feedback
- **Background updates** keep data fresh

### 📁 Hook Categories

#### Authentication (`useAuth.ts`)
- `useCurrentUser()` - Get current authenticated user
- `useLogin()` - Login mutation with auto-caching
- `useRegister()` - Registration with auto-login
- `useUpdateProfile()` - Update user profile
- `useLogout()` - Logout with cache clearing

#### Properties (`useProperties.ts`)
- `useProperties(filters, page, size)` - Paginated property list
- `useInfiniteProperties(filters)` - Infinite scroll property list
- `useProperty(id)` - Single property details
- `useMyProperties()` - Current user's properties
- `useCreateProperty()` - Create new property
- `useUpdateProperty()` - Update existing property
- `useDeleteProperty()` - Delete property
- `useUploadPropertyImages()` - Upload property images

#### Chat (`useChat.ts`)
- `useConversations()` - User's conversations list
- `useConversation(id)` - Single conversation with messages
- `useCreateConversation()` - Start new conversation
- `useSendMessage()` - Send message with optimistic updates
- `useUploadMessageFile()` - Upload files to messages
- `useAddLawyerToConversation()` - Add lawyer to conversation
- `useOptimisticMessage()` - Utility for optimistic message updates

#### Bookings (`useBookings.ts`)
- `useMyBookings(status?)` - User's bookings with optional status filter
- `useBooking(id)` - Single booking details
- `useAvailableSlots(propertyId, date)` - Available booking slots
- `useCreateBooking()` - Create new booking
- `useUpdateBooking()` - Update booking
- `useCancelBooking()` - Cancel booking
- `useConfirmBooking()` - Confirm booking (utility)
- `useCompleteBooking()` - Mark booking complete (utility)

#### Lawyers (`useLawyers.ts`)
- `useLawyers(filters)` - Filtered lawyer list
- `useLawyer(id)` - Single lawyer profile
- `useMyLawyerProfile()` - Current user's lawyer profile
- `useLawyerSpecializations()` - Available specializations
- `useCreateLawyerProfile()` - Create lawyer profile
- `useUpdateLawyerProfile()` - Update lawyer profile
- Utility hooks for common filters (verified, by specialization, etc.)

#### AI Services (`useAI.ts`)
- `usePropertyValuations(propertyId)` - Property valuation history
- `usePropertyRecommendations(propertyId)` - AI recommendations
- `useMarketTrends(zipCode)` - Market trends by location
- `useValuateProperty()` - Trigger new valuation
- `useGenerateRecommendations()` - Generate new recommendations
- `useAnalyzeImage()` - Analyze property images
- Utility hooks for latest valuations, high priority recommendations, etc.

## 🎯 Key Features

### Smart Caching Strategy
```typescript
// Different stale times based on data volatility
- User data: 5 minutes
- Properties: 2 minutes  
- Conversations: 30 seconds (real-time feel)
- Bookings: 1 minute
- Market trends: 30 minutes
- Lawyer specializations: 1 hour
```

### Optimistic Updates
```typescript
// Messages appear instantly, sync in background
const sendMessage = useSendMessage()
const addOptimisticMessage = useOptimisticMessage()

const handleSend = (message) => {
  addOptimisticMessage(conversationId, message) // Instant UI update
  sendMessage.mutate(message) // Background sync
}
```

### Infinite Queries
```typescript
// Properties load more as user scrolls
const {
  data,
  fetchNextPage,
  hasNextPage,
  isFetchingNextPage
} = useInfiniteProperties(filters)
```

### Real-time Feel
```typescript
// Conversations poll every 5 seconds for new messages
const conversation = useConversation(id, {
  refetchInterval: 5000
})
```

## 🔧 Usage Examples

### Basic Data Fetching
```typescript
function PropertyList() {
  const { data: properties, isLoading, error } = useProperties()
  
  if (isLoading) return <LoadingSpinner />
  if (error) return <ErrorMessage />
  
  return (
    <div>
      {properties?.properties.map(property => (
        <PropertyCard key={property.id} property={property} />
      ))}
    </div>
  )
}
```

### Mutations with Optimistic Updates
```typescript
function CreatePropertyForm() {
  const createProperty = useCreateProperty()
  
  const handleSubmit = async (data) => {
    try {
      await createProperty.mutateAsync(data)
      navigate('/properties') // Auto-cached on success
    } catch (error) {
      // Error handled by hook with toast
    }
  }
  
  return (
    <form onSubmit={handleSubmit}>
      {/* form fields */}
      <button disabled={createProperty.isPending}>
        {createProperty.isPending ? 'Creating...' : 'Create Property'}
      </button>
    </form>
  )
}
```

### Multiple Related Queries
```typescript
function Dashboard() {
  const { data: properties } = useMyProperties()
  const { data: bookings } = useMyBookings()
  const { data: conversations } = useConversations()
  
  // All queries run in parallel, cached independently
  const stats = {
    activeProperties: properties?.filter(p => p.status === 'active').length,
    pendingBookings: bookings?.filter(b => b.status === 'pending').length,
    activeChats: conversations?.filter(c => c.status === 'active').length
  }
  
  return <StatsCards stats={stats} />
}
```

## 🎨 Integration with UI

The hooks are fully integrated with:
- ✅ **Toast notifications** for all mutations
- ✅ **Loading states** for all queries  
- ✅ **Error handling** with user-friendly messages
- ✅ **Optimistic updates** for instant feedback
- ✅ **Cache invalidation** to keep data consistent
- ✅ **Background refetching** for fresh data

## 🔄 Migration from Old System

The old API service in `services/api.ts` is still available but all components should now use the TanStack Query hooks instead. The new `AuthContext` has been updated to use the query hooks as well.

### Before (Old Way)
```typescript
const [properties, setProperties] = useState([])
const [loading, setLoading] = useState(true)

useEffect(() => {
  const fetchProperties = async () => {
    try {
      setLoading(true)
      const data = await propertiesAPI.getProperties()
      setProperties(data.properties)
    } catch (error) {
      toast.error('Failed to load properties')
    } finally {
      setLoading(false)
    }
  }
  fetchProperties()
}, [])
```

### After (New Way)
```typescript
const { data: properties, isLoading } = useProperties()
// Error handling, caching, and loading states are automatic!
``` 