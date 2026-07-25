import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { motion } from 'framer-motion'
import {
  Package,
  TrendingUp,
  ShoppingCart,
  Bot,
  Loader2,
  CheckCircle2,
  AlertCircle,
  ChevronDown,
  ChevronRight,
  XCircle,
  Clock,
  DollarSign,
  AlertTriangle,
  CalendarDays,
  MessageSquareText,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useAuthStore } from '@/stores/authStore'
import apiClient from '@/api/client'

/** 看板数据类型 */
interface DashboardData {
  products: {
    total: number
    this_month: number
    pending: number
  }
  recent: Array<{
    id: string
    title: string
    price: number | null
    status: string
    created_at: string
  }>
  credits: {
    remaining: number
    used: number
  }
}

export default function DashboardPage() {
  const { user } = useAuthStore()
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [input, setInput] = useState('')
  const [showAgentResult, setShowAgentResult] = useState(false)

  // 看板数据
  const { data: dashboard, isLoading } = useQuery<DashboardData>({
    queryKey: ['dashboard'],
    queryFn: async () => {
      const res = await apiClient.get('/analytics/dashboard')
      return res.data
    },
  })

  // 快捷跳转
  const quickActions = [
    { icon: ShoppingCart, label: '录入商品', path: '/products', color: 'text-blue-500', bg: 'bg-blue-500/10' },
    { icon: MessageSquareText, label: 'AI 生成', path: '/content', color: 'text-amber-500', bg: 'bg-amber-500/10' },
    { icon: Bot, label: 'AI 助手', path: '/agent', color: 'text-violet-500', bg: 'bg-violet-500/10' },
    { icon: DollarSign, label: '算利润', path: '/ledger', color: 'text-emerald-500', bg: 'bg-emerald-500/10' },
  ]

  // ── Agent 执行 ──────────────────────────────────────────
  const agentMutation = useMutation({
    mutationFn: async (instruction: string) => {
      const res = await apiClient.post('/agent/run', { instruction })
      return res.data
    },
    onSuccess: () => setShowAgentResult(true),
  })

  const handleSubmit = () => {
    if (!input.trim()) return
    setShowAgentResult(false)
    agentMutation.mutate(input.trim())
  }

  const timeAgo = (dateStr: string) => {
    const diff = Date.now() - new Date(dateStr).getTime()
    const mins = Math.floor(diff / 60000)
    if (mins < 60) return `${mins} 分钟前`
    const hours = Math.floor(mins / 60)
    if (hours < 24) return `${hours} 小时前`
    return `${Math.floor(hours / 24)} 天前`
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    )
  }

  const stats = [
    {
      title: '商品总数',
      value: dashboard?.products?.total ?? 0,
      sub: `本月新增 ${dashboard?.products?.this_month ?? 0}`,
      icon: Package,
      color: 'text-blue-500',
      bg: 'bg-blue-500/10',
    },
    {
      title: '待处理',
      value: dashboard?.products?.pending ?? 0,
      sub: dashboard?.products?.pending ? '需要补充信息' : '已全部完善',
      icon: AlertTriangle,
      color: dashboard?.products?.pending ? 'text-amber-500' : 'text-emerald-500',
      bg: dashboard?.products?.pending ? 'bg-amber-500/10' : 'bg-emerald-500/10',
    },
    {
      title: '剩余积分',
      value: dashboard?.credits?.remaining ?? 0,
      sub: `已用 ${dashboard?.credits?.used ?? 0}`,
      icon: DollarSign,
      color: 'text-emerald-500',
      bg: 'bg-emerald-500/10',
    },
    {
      title: 'AI 助手',
      value: '对话式',
      sub: '一句话搞定操作',
      icon: Bot,
      color: 'text-violet-500',
      bg: 'bg-violet-500/10',
    },
  ]

  return (
    <div className="space-y-5">
      {/* ── 头部 ──────────────────────────────────────────── */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold tracking-tight">
            👋 你好, {user?.username || '卖家'}！
          </h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            今天有什么要做的？
          </p>
        </div>
        <Button onClick={() => navigate('/agent')} className="gap-2">
          <Bot className="h-4 w-4" />
          AI 助手
        </Button>
      </div>

      {/* ── 快捷入口 ──────────────────────────────────────── */}
      <div className="grid grid-cols-4 gap-3">
        {quickActions.map((action) => (
          <Card
            key={action.label}
            className="cursor-pointer transition-all hover:shadow-md hover:-translate-y-0.5"
            onClick={() => navigate(action.path)}
          >
            <CardContent className="flex flex-col items-center gap-2 py-4">
              <div className={`rounded-lg p-2.5 ${action.bg}`}>
                <action.icon className={`h-5 w-5 ${action.color}`} />
              </div>
              <span className="text-xs font-medium">{action.label}</span>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* ── 统计卡片 ──────────────────────────────────────── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {stats.map((s) => (
          <Card key={s.title}>
            <CardContent className="p-4">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-xs text-muted-foreground">{s.title}</p>
                  <p className="text-2xl font-bold mt-0.5">{s.value}</p>
                  <p className="text-xs text-muted-foreground mt-1">{s.sub}</p>
                </div>
                <div className={`rounded-lg p-2 ${s.bg}`}>
                  <s.icon className={`h-4 w-4 ${s.color}`} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* ── AI 输入框（快捷指令） ──────────────────────────── */}
      <Card className="border-primary/20 bg-primary/5">
        <CardContent className="p-4">
          <div className="flex gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
              placeholder="粘贴 1688 链接，或说"帮我算利润""...
              className="flex-1 h-10 rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary/40"
            />
            <Button onClick={handleSubmit} disabled={!input.trim() || agentMutation.isPending} className="h-10 px-4">
              {agentMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Bot className="h-4 w-4" />}
            </Button>
          </div>
          <div className="flex gap-2 mt-2">
            {['帮我算利润', '检查合规', '抓取商品'].map((hint) => (
              <button
                key={hint}
                className="text-xs text-muted-foreground bg-background px-2 py-1 rounded-md border hover:bg-accent"
                onClick={() => { setInput(hint); handleSubmit() }}
              >
                {hint}
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Agent 结果 */}
      {agentMutation.data && showAgentResult && (
        <AgentResult data={agentMutation.data} onClose={() => setShowAgentResult(false)} />
      )}

      {/* ── 最近操作 ──────────────────────────────────────── */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm flex items-center gap-2">
            <Clock className="h-4 w-4 text-muted-foreground" />
            最近操作
          </CardTitle>
        </CardHeader>
        <CardContent>
          {dashboard?.recent && dashboard.recent.length > 0 ? (
            <div className="space-y-2">
              {dashboard.recent.map((p) => (
                <div
                  key={p.id}
                  className="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-muted/50 cursor-pointer text-sm"
                  onClick={() => navigate(`/products/${p.id}`)}
                >
                  <div className="flex items-center gap-3 min-w-0">
                    {p.status === '待补充' ? (
                      <AlertCircle className="h-4 w-4 text-amber-500 shrink-0" />
                    ) : (
                      <CheckCircle2 className="h-4 w-4 text-emerald-500 shrink-0" />
                    )}
                    <span className="truncate">{p.title}</span>
                    {p.price != null && <span className="text-muted-foreground shrink-0">¥{p.price}</span>}
                  </div>
                  <span className="text-xs text-muted-foreground shrink-0 ml-2">{timeAgo(p.created_at)}</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-6 text-sm text-muted-foreground">
              还没有商品，点击上方「录入商品」开始
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

/**
 * AgentResult - AI 智能助手执行结果
 */
function AgentResult({ data, onClose }: { data: any; onClose: () => void }) {
  const [expanded, setExpanded] = useState(false)

  const statusIcon = (s: string) => {
    if (s === 'success') return <CheckCircle2 className="h-4 w-4 text-emerald-500 shrink-0" />
    if (s === 'failed') return <XCircle className="h-4 w-4 text-destructive shrink-0" />
    return <Loader2 className="h-4 w-4 animate-spin shrink-0" />
  }

  const actionLabel = (a: string) => {
    const labels: Record<string, string> = {
      scrape_1688: '抓取 1688 商品',
      create_product: '创建商品',
      generate_listing: 'AI 生成 Listing',
      compliance_check: '合规审查',
      calculate_profit: '净利计算',
      answer: '回答',
    }
    return labels[a] || a
  }

  return (
    <Card className={`${data.status === 'success' ? 'border-emerald-500/30' : 'border-destructive/30'}`}>
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-2">
            {data.status === 'success' ? (
              <CheckCircle2 className="h-5 w-5 text-emerald-500 mt-0.5" />
            ) : (
              <XCircle className="h-5 w-5 text-destructive mt-0.5" />
            )}
            <div>
              <p className="text-sm font-medium">AI 执行结果</p>
              <p className="text-sm text-muted-foreground mt-0.5">{data.summary}</p>
            </div>
          </div>
          <div className="flex gap-1">
            <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => setExpanded(!expanded)}>
              {expanded ? <ChevronDown className="h-3.5 w-3.5" /> : <ChevronRight className="h-3.5 w-3.5" />}
            </Button>
            <Button variant="ghost" size="icon" className="h-7 w-7 text-muted-foreground" onClick={onClose}>
              <XCircle className="h-3.5 w-3.5" />
            </Button>
          </div>
        </div>
      </CardHeader>
      {expanded && data.steps && (
        <CardContent className="space-y-1.5 pt-0">
          {data.steps.map((step: any, i: number) => (
            <div key={i} className="flex items-start gap-2 text-sm">
              {statusIcon(step.status)}
              <div>
                <span className="text-xs font-medium">{actionLabel(step.action)}</span>
                {step.summary && <p className="text-xs text-muted-foreground">{step.summary}</p>}
                {step.error && <p className="text-xs text-destructive">{step.error}</p>}
              </div>
            </div>
          ))}
        </CardContent>
      )}
    </Card>
  )
}
