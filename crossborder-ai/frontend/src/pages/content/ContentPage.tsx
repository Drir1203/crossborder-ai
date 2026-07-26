import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Sparkles, Copy, CheckCircle2, Loader2, AlertCircle, Package, Globe, Image as ImageIcon, ShoppingBag, ExternalLink } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import apiClient from '@/api/client'

interface Product {
  id: string
  title: string | null
  price: number | null
  shop_name: string | null
  main_image_url: string | null
}

interface GenerateResult {
  title: string
  description: string
  bullet_points: string[]
  seo_title: string
  seo_description: string
  image_url: string
}

const PLATFORMS = [
  { id: 'amazon', label: 'Amazon' },
  { id: 'ebay', label: 'eBay' },
  { id: 'shopify', label: 'Shopify' },
  { id: 'etsy', label: 'Etsy' },
  { id: 'shein', label: 'SHEIN' },
  { id: 'temu', label: 'Temu' },
  { id: 'tiktok', label: 'TikTok Shop' },
  { id: 'aliexpress', label: 'AliExpress' },
  { id: 'walmart', label: 'Walmart' },
  { id: 'shopee', label: 'Shopee' },
  { id: 'lazada', label: 'Lazada' },
]

const TONES = [
  { id: 'professional', label: '专业' },
  { id: 'casual', label: '随意' },
  { id: 'luxury', label: '高端' },
  { id: 'friendly', label: '亲切' },
  { id: 'persuasive', label: '说服力' },
  { id: 'humorous', label: '幽默' },
  { id: 'luxury_minimal', label: '极简高端' },
  { id: 'urgent', label: '限时抢购' },
  { id: 'custom', label: '自定义' },
]

const LANGUAGES = [
  { id: 'en', label: 'English (US/UK/AU)' },
  { id: 'ja', label: '日本語' },
  { id: 'es', label: 'Español' },
  { id: 'fr', label: 'Français' },
  { id: 'de', label: 'Deutsch' },
  { id: 'it', label: 'Italiano' },
  { id: 'pt', label: 'Português' },
  { id: 'nl', label: 'Nederlands' },
  { id: 'sv', label: 'Svenska' },
  { id: 'pl', label: 'Polski' },
  { id: 'tr', label: 'Türkçe' },
  { id: 'ar', label: 'العربية' },
  { id: 'ko', label: '한국어' },
  { id: 'zh', label: '中文' },
  { id: 'vi', label: 'Tiếng Việt' },
  { id: 'th', label: 'ไทย' },
  { id: 'ms', label: 'Bahasa Melayu' },
]

