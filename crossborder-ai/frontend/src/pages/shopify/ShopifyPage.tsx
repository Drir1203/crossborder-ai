import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { ShoppingBag, Link, ExternalLink, Plus, AlertCircle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import apiClient from '@/api/client'

export default function ShopifyPage() {
  const [shopName, setShopName] = useState('')

  const { data: channels } = useQuery({
    queryKey: ['shopify-channels'],
    queryFn: async () => {
      const r = await apiClient.get('/shopify/channels')
      return r.data
    },
  })

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <ShoppingBag className="h-6 w-6 text-primary" />
          Shopify
        </h1>
        <p className="text-muted-foreground">绑定 Shopify 店铺，发布商品和管理订单</p>
      </div>

      <Card>
        <CardHeader><CardTitle className="text-sm">绑定店铺</CardTitle></CardHeader>
        <CardContent className="flex gap-2">
          <Input value={shopName} onChange={e => setShopName(e.target.value)}
            placeholder="输入 Shopify 店铺名（如 my-store）" />
          <Button disabled={!shopName.trim()} onClick={() => {
            window.open(`/api/v1/shopify/auth?shop=${shopName.trim()}.myshopify.com`)
          }}>
            <Link className="h-4 w-4 mr-1" />授权
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="text-sm">已绑定店铺</CardTitle></CardHeader>
        <CardContent>
          {channels?.length > 0 ? channels.map((c: any) => (
            <div key={c.id} className="flex items-center justify-between py-2 border-b last:border-0">
              <div>
                <p className="text-sm font-medium">{c.shop_name}</p>
                <p className="text-xs text-muted-foreground">{c.domain}</p>
              </div>
              <Badge variant="success">已绑定</Badge>
            </div>
          )) : (
            <p className="text-sm text-muted-foreground">暂未绑定 Shopify 店铺</p>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}
