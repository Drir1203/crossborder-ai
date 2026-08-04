import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import {
  ArrowLeft,
  ExternalLink,
  Sparkles,
  ShoppingBag,
  Globe,
  Loader2,
  Clock,
  ChevronDown,
  ChevronUp,
  Trash2,
  AlertTriangle,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import apiClient from '@/api/client'

const PLATFORMS = [
  { id: 'amazon', label: 'Amazon', color: 'bg-amber-500/10 text-amber-600' },
  { id: 'ebay', label: 'eBay', color: 'bg-amber-500/10 text-amber-500' },
  { id: 'shopify', label: 'Shopify', color: 'bg-emerald-500/10 text-emerald-600' },
  { id: 'etsy', label: 'Etsy', color: 'bg-orange-500/10 text-orange-600' },
  { id: 'shein', label: 'SHEIN', color: 'bg-green-600/10 text-green-600' },
  { id: 'temu', label: 'Temu', color: 'bg-red-500/10 text-red-600' },
  { id: 'tiktok', label: 'TikTok Shop', color: 'bg-purple-500/10 text-purple-600' },
  { id: 'aliexpress', label: 'AliExpress', color: 'bg-rose-500/10 text-rose-600' },
  { id: 'walmart', label: 'Walmart', color: 'bg-sky-500/10 text-sky-600' },
  { id: 'shopee', label: 'Shopee', color: 'bg-orange-600/10 text-orange-600' },
  { id: 'lazada', label: 'Lazada', color: 'bg-amber-500/10 text-amber-500' },
]

export default function ProductDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [showAllPlatforms, setShowAllPlatforms] = useState(false)

  const { data: product, isLoading } = useQuery({
    queryKey: ['product', id],
    queryFn: async () => {
      const res = await apiClient.get(`/products/${id}`)
      return res.data
    },
    enabled: !!id,
  })

  const { data: history } = useQuery({
    queryKey: ['product-history', id],
    queryFn: async () => {
      const res = await apiClient.get(`/products/${id}/history`)
      return res.data
    },
    enabled: !!id,
  })

  // 删除商品
  const deleteMutation = useMutation({
    mutationFn: async () => {
      await apiClient.delete(`/products/${id}`)
    },
    onSuccess: () => navigate('/app/products'),
  })
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)

  if (isLoading) {
    return (
      <div className="flex justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (!product) {
    return (
      <div className="flex flex-col items-center py-20 text-muted-foreground">
        <ShoppingBag className="h-12 w-12 mb-4 opacity-50" />
        <p>商品不存在</p>
        <Button variant="link" onClick={() => navigate('/app/products')}>返回商品列表</Button>
      </div>
    )
  }

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      {/* 返回按钮 */}
      <Button variant="ghost" size="sm" onClick={() => navigate('/app/products')}>
        <ArrowLeft className="h-4 w-4 mr-1" /> 返回商品列表
      </Button>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* 左：商品信息 */}
        <div className="space-y-4 lg:col-span-1">
          <Card>
            <div className="aspect-square bg-muted flex items-center justify-center overflow-hidden rounded-t-xl">
              {product.main_image_url ? (
                <img src={product.main_image_url} alt={product.title} className="h-full w-full object-cover" />
              ) : (
                <ShoppingBag className="h-16 w-16 text-muted-foreground/30" />
              )}
            </div>
            <CardContent className="p-4 space-y-3">
              <h1 className="font-semibold leading-snug">{product.title || '无标题'}</h1>
              <div className="flex items-center justify-between">
                {product.price != null && (
                  <span className="text-2xl font-bold text-primary">¥{product.price.toFixed(2)}</span>
                )}
                {product.sales_count != null && (
                  <Badge variant="secondary">已售 {product.sales_count}</Badge>
                )}
              </div>
              {product.shop_name && (
                <p className="text-sm text-muted-foreground">店铺: {product.shop_name}</p>
              )}
              <a
                href={product.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1 text-xs text-primary hover:underline"
              >
                <ExternalLink className="h-3 w-3" />
                查看 1688 原链接
              </a>
            </CardContent>
          </Card>
        </div>

        {/* 右：操作区 */}
        <div className="space-y-4 lg:col-span-2">
          {/* 一键生成 */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-primary" />
                AI 生成 Listing
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                选择平台，AI 自动生成适配的标题、描述和卖点
              </p>
              <div className="grid gap-3 grid-cols-2 sm:grid-cols-3">
                {(showAllPlatforms ? PLATFORMS : PLATFORMS.slice(0, 4)).map((p) => (
                  <Button
                    key={p.id}
                    variant="outline"
                    className="justify-start h-auto py-3 px-4"
                    onClick={() => navigate(`/app/content?product=${id}&platform=${p.id}`)}
                  >
                    <Globe className="h-4 w-4 mr-2 shrink-0" />
                    <div className="text-left">
                      <p className="text-sm font-medium">{p.label}</p>
                      <p className="text-xs text-muted-foreground">生成 Listing</p>
                    </div>
                  </Button>
                ))}
              </div>
              <Button
                variant="ghost"
                size="sm"
                className="mt-2"
                onClick={() => setShowAllPlatforms(!showAllPlatforms)}
              >
                {showAllPlatforms ? (
                  <>收起 <ChevronUp className="h-3 w-3 ml-1" /></>
                ) : (
                  <>全部平台 ({PLATFORMS.length}) <ChevronDown className="h-3 w-3 ml-1" /></>
                )}
              </Button>
            </CardContent>
          </Card>

          {/* 生成历史 */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Clock className="h-4 w-4 text-muted-foreground" />
                生成历史
              </CardTitle>
            </CardHeader>
            <CardContent>
              {history?.items?.length > 0 ? (
                <div className="space-y-2">
                  {history.items.map((item: any) => (
                    <div key={item.id} className="flex items-center justify-between rounded-md border p-3">
                      <div>
                        <p className="text-sm font-medium">{item.platform}</p>
                        <p className="text-xs text-muted-foreground">{item.created_at}</p>
                      </div>
                      <Button variant="ghost" size="sm">再次生成</Button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex flex-col items-center py-8 text-muted-foreground">
                  <Clock className="h-8 w-8 mb-2 opacity-40" />
                  <p className="text-sm">暂无生成记录</p>
                  <p className="text-xs mt-1">点击上方按钮生成第一个 Listing</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* 删除商品 */}
          <Card className="border-destructive/20">
            <CardContent className="pt-4">
              {showDeleteConfirm ? (
                <div className="space-y-3">
                  <div className="flex items-start gap-2 text-sm">
                    <AlertTriangle className="h-4 w-4 text-destructive mt-0.5 shrink-0" />
                    <p>确定要删除这个商品吗？此操作不可撤销。</p>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="destructive" size="sm" onClick={() => deleteMutation.mutate()} disabled={deleteMutation.isPending}>
                      {deleteMutation.isPending ? '删除中...' : '确认删除'}
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => setShowDeleteConfirm(false)}>取消</Button>
                  </div>
                </div>
              ) : (
                <Button variant="outline" size="sm" className="text-destructive gap-1 w-full" onClick={() => setShowDeleteConfirm(true)}>
                  <Trash2 className="h-4 w-4" />删除商品
                </Button>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </motion.div>
  )
}
