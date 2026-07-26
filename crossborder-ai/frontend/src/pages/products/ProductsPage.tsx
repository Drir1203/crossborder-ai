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
  Trash2,
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
  Upload,
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
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [confirmDelete, setConfirmDelete] = useState<'single' | 'batch' | 'all' | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null)

  // 手动输入表单
  const [manualForm, setManualForm] = useState({
    url: '', title: '', price: '', shop_name: '', main_image_url: '', sales_count: '',
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

  // 删除单个
  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/products/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] })
      setSelected(new Set())
    },
  })

  // 批量删除
  const batchDeleteMutation = useMutation({
    mutationFn: async (ids: string[]) => {
      await apiClient.post('/products/batch-delete', { ids })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] })
      setSelected(new Set())
    },
  })

  // 全量删除
  const deleteAllMutation = useMutation({
    mutationFn: async () => {
      await apiClient.delete('/products')
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] })
      setSelected(new Set())
    },
  })

  const handleScrape = () => {
    if (!url.trim()) return
    scrapeMutation.mutate(url.trim())
  }

  const toggleSelect = (id: string) => {
    const next = new Set(selected)
    if (next.has(id)) next.delete(id)
    else next.add(id)
    setSelected(next)
  }

  const toggleAll = () => {
    if (!data?.items) return
    if (selected.size === data.items.length) {
      setSelected(new Set())
    } else {
      setSelected(new Set(data.items.map(p => p.id)))
    }
  }

  const handleDeleteClick = (id: string) => {
    setDeleteTarget(id)
    setConfirmDelete('single')
  }

  const executeDelete = () => {
    if (confirmDelete === 'single' && deleteTarget) {
      deleteMutation.mutate(deleteTarget)
    } else if (confirmDelete === 'batch') {
      batchDeleteMutation.mutate(Array.from(selected))
    } else if (confirmDelete === 'all') {
      deleteAllMutation.mutate()
    }
    setConfirmDelete(null)
    setDeleteTarget(null)
  }

  const isDeleting = deleteMutation.isPending || batchDeleteMutation.isPending || deleteAllMutation.isPending

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      {/* 标题 + 操作栏 */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <Package className="h-6 w-6 text-primary" />
            商品管理
          </h1>
          <p className="text-muted-foreground text-sm">粘贴商品链接自动抓取，或手动/CSV 批量录入自有商品</p>
        </div>
        <div className="flex gap-2">
          {selected.size > 0 && (
            <>
              <span className="text-sm text-muted-foreground self-center">已选 {selected.size} 个</span>
              <Button variant="destructive" size="sm" onClick={() => setConfirmDelete('batch')} className="gap-1">
                <Trash2 className="h-4 w-4" />删除选中
              </Button>
            </>
          )}
          {data && data.total > 0 && (
            <Button variant="outline" size="sm" onClick={() => setConfirmDelete('all')} className="gap-1 text-destructive">
              <Trash2 className="h-4 w-4" />删除全部
            </Button>
          )}
          <Button variant="outline" size="sm" onClick={() => navigate('/app/batch')} className="gap-1">
            <Upload className="mr-1 h-4 w-4" />CSV 批量导入
          </Button>
          <Button variant="outline" size="sm" onClick={() => setShowManual(!showManual)}>
            <FileInput className="mr-1 h-4 w-4" />手动录入
          </Button>
        </div>
      </div>

      {/* 确认弹窗 */}
      {confirmDelete && (
        <Card className={`${confirmDelete === 'all' ? 'border-destructive' : 'border-destructive/50'} bg-destructive/5`}>
          <CardContent className="pt-4 flex items-start justify-between">
            <div className="flex items-start gap-3">
              <AlertTriangle className="h-5 w-5 text-destructive mt-0.5 shrink-0" />
              <div>
                <p className="font-medium text-sm">
                  {confirmDelete === 'single' ? '确认删除此商品？' :
                   confirmDelete === 'batch' ? `确认删除选中的 ${selected.size} 个商品？` :
                   '确认删除全部商品？'}
                </p>
                <p className="text-xs text-muted-foreground mt-0.5">此操作不可撤销</p>
              </div>
            </div>
            <div className="flex gap-2 shrink-0">
              <Button size="sm" variant="destructive" onClick={executeDelete} disabled={isDeleting}>
                {isDeleting ? '删除中...' : '确认删除'}
              </Button>
              <Button size="sm" variant="outline" onClick={() => setConfirmDelete(null)}>取消</Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 自动抓取 */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-3">
            <div className="relative flex-1">
              <LinkIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="粘贴商品链接，或手动录入..."
                className="pl-10"
                onKeyDown={(e) => e.key === 'Enter' && handleScrape()}
              />
            </div>
            <Button onClick={handleScrape} disabled={!url.trim() || scrapeMutation.isPending}>
              {scrapeMutation.isPending ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />抓取中</> : <><ExternalLink className="mr-2 h-4 w-4" />自动抓取</>}
            </Button>
          </div>
          {scrapeMutation.data && <p className="mt-2 text-sm text-emerald-600 flex items-center gap-1"><CheckCircle2 className="h-4 w-4" />{scrapeMutation.data.message}</p>}
          {scrapeMutation.error && (
            <div className="mt-2 flex items-start gap-2 text-sm bg-amber-500/10 p-3 rounded-md">
              <AlertCircle className="h-4 w-4 mt-0.5 shrink-0 text-amber-600" />
              <div>
                <p className="text-amber-600 font-medium">抓取失败</p>
                <p className="text-muted-foreground">{(scrapeMutation.error as any)?.response?.data?.detail || '请稍后重试'}</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 手动录入 */}
      {showManual && (
        <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }}>
          <Card>
            <CardHeader><CardTitle className="flex items-center gap-2 text-base"><Plus className="h-4 w-4" />手动录入商品</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2 sm:col-span-2"><Label>商品链接 *</Label><Input value={manualForm.url} onChange={(e) => setManualForm({ ...manualForm, url: e.target.value })} /></div>
                <div className="space-y-2"><Label>标题</Label><Input value={manualForm.title} onChange={(e) => setManualForm({ ...manualForm, title: e.target.value })} /></div>
                <div className="space-y-2"><Label>价格</Label><Input value={manualForm.price} onChange={(e) => setManualForm({ ...manualForm, price: e.target.value })} /></div>
                <div className="space-y-2"><Label>店铺</Label><Input value={manualForm.shop_name} onChange={(e) => setManualForm({ ...manualForm, shop_name: e.target.value })} /></div>
                <div className="space-y-2"><Label>销量</Label><Input value={manualForm.sales_count} onChange={(e) => setManualForm({ ...manualForm, sales_count: e.target.value })} /></div>
              </div>
              <div className="flex gap-2 justify-end">
                <Button variant="outline" onClick={() => setShowManual(false)}>取消</Button>
                <Button onClick={() => manualMutation.mutate({ url: manualForm.url, title: manualForm.title || null, price: manualForm.price ? parseFloat(manualForm.price) : null, shop_name: manualForm.shop_name || null, sales_count: manualForm.sales_count ? parseInt(manualForm.sales_count) : null })} disabled={!manualForm.url.trim() || manualMutation.isPending}>
                  {manualMutation.isPending ? '保存中...' : '保存'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* 搜索 + 总数 */}
      <div className="flex items-center justify-between">
        <div className="relative max-w-sm flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input value={search} onChange={(e) => { setSearch(e.target.value); setPage(1) }} placeholder="搜索商品..." className="pl-10" />
        </div>
        {data && <span className="text-sm text-muted-foreground">{data.total} 个商品</span>}
      </div>

      {/* 全选 */}
      {data && data.items.length > 0 && (
        <label className="flex items-center gap-2 text-sm cursor-pointer">
          <input type="checkbox" checked={selected.size === data.items.length} onChange={toggleAll} className="rounded" />
          全选
        </label>
      )}

      {/* 商品列表 */}
      {isLoading ? (
        <div className="flex justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-muted-foreground" /></div>
      ) : data?.items?.length ? (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {data.items.map((product) => (
              <Card key={product.id} className="overflow-hidden transition-shadow hover:shadow-md">
                <div className="relative">
                  <div className="absolute top-2 left-2 z-10">
                    <input
                      type="checkbox"
                      checked={selected.has(product.id)}
                      onChange={() => toggleSelect(product.id)}
                      onClick={(e) => e.stopPropagation()}
                      className="rounded"
                    />
                  </div>
                  <div className="absolute top-2 right-2 z-10">
                    <button
                      onClick={(e) => { e.stopPropagation(); handleDeleteClick(product.id) }}
                      className="p-1.5 rounded-full bg-background/80 hover:bg-destructive/10 text-muted-foreground hover:text-destructive transition-colors"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  </div>
                  <div className="aspect-square bg-muted flex items-center justify-center cursor-pointer" onClick={() => navigate(`/app/products/${product.id}`)}>
                    {product.main_image_url ? (
                      <img src={product.main_image_url} alt="" className="h-full w-full object-cover" />
                    ) : (
                      <ShoppingBag className="h-12 w-12 text-muted-foreground/40" />
                    )}
                  </div>
                </div>
                <CardContent className="p-3 space-y-2" onClick={() => navigate(`/app/products/${product.id}`)}>
                  <p className="text-sm font-medium line-clamp-2 leading-snug h-10">{product.title || '无标题'}</p>
                  <div className="flex items-center justify-between">
                    {product.price != null && <span className="text-base font-bold text-primary">¥{product.price.toFixed(2)}</span>}
                    {product.sales_count != null && <Badge variant="secondary" className="text-xs">已售 {product.sales_count}</Badge>}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
          {data.total_pages > 1 && (
            <div className="flex justify-center gap-2 mt-4">
              <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>上一页</Button>
              <span className="flex items-center text-sm px-2 text-muted-foreground">{page} / {data.total_pages}</span>
              <Button variant="outline" size="sm" disabled={page >= data.total_pages} onClick={() => setPage(page + 1)}>下一页</Button>
            </div>
          )}
        </>
      ) : (
        <div className="flex flex-col items-center py-16 text-muted-foreground">
          <ShoppingBag className="h-12 w-12 mb-3 opacity-50" />
          <p className="text-sm">暂无商品</p>
          <p className="text-xs mt-1">粘贴 1688 链接或点击手动录入添加</p>
        </div>
      )}
    </motion.div>
  )
}
