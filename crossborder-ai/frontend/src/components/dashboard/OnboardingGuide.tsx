import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Store, Palette, Sparkles, CheckCircle2, ChevronRight, Rocket } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  isOnboardingSeen,
  markOnboardingSeen,
  useShopifyChannels,
  usePersonaFilled,
  useImageHistory,
} from './useOnboarding'

/**
 * OnboardingGuide - 新手三步激活引导（Dashboard 空状态主区块）
 *
 * 触发规则（满足其一就不再打扰）：
 *   1. localStorage 已有 veyaship_onboarded_seen 标记（跳过过）
 *   2. 已绑定 Shopify 店铺
 *   3. 图片历史中存在 completed 记录
 * 非强制阻断：右上角可随时「跳过」，引导卡仅占 Dashboard 一段，可关可滚。
 */
export default function OnboardingGuide() {
  const navigate = useNavigate()
  const [dismissed, setDismissed] = useState(false)

  // 真实信号：店铺 / 品牌调性 / 图片历史（失败即视为未完成，静默降级）
  const channels = useShopifyChannels()
  const persona = usePersonaFilled()
  const history = useImageHistory()

  const shopBound = !!channels.data && channels.data.length > 0
  const personaDone = persona.data === true
  const imageDone =
    !history.isError &&
    !!history.data &&
    history.data.some(
      (it) => it.status === 'completed' && Array.isArray(it.image_urls) && it.image_urls.length > 0,
    )

  // 首次挂载：等三个信号都落定再决定显隐，避免完成用户的引导闪烁
  const deciding = channels.isLoading || persona.isLoading || history.isLoading
  if (dismissed || deciding || shopBound || imageDone || isOnboardingSeen()) return null

  const steps = [
    {
      icon: Store,
      title: '绑定 Shopify 店铺',
      subtitle: '把店铺连进来，之后的商品上新、自动退款才有操作对象',
      path: '/app/shopify',
      cta: '去绑定',
      done: shopBound,
    },
    {
      icon: Palette,
      title: '设置品牌调性',
      subtitle: '告诉 AI 你的品牌风格与违禁词，生成的文案才像你亲手写的',
      path: '/app/settings',
      cta: '去设置',
      done: personaDone,
    },
    {
      icon: Sparkles,
      title: '生成第一张 AI 主图',
      subtitle: '用一句话描述商品，看到第一条产出，就验证了从想法到素材的整条链路',
      path: '/app/images',
      cta: '去生成',
      done: imageDone,
    },
  ]

  const doneCount = steps.filter((s) => s.done).length

  const handleSkip = () => {
    markOnboardingSeen()
    setDismissed(true)
  }

  return (
    <Card className="relative overflow-hidden border-primary/20 bg-gradient-to-br from-primary/10 via-glass to-glass">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground shadow">
              <Rocket className="h-4 w-4" />
            </span>
            <div>
              <CardTitle className="text-base">
                3 步跑通第一个「商品 → AI 素材」闭环
              </CardTitle>
              <CardDescription className="mt-0.5 text-xs">
                完成后，上新发布、文案撰写、商品配图都能自动完成，不用再逐条手工做
              </CardDescription>
            </div>
          </div>
          <Button variant="ghost" size="sm" className="h-7 px-2 text-xs text-muted-foreground shrink-0" onClick={handleSkip}>
            跳过引导
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-2">
        <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <span className="font-medium text-primary">已完成 {doneCount}/3</span>
          <span className="h-px flex-1 bg-border" />
        </div>

        {steps.map((step, index) => (
          <div
            key={step.path}
            onClick={!step.done ? () => navigate(step.path) : undefined}
            className={`flex items-center gap-3 rounded-xl border bg-background/70 px-3 py-2.5 transition-colors ${
              step.done
                ? 'border-emerald-500/20'
                : 'cursor-pointer hover:border-primary/40 hover:bg-background'
            }`}
          >
            <span className="flex shrink-0 items-center justify-center">
              {step.done ? (
                <CheckCircle2 className="h-6 w-6 text-emerald-500" />
              ) : (
                <span className="flex h-6 w-6 items-center justify-center rounded-full bg-primary/10 text-xs font-bold text-primary">
                  {index + 1}
                </span>
              )}
            </span>
            <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-muted/60 text-muted-foreground">
              <step.icon className="h-4 w-4" />
            </span>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium">{step.title}</p>
              <p className="text-xs text-muted-foreground truncate">{step.subtitle}</p>
            </div>
            {step.done ? (
              <Badge variant="success" className="shrink-0">已完成</Badge>
            ) : (
              <Button size="sm" className="h-8 gap-0.5 shrink-0">
                {step.cta}
                <ChevronRight className="h-3.5 w-3.5" />
              </Button>
            )}
          </div>
        ))}
      </CardContent>
    </Card>
  )
}
