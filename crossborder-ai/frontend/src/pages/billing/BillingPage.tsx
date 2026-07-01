import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { CheckCircle2, CreditCard, ArrowRight, X, Copy, Check } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useAuthStore } from '@/stores/authStore'
import apiClient from '@/api/client'

interface Plan {
  id: string
  name: string
  price: number
  price_label: string
  description: string
  features: string[]
  recommended: boolean
}

export default function BillingPage() {
  const { user } = useAuthStore()
  const [selectedPlan, setSelectedPlan] = useState<Plan | null>(null)
  const [copied, setCopied] = useState(false)

  const { data } = useQuery({
    queryKey: ['plans'],
    queryFn: async () => {
      const res = await apiClient.get('/billing/plans')
      return res.data.plans as Plan[]
    },
  })

  const plans = data || []

  const handleCopy = () => {
    navigator.clipboard.writeText('VeyaShip 套餐升级')
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      <div className="text-center max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold tracking-tight">选择套餐</h1>
        <p className="text-muted-foreground mt-2">按需选择，随时升级</p>
      </div>

      {/* 当前套餐 */}
      {user && (
        <div className="text-center text-sm text-muted-foreground">
          当前套餐：<Badge variant="secondary" className="capitalize">{user.plan}</Badge>
          {' '}｜可用积分：<Badge variant="secondary">{user.credits_remaining}</Badge>
        </div>
      )}

      {/* 套餐对比 */}
      <div className="grid gap-6 md:grid-cols-3 max-w-4xl mx-auto">
        {plans.map((plan) => (
          <Card
            key={plan.id}
            className={`relative ${plan.recommended ? 'border-primary shadow-lg ring-1 ring-primary' : ''} ${plan.id === user?.plan ? 'border-emerald-500' : ''}`}
          >
            {plan.recommended && (
              <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                <Badge>推荐</Badge>
              </div>
            )}
            {plan.id === user?.plan && (
              <div className="absolute -top-3 right-3">
                <Badge variant="success">当前套餐</Badge>
              </div>
            )}
            <CardHeader className="text-center pb-2">
              <CardTitle className="text-xl">{plan.name}</CardTitle>
              <p className="text-3xl font-bold mt-2">{plan.price_label}</p>
              <p className="text-sm text-muted-foreground mt-1">{plan.description}</p>
            </CardHeader>
            <CardContent className="space-y-4">
              <ul className="space-y-2">
                {plan.features.map((f, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm">
                    <CheckCircle2 className="h-4 w-4 text-emerald-500 shrink-0 mt-0.5" />
                    {f}
                  </li>
                ))}
              </ul>
              {plan.id !== 'free' && plan.id !== user?.plan && (
                <Button
                  className="w-full"
                  onClick={() => setSelectedPlan(plan)}
                >
                  {plan.price === 0 ? '免费开通' : '立即开通'}
                  <ArrowRight className="h-4 w-4 ml-1" />
                </Button>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* 付款弹窗 */}
      {selectedPlan && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="max-w-md w-full relative">
            <Button variant="ghost" size="icon" className="absolute right-2 top-2"
              onClick={() => setSelectedPlan(null)}>
              <X className="h-4 w-4" />
            </Button>
            <CardHeader className="text-center">
              <CardTitle className="text-lg">开通 {selectedPlan.name} 套餐</CardTitle>
              <p className="text-2xl font-bold text-primary mt-2">{selectedPlan.price_label}</p>
            </CardHeader>
            <CardContent className="space-y-4 text-center">
              <div className="rounded-lg bg-muted p-6">
                <p className="text-sm text-muted-foreground mb-4">请扫描下方二维码付款</p>
                <div className="w-48 h-48 bg-muted-foreground/10 mx-auto rounded-lg flex items-center justify-center border-2 border-dashed">
                  <CreditCard className="h-12 w-12 text-muted-foreground/40" />
                </div>
                <p className="text-xs text-muted-foreground mt-3">
                  把你的微信/支付宝收款码放上去
                </p>
              </div>

              <div className="text-sm text-left space-y-2 bg-muted/50 rounded-lg p-3">
                <p className="font-medium">付款后请：</p>
                <ol className="text-muted-foreground space-y-1 list-decimal list-inside">
                  <li>截图保存付款凭证</li>
                  <li>扫码添加微信：<span className="font-medium text-foreground">你的微信号</span>
                    <Button variant="ghost" size="icon" className="h-5 w-5 inline-flex ml-1" onClick={handleCopy}>
                      {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                    </Button>
                  </li>
                  <li>发送截图，我帮你开通套餐</li>
                </ol>
              </div>

              <p className="text-xs text-muted-foreground">
                通常 30 分钟内处理，工作时间更快
              </p>
            </CardContent>
          </Card>
        </div>
      )}
    </motion.div>
  )
}
