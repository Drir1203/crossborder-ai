import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { motion } from 'framer-motion'
import {
  Package,
  FileText,
  Sparkles,
  TrendingUp,
  ShoppingCart,
  Globe,
  ArrowRight,
  CreditCard,
  Link as LinkIcon,
  MessageSquareText,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useAuthStore } from '@/stores/authStore'
import apiClient from '@/api/client'
import type { DashboardData } from '@/types'

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 },
  },
}

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 },
}

export default function DashboardPage() {
  const { user } = useAuthStore()
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [input, setInput] = useState('')

  const handleSubmit = () => {
    if (!input.trim()) return
    const val = input.trim()
    // URL → 跳转商品抓取
    if (val.startsWith('http://') || val.startsWith('https://')) {
      navigate(`/products?url=${encodeURIComponent(val)}`)
    } else {
      // 文本 → 跳转 AI 生成（需要先有商品，先跳转到商品页手动录入）
      navigate(`/products?q=${encodeURIComponent(val)}`)
    }
  }

  const { data: dashboard, isLoading } = useQuery<DashboardData>({
    queryKey: ['dashboard'],
    queryFn: async () => {
      const response = await apiClient.get('/analytics/dashboard')
      return response.data
    },
  })

  const stats = [
    {
      title: t('dashboard.products'),
      value: dashboard?.products?.total ?? 0,
      icon: Package,
      color: 'text-blue-500',
      bg: 'bg-blue-500/10',
      link: '/products',
    },
    {
      title: t('dashboard.listings'),
      value: dashboard?.listings?.total ?? 0,
      icon: FileText,
      color: 'text-violet-500',
      bg: 'bg-violet-500/10',
      link: '/listings',
    },
    {
      title: t('dashboard.aiGenerations'),
      value: dashboard?.content?.total_generations ?? 0,
      icon: Sparkles,
      color: 'text-amber-500',
      bg: 'bg-amber-500/10',
      link: '/content',
    },
    {
      title: t('dashboard.published'),
      value: dashboard?.listings?.published ?? 0,
      icon: Globe,
      color: 'text-emerald-500',
      bg: 'bg-emerald-500/10',
      link: '/listings',
    },
  ]

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      {/* Welcome */}
      <motion.div variants={item}>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">
              {t('dashboard.welcome')}{user?.username ? `, ${user.username}` : ''}! 👋
            </h1>
            <p className="text-muted-foreground">
              {t('dashboard.overview')}
            </p>
          </div>
          <Button onClick={() => navigate('/content')}>
            <Sparkles className="mr-2 h-4 w-4" />
            {t('dashboard.generateContent')}
          </Button>
        </div>
      </motion.div>

      {/* 中央输入框 */}
      <motion.div variants={item}>
        <Card className="border-primary/20 bg-primary/5">
          <CardContent className="pt-6">
            <div className="flex gap-3">
              <div className="relative flex-1">
                <LinkIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
                  placeholder="粘贴 1688 链接抓取商品，或输入商品名称用 AI 生成 Listing..."
                  className="flex h-12 w-full rounded-md border bg-background pl-10 pr-4 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                />
              </div>
              <Button className="h-12 px-6" onClick={handleSubmit}>
                <Sparkles className="mr-2 h-4 w-4" />
                开始
              </Button>
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              粘贴 1688 链接 → 自动抓取商品信息 ｜ 输入商品名 → 跳转到手动录入
            </p>
          </CardContent>
        </Card>
      </motion.div>

      {/* Credit Bar */}
      <motion.div variants={item}>
        <Card className="bg-gradient-to-r from-primary/10 via-primary/5 to-background border-primary/20">
          <CardContent className="flex items-center justify-between p-4">
            <div className="flex items-center gap-3">
              <CreditCard className="h-8 w-8 text-primary" />
              <div>
                <p className="text-sm font-medium">{t('dashboard.availableCredits')}</p>
                <p className="text-2xl font-bold">
                  {user?.credits_remaining ?? 0}
                  <span className="text-sm font-normal text-muted-foreground">
                    {' / '}{user?.credits_total ?? 0}
                  </span>
                </p>
              </div>
            </div>
            <Badge variant="secondary" className="capitalize">
              {user?.plan} {t('dashboard.plan')}
            </Badge>
          </CardContent>
        </Card>
      </motion.div>

      {/* Stats Grid */}
      <motion.div variants={item} className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.title} className="cursor-pointer transition-colors hover:bg-accent/50"
            onClick={() => navigate(stat.link)}
          >
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {stat.title}
              </CardTitle>
              <div className={`rounded-lg p-2 ${stat.bg}`}>
                <stat.icon className={`h-4 w-4 ${stat.color}`} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
            </CardContent>
          </Card>
        ))}
      </motion.div>

      {/* Quick Actions */}
      <motion.div variants={item} className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ShoppingCart className="h-5 w-5 text-primary" />
              {t('dashboard.quickActions')}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <Button variant="outline" className="w-full justify-between" onClick={() => navigate('/products')}>
              {t('dashboard.addProduct')} <ArrowRight className="h-4 w-4" />
            </Button>
            <Button variant="outline" className="w-full justify-between" onClick={() => navigate('/content')}>
              {t('dashboard.generateListing')} <ArrowRight className="h-4 w-4" />
            </Button>
            <Button variant="outline" className="w-full justify-between" onClick={() => navigate('/images')}>
              {t('dashboard.generateImage')} <ArrowRight className="h-4 w-4" />
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-primary" />
              {t('dashboard.recentActivity')}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center justify-center py-8 text-center text-muted-foreground">
              <TrendingUp className="mb-2 h-8 w-8" />
              <p className="text-sm">{t('dashboard.activityEmpty')}</p>
              <p className="text-xs">{t('dashboard.activityHint')}</p>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  )
}
