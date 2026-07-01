import { useState, useEffect } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Settings, Globe, CheckCircle2, AlertCircle, Key, Eye, EyeOff, ExternalLink } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import apiClient from '@/api/client'

export default function SettingsPage() {
  const queryClient = useQueryClient()
  const [apiKey, setApiKey] = useState('')
  const [apiSecret, setApiSecret] = useState('')
  const [showKey, setShowKey] = useState(false)
  const [showSecret, setShowSecret] = useState(false)

  const { data, isLoading } = useQuery({
    queryKey: ['scraping-config'],
    queryFn: async () => {
      const res = await apiClient.get('/settings/scraping')
      return res.data
    },
  })

  useEffect(() => {
    if (data) {
      setApiKey(data.api_key || '')
      setApiSecret(data.api_secret || '')
    }
  }, [data])

  const saveMutation = useMutation({
    mutationFn: async (body: { api_key: string; api_secret: string }) => {
      const res = await apiClient.put('/settings/scraping', body)
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scraping-config'] })
    },
  })

  const handleSave = () => {
    saveMutation.mutate({ api_key: apiKey.trim(), api_secret: apiSecret.trim() })
  }

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <Settings className="h-6 w-6 text-primary" />
          系统设置
        </h1>
        <p className="text-muted-foreground">配置 1688 数据接口，让用户可以直接抓取商品信息</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span className="flex items-center gap-2 text-base">
              <Globe className="h-4 w-4" />
              1688 数据接口配置
            </span>
            <Badge variant={data?.configured ? 'success' : 'warning'}>
              {data?.configured ? '已配置' : '未配置'}
            </Badge>
          </CardTitle>
          <CardDescription>
            在这里输入 Onebound API 凭证，保存后立即生效，用户即可正常抓取 1688 商品
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-5">
          {data?.configured ? (
            <div className="rounded-md bg-emerald-500/10 border border-emerald-500/20 p-3 text-sm flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />
              <span className="text-emerald-600 font-medium">1688 数据接口已就绪，用户可以直接抓取商品</span>
            </div>
          ) : (
            <div className="rounded-md bg-amber-500/10 border border-amber-500/20 p-3 text-sm">
              <p className="font-medium text-amber-600 flex items-center gap-1">
                <AlertCircle className="h-4 w-4" />
                1688 数据接口未配置
              </p>
              <p className="text-muted-foreground mt-1">
                配置后用户粘贴 1688 链接即可自动抓取商品标题、价格、图片等信息。
                无需用户做任何额外操作。
              </p>
            </div>
          )}

          {/* API Key */}
          <div className="space-y-2">
            <Label htmlFor="api_key">Onebound API Key</Label>
            <div className="relative">
              <Input
                id="api_key"
                type={showKey ? 'text' : 'password'}
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="输入 Onebound API Key"
                className="pr-10"
              />
              <Button type="button" variant="ghost" size="icon" className="absolute right-0 top-0 h-full px-3"
                onClick={() => setShowKey(!showKey)}>
                {showKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </Button>
            </div>
          </div>

          {/* API Secret */}
          <div className="space-y-2">
            <Label htmlFor="api_secret">Onebound API Secret</Label>
            <div className="relative">
              <Input
                id="api_secret"
                type={showSecret ? 'text' : 'password'}
                value={apiSecret}
                onChange={(e) => setApiSecret(e.target.value)}
                placeholder="输入 Onebound API Secret"
                className="pr-10"
              />
              <Button type="button" variant="ghost" size="icon" className="absolute right-0 top-0 h-full px-3"
                onClick={() => setShowSecret(!showSecret)}>
                {showSecret ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </Button>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <a href="https://www.onebound.cn" target="_blank" rel="noopener noreferrer"
              className="text-xs text-primary hover:underline flex items-center gap-1">
              <ExternalLink className="h-3 w-3" />
              前往 Onebound 获取 API 凭证
            </a>
            <Button onClick={handleSave} disabled={saveMutation.isPending}>
              {saveMutation.isPending ? '保存中...' : '保存配置'}
            </Button>
          </div>

          {saveMutation.isSuccess && (
            <p className="text-sm text-emerald-600 flex items-center gap-1">
              <CheckCircle2 className="h-4 w-4" /> 配置已保存，立即生效
            </p>
          )}
          {saveMutation.isError && (
            <p className="text-sm text-destructive flex items-center gap-1">
              <AlertCircle className="h-4 w-4" /> 保存失败，请重试
            </p>
          )}

          <p className="text-xs text-muted-foreground">
            💡 配置信息保存在数据库中，保存后立即生效，无需重启服务器
          </p>
        </CardContent>
      </Card>
    </motion.div>
  )
}
