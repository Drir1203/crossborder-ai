// ============================================================================
// VeyaShip - Root Application with Routing
// ============================================================================

import { Routes, Route, Navigate } from 'react-router-dom'
import { RootLayout } from '@/components/layout/root-layout'
import LoginPage from '@/pages/auth/LoginPage'
import RegisterPage from '@/pages/auth/RegisterPage'
import DashboardPage from '@/pages/dashboard/DashboardPage'
import ProductsPage from '@/pages/products/ProductsPage'
import ProductDetailPage from '@/pages/products/ProductDetailPage'
import SettingsPage from '@/pages/settings/SettingsPage'
import ContentPage from '@/pages/content/ContentPage'
import BillingPage from '@/pages/billing/BillingPage'
import ImagesPage from '@/pages/images/ImagesPage'
import AnalyticsPage from '@/pages/analytics/AnalyticsPage'
import ShopifyPage from '@/pages/shopify/ShopifyPage'
import BatchPage from '@/pages/batch/BatchPage'
import RadarPage from '@/pages/radar/RadarPage'
import LedgerPage from '@/pages/ledger/LedgerPage'
import AgentPage from '@/pages/agent/AgentPage'
import { useAuthStore } from '@/stores/authStore'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return <>{children}</>
}

export default function App() {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      {/* Protected Routes */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <RootLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="agent" element={<AgentPage />} />
        <Route path="products" element={<ProductsPage />} />
        <Route path="products/:id" element={<ProductDetailPage />} />
        <Route path="listings" element={<ListingsPlaceholder />} />
        <Route path="content" element={<ContentPage />} />
        <Route path="images" element={<ImagesPage />} />
        <Route path="shopify" element={<ShopifyPage />} />
        <Route path="batch" element={<BatchPage />} />
        <Route path="radar" element={<RadarPage />} />
        <Route path="ledger" element={<LedgerPage />} />
        <Route path="analytics" element={<AnalyticsPage />} />
        <Route path="billing" element={<BillingPage />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

// --- Placeholder pages (to be implemented in detail later) ---
function PlaceholderPage({ title, description }: { title: string; description: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-20">
      <h1 className="text-2xl font-bold">{title}</h1>
      <p className="mt-2 text-muted-foreground">{description}</p>
    </div>
  )
}

function ProductsPlaceholder() {
  return <PlaceholderPage title="Products" description="Manage your product catalog" />
}

function ListingsPlaceholder() {
  return <PlaceholderPage title="Listings" description="Multi-platform listing management" />
}


