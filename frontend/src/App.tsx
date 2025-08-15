import { Routes, Route } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { ProtectedRoute } from './components/ProtectedRoute'
import { Layout } from './components/Layout'

// Page imports
import { HomePage } from './pages/HomePage'
import { PropertiesPage } from './pages/PropertiesPage'
import { PropertyDetailPage } from './pages/PropertyDetailPage'
import { StockPredictorPage } from './pages/StockPredictorPage'
import { LoginPage } from './pages/LoginPage'
import { RegisterPage } from './pages/RegisterPage'
import { OAuthCallbackPage } from './pages/OAuthCallbackPage'
import { DashboardPage } from './pages/DashboardPage'
import { CreatePropertyPage } from './pages/CreatePropertyPage'
import { ChatPage } from './pages/ChatPage'
import { BookingsPage } from './pages/BookingsPage'
import { LawyersPage } from './pages/LawyersPage'
import { UserTypeSelectionPage } from './pages/UserTypeSelectionPage'
import { NotFoundPage } from './pages/NotFoundPage'

function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="properties" element={<PropertiesPage />} />
          <Route path="properties/:id" element={<PropertyDetailPage />} />
          <Route path="stocks" element={<StockPredictorPage />} />
          <Route path="lawyers" element={<LawyersPage />} />
          <Route path="login" element={<LoginPage />} />
          <Route path="register" element={<RegisterPage />} />
          <Route path="auth/callback" element={<OAuthCallbackPage />} />
          <Route path="select-role" element={<UserTypeSelectionPage />} />
        </Route>

        {/* Protected routes */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route index element={<DashboardPage />} />
          <Route path="properties/create" element={<CreatePropertyPage />} />
          <Route path="chat" element={<ChatPage />} />
          <Route path="chat/:conversationId" element={<ChatPage />} />
          <Route path="bookings" element={<BookingsPage />} />
        </Route>

        {/* 404 page */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </AuthProvider>
  )
}

export default App 