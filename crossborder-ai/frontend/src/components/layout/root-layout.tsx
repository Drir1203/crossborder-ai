import { useState } from 'react'
import { Outlet, Navigate } from 'react-router-dom'
import { Sidebar } from './sidebar'
import { Header } from './header'
import { useAuthStore } from '@/stores/authStore'
import { useEffect } from 'react'
import { Menu, X } from 'lucide-react'

export function RootLayout() {
  const { isAuthenticated, loadUser, isLoading, token } = useAuthStore()
  const [mobileSidebar, setMobileSidebar] = useState(false)

  useEffect(() => {
    if (token && !useAuthStore.getState().user) {
      loadUser()
    }
  }, [token, loadUser])

  // 移动端：侧边栏打开时禁止滚动
  useEffect(() => {
    document.body.style.overflow = mobileSidebar ? 'hidden' : ''
    return () => { document.body.style.overflow = '' }
  }, [mobileSidebar])

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return (
    <div className="relative flex h-screen overflow-hidden">
      {/* 高级感背景：aurora 光晕 + 细腻颗粒 */}
      <div className="aurora-layer" aria-hidden />
      <div className="grain" aria-hidden />

      {/* 桌面端侧边栏 */}
      <div className="relative z-10 hidden lg:flex">
        <Sidebar />
      </div>

      {/* 移动端侧边栏（遮罩） */}
      {mobileSidebar && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="absolute inset-0 bg-black/50" onClick={() => setMobileSidebar(false)} />
          <div className="absolute left-0 top-0 h-full">
            <Sidebar onClose={() => setMobileSidebar(false)} />
          </div>
        </div>
      )}

      <div className="relative z-10 flex flex-1 flex-col overflow-hidden">
        {/* 移动端顶栏 */}
        <div className="lg:hidden flex items-center justify-between border-b border-glass-border bg-glass backdrop-blur-xl px-4 h-14">
          <button onClick={() => setMobileSidebar(true)} className="p-2 -ml-2">
            <Menu className="h-5 w-5" />
          </button>
          <span className="font-bold text-sm">VeyaShip AI</span>
          <div className="w-9" /> {/* 占位保持对称 */}
        </div>

        <Header />
        <main className="flex-1 overflow-y-auto p-4 md:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
