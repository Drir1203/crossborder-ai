import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Link as LinkIcon,
  Search,
  ExternalLink,
  ShoppingBag,
  Loader2,
  AlertCircle,
  CheckCircle2,
  Package,
  Plus,
  FileInput,
  Settings,
  Sparkles,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import apiClient from '@/api/client'

interface Product {
  id: string
  url: string
  title: string | null
  main_image_url: string | null
  price: number | null
  sales_count: number | null
  shop_name: string | null
  created_at: string
  updated_at: string
}

interface ProductListResponse {
  items: Product[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export default function ProductsPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [url, setUrl] = useState('')
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [showManual, setShowManual] = useState(false)

  // 手动输入表单
  const [manualForm, setManualForm] = useState({
    url: '',
    title: '',
    price: '',
    shop_name: '',
    main_image_url: '',
    sales_count: '',
  })

  // 商品列表
  const { data, isLoading } = useQuery<ProductListResponse>({
    queryKey: ['products', page, search],
    queryFn: async () => {
      const params: Record<string, unknown> = { page, page_size: 20 }
      if (search) params.search = search
      const res = await apiClient.get('/products', { params })
      return res.data
    },
  })

  // 自动抓取
  const scrapeMutation = useMutation({
    mutationFn: async (productUrl: string) => {
      const res = await apiClient.post('/products/scrape', { url: productUrl })
      return res.data
    },
    onSuccess: () => { setUrl(''); queryClient.invalidateQueries({ queryKey: ['products'] }) },
  })

  // 手动创建
  const manualMutation = useMutation({
    mutationFn: async (data: Record<string, unknown>) => {
      const res = await apiClient.post('/products/manual', data)
      return res.data
    },
    onSuccess: () => {
      setManualForm({ url: '', title: '', price: '', shop_name: '', main_image_url: '', sales_count: '' })
      setShowManual(false)
      queryClient.invalidateQueries({ queryKey: ['products'] })
    },
  })

  const handleScrape = () => {
    if (!url.trim()) return
    scrapeMutation.mutate(url.trim())
  }

  const handleManualSubmit = () => {
    if (!manualForm.url.trim()) return
    manualMutation.mutate({
      url: manualForm.url,
      title: manualForm.title || null,
      price: manualForm.price ? parseFloat(manualForm.price) : null,
      shop_name: manualForm.shop_name || null,
      main_image_url: manualForm.main_image_url || null,
      sales_count: manualForm.sales_count ? parseInt(manualForm.sales_count) : null,
    })
  }

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      {/* 标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <Package className="h-6 w-6 text-primary" />
            商品管理
          </h1>
          <p className="text-muted-foreground">粘贴 1688 链接自动抓取，或手动录入商品信息</p>
        </div>
        <Button variant="outline" onClick={() => setShowManual(!showManual)}>
          <FileInput className="mr-2 h-4 w-4" />
          手动录入
        </Button>
      </div>

      {/* 自动抓取 */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-3">
            <div className="relative flex-1">
              <LinkIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="粘贴 1688 商品链接，例如 https://detail.1688.com/offer/..."
                className="pl-10"
                onKeyDown={(e) => e.key === 'Enter' && handleScrape()}
              />
            </div>
            <Button onClick={handleScrape} disabled={!url.trim() || scrapeMutation.isPending} className="shrink-0">
              {scrapeMutation.isPending ? (
                <><Loader2 className="mr-2 h-4 w-4 animate-spin" />抓取中...</>
              ) : (
                <><ExternalLink className="mr-2 h-4 w-4" />自动抓取</>
              )}
            </Button>
          </div>

          {scrapeMutation.data && (
            <div className="mt-3 flex items-center gap-2 text-sm text-emerald-600">
              <CheckCircle2 className="h-4 w-4" />
              {scrapeMutation.data.message}
            </div>
          )}
          {scrapeMutation.error && (
            <div className="mt-3 rounded-md bg-amber-500/10 border border-amber-500/20 p-4 text-sm space-y-3">
              <div className="flex items-start gap-2">
                <AlertCircle className="h-4 w-4 mt-0.5 shrink-0 text-amber-600" />
                <div>
                  <p className="font-medium text-amber-600">1688 无法自动抓取</p>
                  <p className="text-muted-foreground mt-1">
                    {(scrapeMutation.error as any)?.response?.data?.detail || '获取商品信息失败'}
                  </p>
                </div>
              </div>
              <div className="flex gap-2 flex-wrap">
                <Button size="sm" variant="outline" onClick={() => { setShowManual(true); setManualForm({ ...manualForm, url }) }}>
                  📝 手动录入此商品
                </Button>
                <Button size="sm" variant="outline" onClick={() => navigate('/settings')}>
                  ⚙️ 查看配置说明
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 手动录入表单 */}
      {showManual && (
        <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Plus className="h-4 w-4" />
                手动录入商品
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2 sm:col-span-2">
                  <Label>商品链接 *</Label>
                  <Input value={manualForm.url} onChange={(e) => setManualForm({ ...manualForm, url: e.target.value })} placeholder="https://detail.1688.com/offer/..." />
                </div>
                <div className="space-y-2">
                  <Label>商品标题</Label>
                  <Input value={manualForm.title} onChange={(e) => setManualForm({ ...manualForm, title: e.target.value })} placeholder="输入商品名称" />
                </div>
                <div className="space-y-2">
                  <Label>价格</Label>
                  <Input value={manualForm.price} onChange={(e) => setManualForm({ ...manualForm, price: e.target.value })} placeholder="例如 29.90" />
                </div>
                <div className="space-y-2">
                  <Label>店铺名</Label>
                  <Input value={manualForm.shop_name} onChange={(e) => setManualForm({ ...manualForm, shop_name: e.target.value })} placeholder="店铺名称" />
                </div>
                <div className="space-y-2">
                  <Label>销量</Label>
                  <Input value={manualForm.sales_count} onChange={(e) => setManualForm({ ...manualForm, sales_count: e.target.value })} placeholder="例如 1000" />
                </div>
                <div className="space-y-2 sm:col-span-2">
                  <Label>主图 URL</Label>
                  <Input value={manualForm.main_image_url} onChange={(e) => setManualForm({ ...manualForm, main_image_url: e.target.value })} placeholder="图片链接（可选）" />
                </div>
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setShowManual(false)}>取消</Button>
                <Button onClick={handleManualSubmit} disabled={!manualForm.url.trim() || manualMutation.isPending}>
                  {manualMutation.isPending ? '保存中...' : '保存商品'}
                </Button>
              </div>
              {manualMutation.error && (
                <p className="text-sm text-destructive">
                  {(manualMutation.error as any)?.response?.data?.detail || '保存失败'}
                </p>
              )}
              {manualMutation.data && (
                <p className="text-sm text-emerald-600 flex items-center gap-1">
                  <CheckCircle2 className="h-4 w-4" /> 保存成功
                </p>
              )}
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* 搜索 */}
      <div className="flex items-center gap-2">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input value={search} onChange={(e) => { setSearch(e.target.value); setPage(1) }} placeholder="搜索商品..." className="pl-10" />
        </div>
        {data && <span className="text-sm text-muted-foreground">共 {data.total} 个商品</span>}
      </div>

      {/* 商品列表 */}
      {isLoading ? (
        <div className="flex justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-muted-foreground" /></div>
      ) : data?.items?.length ? (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {data.items.map((product) => (
              <Card key={product.id} className="overflow-hidden transition-shadow hover:shadow-md cursor-pointer" onClick={() => navigate(`/products/${product.id}`)}>
                <div className="aspect-square bg-muted flex items-center justify-center overflow-hidden">
                  {product.main_image_url ? (
                    <img src={product.main_image_url} alt={product.title || ''} className="h-full w-full object-cover" />
                  ) : (
                    <ShoppingBag className="h-12 w-12 text-muted-foreground/40" />
                  )}
                </div>
                <CardContent className="p-4 space-y-2">
                  <p className="text-sm font-medium line-clamp-2 leading-snug min-h-[2.5em]">{product.title || '无标题'}</p>
                  <div className="flex items-center justify-between">
                    {product.price != null && <span className="text-lg font-bold text-primary">¥{product.price.toFixed(2)}</span>}
                    {product.sales_count != null && <Badge variant="secondary" className="text-xs">已售 {product.sales_count}</Badge>}
                  </div>
                  {product.shop_name && <p className="text-xs text-muted-foreground truncate">店铺: {product.shop_name}</p>}
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full mt-2"
                    onClick={() => navigate(`/content?product=${product.id}`)}
                  >
                    <Sparkles className="h-3 w-3 mr-1" />
                    AI 生成 Listing
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
          {data.total_pages > 1 && (
            <div className="flex justify-center gap-2">
              <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>上一页</Button>
              <span className="flex items-center text-sm text-muted-foreground px-2">{page} / {data.total_pages}</span>
              <Button variant="outline" size="sm" disabled={page >= data.total_pages} onClick={() => setPage(page + 1)}>下一页</Button>
            </div>
          )}
        </>
      ) : (
        <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
          <ShoppingBag className="h-12 w-12 mb-3 opacity-50" />
          <p className="text-sm">暂无商品数据</p>
          <p className="text-xs">粘贴 1688 链接自动抓取，或点击「手动录入」添加</p>
        </div>
      )}
    </motion.div>
  )
}
