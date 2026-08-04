import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { LogOut, User, Settings, CreditCard, ChevronDown, Globe, Palette, Store } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/stores/authStore'
import { useStoreStore } from '@/stores/storeStore'
import { Badge } from '@/components/ui/badge'
import apiClient from '@/api/client'
import { themes, getTheme, applyTheme, Theme } from '@/utils/themes'

const LANGUAGES = [
  { code: 'en', label: 'English', flag: '🇺🇸' },
  { code: 'zh', label: '中文', flag: '🇨🇳' },
  { code: 'ja', label: '日本語', flag: '🇯🇵' },
  { code: 'ko', label: '한국어', flag: '🇰🇷' },
  { code: 'es', label: 'Español', flag: '🇪🇸' },
  { code: 'fr', label: 'Français', flag: '🇫🇷' },
  { code: 'de', label: 'Deutsch', flag: '🇩🇪' },
  { code: 'pt', label: 'Português', flag: '🇧🇷' },
  { code: 'ru', label: 'Русский', flag: '🇷🇺' },
]

export function Header() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const { t, i18n } = useTranslation()
  const [currentTheme, setCurrentTheme] = useState<Theme>(getTheme)
  const { stores, currentStoreId, setStores, setCurrentStore } = useStoreStore()

  // 加载店铺列表
  useQuery({
    queryKey: ['header-shopify-channels'],
    queryFn: async () => {
      const r = await apiClient.get('/shopify/channels')
      const channels = (r.data || []).map((c: any) => ({
        id: c.id,
        name: c.shop_name,
        platform: 'shopify' as const,
      }))
      if (channels.length > 0) setStores(channels)
      return channels
    },
    enabled: !!user,
    retry: false,
  })

  const switchTheme = (theme: Theme) => {
    setCurrentTheme(theme)
    applyTheme(theme)
  }

  const currentLang = LANGUAGES.find((l) => l.code === i18n.language) || LANGUAGES[0]

  const switchLanguage = (code: string) => {
    i18n.changeLanguage(code)
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  // 头像显示优先级：username > full_name > email
  const displayName = user?.username || user?.full_name || user?.email || 'U'
  const avatarLetter = displayName.charAt(0).toUpperCase()

  return (
    <header className="flex h-14 items-center justify-between border-b border-glass-border bg-glass backdrop-blur-xl px-4 lg:px-6">
      {/* Left */}
      <div className="flex items-center gap-2">
        <h1 className="text-lg font-semibold" />
      </div>

      {/* Right */}
      <div className="flex items-center gap-2 lg:gap-4">
        {/* Language Switcher */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm" className="flex items-center gap-1.5 px-2 text-muted-foreground">
              <Globe className="h-4 w-4" />
              <span className="hidden text-xs md:inline-block">{currentLang.flag} {currentLang.label}</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-44">
            <DropdownMenuLabel className="text-xs text-muted-foreground">
              {t('common.language')}
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            {LANGUAGES.map((lang) => (
              <DropdownMenuItem
                key={lang.code}
                className={i18n.language === lang.code ? 'bg-accent font-medium' : ''}
                onClick={() => switchLanguage(lang.code)}
              >
                <span className="mr-2">{lang.flag}</span>
                {lang.label}
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>

        {/* Theme Switcher */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm" className="flex items-center gap-1.5 px-2 text-muted-foreground">
              <Palette className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-36">
            <DropdownMenuLabel className="text-xs text-muted-foreground">主题</DropdownMenuLabel>
            <DropdownMenuSeparator />
            {themes.map((theme) => (
              <DropdownMenuItem
                key={theme.name}
                className={currentTheme.name === theme.name ? 'bg-accent font-medium' : ''}
                onClick={() => switchTheme(theme)}
              >
                <span className="w-3 h-3 rounded-full mr-2 inline-block border" style={{
                  background: `hsl(${theme.colors['--primary']})`,
                }} />
                {theme.label}
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>

        {/* 店铺切换 */}
        {stores.length > 0 && (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm" className="flex items-center gap-1.5 px-2 text-muted-foreground">
                <Store className="h-4 w-4" />
                <span className="hidden text-xs md:inline-block">
                  {stores.find(s => s.id === currentStoreId)?.name || '选择店铺'}
                </span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-44">
              <DropdownMenuLabel className="text-xs text-muted-foreground">切换店铺</DropdownMenuLabel>
              <DropdownMenuSeparator />
              {stores.map((s) => (
                <DropdownMenuItem
                  key={s.id}
                  className={currentStoreId === s.id ? 'bg-accent font-medium' : ''}
                  onClick={() => setCurrentStore(s.id)}
                >
                  <Store className="mr-2 h-3.5 w-3.5" />
                  {s.name}
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
        )}

        {/* Credits badge */}
        {user && (
          <Badge variant="secondary" className="gap-1 px-2 py-1 text-xs whitespace-nowrap">
            <CreditCard className="h-3 w-3" />
            <span>{user.credits_remaining}</span>
            <span className="hidden sm:inline">{t('header.credits')}</span>
          </Badge>
        )}

        {/* User menu */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="flex items-center gap-2 px-2">
              <div className="flex h-7 w-7 items-center justify-center rounded-full bg-primary/10 text-xs font-semibold text-primary">
                {avatarLetter}
              </div>
              <span className="hidden text-sm font-medium md:inline-block max-w-[120px] truncate">
                {displayName}
              </span>
              <ChevronDown className="h-3 w-3 text-muted-foreground shrink-0" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48">
            <DropdownMenuLabel>
              <div className="flex flex-col">
                <span className="font-medium truncate max-w-[180px]">{displayName}</span>
                <span className="text-xs text-muted-foreground truncate max-w-[180px]">
                  {user?.email}
                </span>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={() => navigate('/app/settings')}>
              <Settings className="mr-2 h-4 w-4" />
              {t('header.settings')}
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => navigate('/app/billing')}>
              <CreditCard className="mr-2 h-4 w-4" />
              {t('header.billing')}
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={handleLogout}>
              <LogOut className="mr-2 h-4 w-4" />
              {t('header.logout')}
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  )
}
