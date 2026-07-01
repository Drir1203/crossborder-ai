import { Outlet, Navigate } from 'react-router-dom'
import { Sidebar } from './sidebar'
import { Header } from './header'
import { useAuthStore } from '@/stores/authStore'
import { useEffect } from 'react'

export function RootLayout() {
  const { isAuthenticated, loadUser, isLoading, token } = useAuthStore()

  useEffect(() => {
    if (token && !useAuthStore.getState().user) {
      loadUser()
    }
  }, [token, loadUser])

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
