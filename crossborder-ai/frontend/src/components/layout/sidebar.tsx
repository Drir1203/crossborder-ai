import { NavLink } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import {
  LayoutDashboard,
  Package,
  FileText,
  Image,
  ShoppingBag,
  BarChart3,
  CreditCard,
  Settings,
  Globe,
  ChevronLeft,
  Sparkles,
  Upload,
  Radar,
  Calculator,
  Bot,
} from 'lucide-react'
import { cn } from '@/utils/cn'
import { Button } from '@/components/ui/button'
import { useState } from 'react'

export function Sidebar({ onClose }: { onClose?: () => void }) {
  const { t } = useTranslation()
  const [collapsed, setCollapsed] = useState(false)

  const navItems = [
    { icon: LayoutDashboard, label: t('nav.dashboard'), path: '/app/dashboard' },
    { icon: Package, label: t('nav.products'), path: '/app/products' },
    { icon: Sparkles, label: t('nav.content'), path: '/app/content' },
    { icon: Bot, label: t('nav.agent'), path: '/app/agent' },
    { icon: Image, label: t('nav.images'), path: '/app/images' },
    { icon: Upload, label: t('nav.batch'), path: '/app/batch' },
    { icon: Globe, label: t('nav.shopify'), path: '/app/shopify' },
    { icon: CreditCard, label: t('nav.billing'), path: '/app/billing' },
    { icon: Settings, label: t('nav.settings'), path: '/app/settings' },
  ]

  return (
    <aside
      className={cn(
        'flex flex-col border-r border-glass-border bg-glass backdrop-blur-xl transition-all duration-300',
        collapsed ? 'w-16' : 'w-60',
      )}
    >
      {/* Logo */}
      <div className="flex h-14 items-center border-b px-4">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary shrink-0">
            <Globe className="h-4 w-4 text-primary-foreground" />
          </div>
          {!collapsed && (
            <span className="font-bold text-sm tracking-tight whitespace-nowrap">
              VeyaShip AI
            </span>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 p-2">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            onClick={onClose}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors',
                isActive
                  ? 'bg-primary/10 text-primary font-medium shadow-[0_0_20px_-6px_var(--glow-primary)]'
                  : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground',
                collapsed && 'justify-center px-2',
              )
            }
          >
            <item.icon className="h-4 w-4 shrink-0" />
            {!collapsed && <span>{item.label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Collapse toggle */}
      <div className="border-t p-2">
        <Button
          variant="ghost"
          size="icon"
          className={cn('w-full', collapsed && 'mx-auto')}
          onClick={() => setCollapsed(!collapsed)}
        >
          <ChevronLeft
            className={cn(
              'h-4 w-4 transition-transform',
              collapsed && 'rotate-180',
            )}
          />
        </Button>
      </div>
    </aside>
  )
}