export default function ContentPage() {
  const [searchParams] = useSearchParams()
  const [selectedProduct, setSelectedProduct] = useState(searchParams.get('product') || '')
  const [platform, setPlatform] = useState(searchParams.get('platform') || 'amazon')
  const [tone, setTone] = useState('professional')
  const [language, setLanguage] = useState('en')
  const [generateImage, setGenerateImage] = useState(false)
  const [imagePrompt, setImagePrompt] = useState('')
  const [expertMode, setExpertMode] = useState(false)
  const [customTone, setCustomTone] = useState('')
  const [copied, setCopied] = useState('')
  const [selectedChannel, setSelectedChannel] = useState('')

  // 商品列表
  const { data: products } = useQuery({
    queryKey: ['products-for-content'],
    queryFn: async () => {
      const res = await apiClient.get('/products', { params: { page_size: 50 } })
      return res.data.items as Product[]
    },
  })

  // Shopify 店铺列表
  const { data: channels } = useQuery({
    queryKey: ['shopify-channels'],
    queryFn: async () => {
      const res = await apiClient.get('/shopify/channels')
      return res.data
    },
  })

  // 发布到 Shopify
  const publishMutation = useMutation({
    mutationFn: async () => {
      const res = await apiClient.post('/shopify/push', {
        product_id: selectedProduct,
        channel_id: selectedChannel,
      })
      return res.data
    },
  })

  const handlePublish = () => {
    if (!selectedProduct || !selectedChannel) return
    publishMutation.mutate()
  }

  // AI 生成
  const generateMutation = useMutation({
    mutationFn: async () => {
      const actualTone = tone === 'custom' ? (customTone || 'professional') : tone
      const res = await apiClient.post('/content/generate', {
        product_id: selectedProduct,
        platform,
        tone: actualTone,
        language,
        generate_image: generateImage,
        image_prompt: imagePrompt || undefined,
        expert_mode: expertMode,
      })
      return res.data as GenerateResult
    },
  })

  const copyText = (text: string, label: string) => {
    navigator.clipboard.writeText(text)
    setCopied(label)
    setTimeout(() => setCopied(''), 2000)
  }

  const selected = products?.find((p) => p.id === selectedProduct)

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <Sparkles className="h-6 w-6 text-primary" />
            AI 生成 Listing
          </h1>
          <p className="text-muted-foreground">选择商品，AI 自动生成标题、描述、卖点</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* 左侧：配置区 */}
        <div className="space-y-4 lg:col-span-1">
          {/* 选择商品 */}
          <Card>
            <CardHeader><CardTitle className="text-sm">选择商品</CardTitle></CardHeader>
            <CardContent className="space-y-2">
              {products?.length === 0 ? (
                <p className="text-sm text-muted-foreground">还没有商品，先去录入吧</p>
              ) : (
                <select
                  value={selectedProduct}
                  onChange={(e) => setSelectedProduct(e.target.value)}
                  className="w-full rounded-md border bg-background px-3 py-2 text-sm"
                >
                  <option value="">-- 选择商品 --</option>
                  {products?.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.title?.slice(0, 40) || '无标题'}
                    </option>
                  ))}
                </select>
              )}
              {selected && (
                <div className="text-xs text-muted-foreground">
                  <p>价格: {selected.price ? `¥${selected.price}` : '-'}</p>
                  <p>店铺: {selected.shop_name || '-'}</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* 平台选择 */}
          <Card>
            <CardHeader><CardTitle className="text-sm">目标平台</CardTitle></CardHeader>
            <CardContent className="flex flex-wrap gap-2">
              {PLATFORMS.map((p) => (
                <Badge
                  key={p.id}
                  variant={platform === p.id ? 'default' : 'outline'}
                  className="cursor-pointer"
                  onClick={() => setPlatform(p.id)}
                >
                  {p.label}
                </Badge>
              ))}
            </CardContent>
          </Card>

          {/* 语气选择 */}
          <Card>
            <CardHeader><CardTitle className="text-sm">语气风格</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              <div className="flex flex-wrap gap-2">
                {TONES.map((t) => (
                  <Badge
                    key={t.id}
                    variant={tone === t.id ? 'default' : 'outline'}
                    className="cursor-pointer"
                    onClick={() => setTone(t.id)}
                  >
                    {t.label}
                  </Badge>
                ))}
              </div>
              {tone === 'custom' && (
                <Input
                  placeholder="输入自定义语气，例如：夸张促销、环保理念、科技感..."
                  value={customTone}
                  onChange={(e) => setCustomTone(e.target.value)}
                />
              )}
            </CardContent>
          </Card>

          {/* 语言选择 */}
          <Card>
            <CardHeader><CardTitle className="text-sm">输出语言</CardTitle></CardHeader>
            <CardContent className="flex flex-wrap gap-2">
              {LANGUAGES.map((l) => (
                <Badge
                  key={l.id}
                  variant={language === l.id ? 'default' : 'outline'}
                  className="cursor-pointer"
                  onClick={() => setLanguage(l.id)}
                >
                  <Globe className="h-3 w-3 mr-1" />
                  {l.label}
                </Badge>
              ))}
            </CardContent>
          </Card>

          {/* 专家模式 */}
          <Card>
            <CardHeader><CardTitle className="text-sm">生成模式</CardTitle></CardHeader>
            <CardContent>
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" checked={expertMode} onChange={(e) => setExpertMode(e.target.checked)}
                  className="rounded border-gray-300" />
                <span className="text-sm">专家模式（多轮自检+优化，质量更高但较慢）</span>
              </label>
            </CardContent>
          </Card>

          {/* 生成主图 */}
          <Card>
            <CardHeader><CardTitle className="text-sm">商品主图</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" checked={generateImage} onChange={(e) => setGenerateImage(e.target.checked)}
                  className="rounded border-gray-300" />
                <span className="text-sm">AI 生成商品主图（FLUX 模型）</span>
              </label>
              {generateImage && (
                <Input
                  value={imagePrompt}
                  onChange={(e) => setImagePrompt(e.target.value)}
                  placeholder="图片描述（留空自动根据商品标题生成）"
                  className="text-sm"
                />
              )}
            </CardContent>
          </Card>

          <Button
            className="w-full"
            size="lg"
            disabled={!selectedProduct || generateMutation.isPending}
            onClick={() => generateMutation.mutate()}
          >
            {generateMutation.isPending ? (
              <><Loader2 className="mr-2 h-4 w-4 animate-spin" />AI 生成中...</>
            ) : (
              <><Sparkles className="mr-2 h-4 w-4" />AI 生成 Listing</>
            )}
          </Button>
        </div>

        {/* 右侧：结果区 */}
        <div className="space-y-4 lg:col-span-2">
          {generateMutation.isError && (
            <Card className="border-destructive/50">
              <CardContent className="pt-6 flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-destructive shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-destructive">生成失败</p>
                  <p className="text-sm text-muted-foreground mt-1">
                    {(generateMutation.error as any)?.response?.data?.detail || '请稍后重试'}
                  </p>
                </div>
              </CardContent>
            </Card>
          )}

          {generateMutation.isPending && (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-16">
                <Loader2 className="h-8 w-8 animate-spin text-primary mb-4" />
                <p className="text-sm text-muted-foreground">AI 正在生成内容，请稍候...</p>
              </CardContent>
            </Card>
          )}

          {generateMutation.data && (
            <>
              {/* 生成的图片 */}
              {generateMutation.data.image_url && (
                <Card>
                  <CardHeader><CardTitle className="text-sm flex items-center gap-2">
                    <ImageIcon className="h-4 w-4" />生成的主图
                  </CardTitle></CardHeader>
                  <CardContent>
                    <img src={generateMutation.data.image_url} alt="Generated product image"
                      className="w-full max-w-sm rounded-lg border" />
                  </CardContent>
                </Card>
              )}
              {/* 标题 */}
              <Card>
                <CardHeader className="flex flex-row items-start justify-between">
                  <CardTitle className="text-sm">商品标题</CardTitle>
                  <Button variant="ghost" size="icon" onClick={() => copyText(generateMutation.data.title, 'title')}>
                    {copied === 'title' ? <CheckCircle2 className="h-4 w-4 text-emerald-500" /> : <Copy className="h-4 w-4" />}
                  </Button>
                </CardHeader>
                <CardContent>
                  <p className="text-sm">{generateMutation.data.title || '无'}</p>
                </CardContent>
              </Card>

              {/* 卖点 */}
              <Card>
                <CardHeader className="flex flex-row items-start justify-between">
                  <CardTitle className="text-sm">卖点（Bullet Points）</CardTitle>
                  <Button variant="ghost" size="icon" onClick={() => copyText(generateMutation.data.bullet_points.join('\n'), 'bullets')}>
                    {copied === 'bullets' ? <CheckCircle2 className="h-4 w-4 text-emerald-500" /> : <Copy className="h-4 w-4" />}
                  </Button>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-1">
                    {generateMutation.data.bullet_points.map((b, i) => (
                      <li key={i} className="text-sm flex items-start gap-2">
                        <span className="text-primary mt-1.5 h-1.5 w-1.5 rounded-full bg-primary shrink-0" />
                        {b}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              {/* 描述 */}
              <Card>
                <CardHeader className="flex flex-row items-start justify-between">
                  <CardTitle className="text-sm">商品描述</CardTitle>
                  <Button variant="ghost" size="icon" onClick={() => copyText(generateMutation.data.description, 'desc')}>
                    {copied === 'desc' ? <CheckCircle2 className="h-4 w-4 text-emerald-500" /> : <Copy className="h-4 w-4" />}
                  </Button>
                </CardHeader>
                <CardContent>
                  <p className="text-sm whitespace-pre-wrap">{generateMutation.data.description || '无'}</p>
                </CardContent>
              </Card>

              {/* SEO */}
              {(generateMutation.data.seo_title || generateMutation.data.seo_description) && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm">SEO 优化</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {generateMutation.data.seo_title && (
                      <div>
                        <p className="text-xs text-muted-foreground mb-1">SEO 标题</p>
                        <div className="flex items-start justify-between gap-2">
                          <p className="text-sm">{generateMutation.data.seo_title}</p>
                          <Button variant="ghost" size="icon" className="shrink-0" onClick={() => copyText(generateMutation.data.seo_title, 'seo_title')}>
                            {copied === 'seo_title' ? <CheckCircle2 className="h-4 w-4 text-emerald-500" /> : <Copy className="h-4 w-4" />}
                          </Button>
                        </div>
                      </div>
                    )}
                    {generateMutation.data.seo_description && (
                      <div>
                        <p className="text-xs text-muted-foreground mb-1">SEO 描述</p>
                        <div className="flex items-start justify-between gap-2">
                          <p className="text-sm">{generateMutation.data.seo_description}</p>
                          <Button variant="ghost" size="icon" className="shrink-0" onClick={() => copyText(generateMutation.data.seo_description, 'seo_desc')}>
                            {copied === 'seo_desc' ? <CheckCircle2 className="h-4 w-4 text-emerald-500" /> : <Copy className="h-4 w-4" />}
                          </Button>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}

              {/* 原文对照 */}
              {selected && language !== 'zh' && (
                <Card className="border-blue-500/20 bg-blue-500/5">
                  <CardHeader>
                    <CardTitle className="text-sm flex items-center gap-2 text-blue-600">
                      <Globe className="h-4 w-4" />
                      原文 vs 译文对照
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid md:grid-cols-2 gap-4">
                      <div className="space-y-3">
                        <p className="text-xs font-medium text-muted-foreground">原文（中文）</p>
                        <div className="rounded-lg border bg-background p-3 space-y-1">
                          <p className="text-sm font-medium">{selected.title || '-'}</p>
                          {selected.price != null && <p className="text-xs text-muted-foreground">价格：¥{selected.price}</p>}
                          {selected.shop_name && <p className="text-xs text-muted-foreground">店铺：{selected.shop_name}</p>}
                        </div>
                      </div>
                      <div className="space-y-3">
                        <p className="text-xs font-medium text-muted-foreground">译文（{language.toUpperCase()}）</p>
                        <div className="rounded-lg border bg-background p-3 space-y-1">
                          <p className="text-sm font-medium">{generateMutation.data.title || '-'}</p>
                          {generateMutation.data.bullet_points?.slice(0, 3).map((b: string, i: number) => (
                            <p key={i} className="text-xs text-muted-foreground">• {b}</p>
                          ))}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
            </>
          )}

          {generateMutation.data && channels && channels.length > 0 && (
            <Card className="border-emerald-500/20 bg-emerald-500/5">
              <CardHeader>
                <CardTitle className="text-sm flex items-center gap-2">
                  <Globe className="h-4 w-4 text-emerald-500" />
                  发布到 Shopify
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <select
                  value={selectedChannel}
                  onChange={(e) => setSelectedChannel(e.target.value)}
                  className="w-full rounded-md border bg-background px-3 py-2 text-sm"
                >
                  <option value="">-- 选择店铺 --</option>
                  {channels.map((c: any) => (
                    <option key={c.id} value={c.id}>{c.shop_name}</option>
                  ))}
                </select>
                <Button
                  className="w-full"
                  disabled={!selectedChannel || publishMutation.isPending}
                  onClick={handlePublish}
                >
                  {publishMutation.isPending ? (
                    <><Loader2 className="mr-2 h-4 w-4 animate-spin" />发布中...</>
                  ) : (
                    <><ShoppingBag className="mr-2 h-4 w-4" />发布到 Shopify</>
                  )}
                </Button>
                {publishMutation.data && (
                  <p className="text-sm text-emerald-600 flex items-center gap-1">
                    <CheckCircle2 className="h-4 w-4" />{publishMutation.data.message}
                  </p>
                )}
                {publishMutation.error && (
                  <p className="text-sm text-destructive flex items-center gap-1">
                    <AlertCircle className="h-4 w-4" />
                    {(publishMutation.error as any)?.response?.data?.detail?.message?.substring?.(0, 100) || '发布失败'}
                  </p>
                )}
              </CardContent>
            </Card>
          )}

          {!generateMutation.data && !generateMutation.isPending && (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-20 text-muted-foreground">
                <Sparkles className="h-12 w-12 mb-4 opacity-30" />
                <p className="text-sm">选择一个商品，点击「AI 生成 Listing」</p>
                <p className="text-xs mt-1">AI 会自动生成标题、描述和卖点</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </motion.div>
  )
}
