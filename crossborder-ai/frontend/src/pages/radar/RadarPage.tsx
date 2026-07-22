import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import {
  Radar,
  Link as LinkIcon,
  Loader2,
  AlertCircle,
  CheckCircle2,
  ExternalLink,
  DollarSign,
  ShoppingBag,
  Store,
  BarChart3,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import apiClient from '@/api/client'

/**
 * RadarPage - 竞品分析（F6 Radar）
 *
 * 功能：
 * 1. 输入竞品 1688 链接 → 自动抓取竞品信息
 * 2. 展示竞品的标题、价格、销量、店铺名
 * 3. 帮助卖家做竞品对比分析
 *
 * 数据来源：通过 Onebound API 抓取 1688 商品详情
 */

// ── 类型定义 ──────────────────────────────────────────────────
/** 竞品数据结构 */
interface CompetitorData {
  url: string
  title: string | null
  main_image_url: string | null
  price: number | null
  sales_count: number | null
  shop_name: string | null
}

/** API 返回的竞品数据外层结构 */
interface RadarResponse {
  competitor: CompetitorData
}


export default function RadarPage() {
  // ── 状态管理 ──────────────────────────────────────────────
  const [url, setUrl] = useState('')
  const [result, setResult] = useState<CompetitorData | null>(null)

  // ── Mutation：抓取竞品数据 ────────────────────────────────
  const scrapeMutation = useMutation({
    mutationFn: async (targetUrl: string) => {
      const res = await apiClient.get<RadarResponse>('/radar/scrape', {
        params: { url: targetUrl },
      })
      return res.data
    },
    onSuccess: (data) => {
      // 保存结果到本地状态，方便页面展示
      setResult(data.competitor)
    },
  })

  // ── 处理抓取 ──────────────────────────────────────────────
  const handleScrape = () => {
    if (!url.trim()) return
    setResult(null)       // 清空上一次结果
    scrapeMutation.mutate(url.trim())
  }

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="max-w-3xl mx-auto space-y-6">
      {/* ── 页面标题 ────────────────────────────────────────── */}
      <div className="text-center">
        <h1 className="text-2xl font-bold tracking-tight flex items-center justify-center gap-2">
          <Radar className="h-6 w-6 text-primary" />
          竞品分析（F6 Radar）
        </h1>
        <p className="text-muted-foreground mt-1">
          输入竞品的 1688 链接，查看其标题、价格、销量等信息
        </p>
      </div>

      {/* ── 输入区域 ────────────────────────────────────────── */}
      <Card>
        <CardContent className="pt-6 space-y-4">
          {/* URL 输入框 */}
          <div className="flex gap-3">
            <div className="relative flex-1">
              <LinkIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleScrape()}
                placeholder="粘贴竞品 1688 链接，如 https://detail.1688.com/offer/..."
                className="pl-10"
              />
            </div>
            <Button
              onClick={handleScrape}
              disabled={!url.trim() || scrapeMutation.isPending}
              className="shrink-0"
            >
              {scrapeMutation.isPending ? (
                <><Loader2 className="mr-2 h-4 w-4 animate-spin" />分析中...</>
              ) : (
                <><Radar className="mr-2 h-4 w-4" />竞品分析</>
              )}
            </Button>
          </div>

          {/* 错误提示：抓取失败时显示 */}
          {scrapeMutation.isError && (
            <div className="flex items-start gap-3 p-3 rounded-md bg-destructive/10 text-sm">
              <AlertCircle className="h-4 w-4 mt-0.5 shrink-0 text-destructive" />
              <div>
                <p className="font-medium text-destructive">抓取失败</p>
                <p className="text-muted-foreground mt-1">
                  {(scrapeMutation.error as any)?.response?.data?.detail || '无法获取竞品信息，请检查链接是否正确'}
                </p>
              </div>
            </div>
          )}

          {/* 加载状态 */}
          {scrapeMutation.isPending && (
            <div className="flex items-center justify-center py-6">
              <Loader2 className="h-6 w-6 animate-spin text-primary" />
              <span className="ml-2 text-sm text-muted-foreground">正在抓取竞品数据...</span>
            </div>
          )}
        </CardContent>
      </Card>

      {/* ── 竞品数据展示 ────────────────────────────────────── */}
      {result && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          {/* 商品图片 & 标题 */}
          <Card>
            <CardContent className="pt-6">
              <div className="flex gap-4">
                {/* 左侧图片 */}
                <div className="w-32 h-32 rounded-lg bg-muted flex items-center justify-center overflow-hidden shrink-0">
                  {result.main_image_url ? (
                    <img src={result.main_image_url} alt={result.title || ''}
                      className="w-full h-full object-cover" />
                  ) : (
                    <ShoppingBag className="h-8 w-8 text-muted-foreground/40" />
                  )}
                </div>
                {/* 右侧信息 */}
                <div className="flex-1 space-y-2">
                  <h2 className="font-semibold text-base leading-snug">
                    {result.title || '未获取到标题'}
                  </h2>
                  {/* 价格 */}
                  {result.price != null && (
                    <div className="flex items-center gap-1 text-lg font-bold text-primary">
                      <DollarSign className="h-4 w-4" />
                      ¥{result.price.toFixed(2)}
                    </div>
                  )}
                  {/* 店铺 & 销量 */}
                  <div className="flex flex-wrap gap-3">
                    {result.shop_name && (
                      <Badge variant="secondary" className="gap-1">
                        <Store className="h-3 w-3" />
                        {result.shop_name}
                      </Badge>
                    )}
                    {result.sales_count != null && (
                      <Badge variant="secondary" className="gap-1">
                        <BarChart3 className="h-3 w-3" />
                        已售 {result.sales_count}
                      </Badge>
                    )}
                  </div>
                  {/* 原始链接 */}
                  {result.url && (
                    <a href={result.url} target="_blank" rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-sm text-primary hover:underline mt-2">
                      <ExternalLink className="h-3 w-3" />
                      查看 1688 原页面
                    </a>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 分析结论卡片 */}
          <Card className="bg-primary/5 border-primary/20">
            <CardHeader>
              <CardTitle className="text-sm flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                分析结果
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm space-y-1 text-muted-foreground">
              <p>✅ 成功获取竞品信息，以下是关键数据：</p>
              <ul className="list-disc list-inside space-y-1 mt-2">
                <li>商品标题：{result.title || '未获取'}</li>
                <li>参考价格：{result.price ? `¥${result.price.toFixed(2)}` : '未获取'}</li>
                <li>店铺名称：{result.shop_name || '未获取'}</li>
                <li>累计销量：{result.sales_count != null ? `${result.sales_count} 件` : '未获取'}</li>
              </ul>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* ── 使用说明（无数据时显示） ────────────────────────── */}
      {!result && !scrapeMutation.isPending && !scrapeMutation.isError && (
        <Card className="bg-muted/30">
          <CardContent className="py-8 text-center text-muted-foreground">
            <Radar className="h-12 w-12 mx-auto mb-3 opacity-30" />
            <p className="text-sm">输入竞品 1688 链接，点击「竞品分析」</p>
            <p className="text-xs mt-1">系统会自动抓取竞品的价格、销量、店铺信息</p>
          </CardContent>
        </Card>
      )}
    </motion.div>
  )
}
