import { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import { Sparkles, Loader2, AlertCircle, ImageIcon, Copy, CheckCircle2, Clock } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import apiClient from '@/api/client'

export default function ImagesPage() {
  const [prompt, setPrompt] = useState('')
  const [copied, setCopied] = useState(false)
  const [taskId, setTaskId] = useState<string | null>(null)
  const [status, setStatus] = useState<'idle' | 'submitting' | 'processing' | 'completed' | 'failed'>('idle')
  const [imageUrls, setImageUrls] = useState<string[]>([])
  const [error, setError] = useState('')
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const startTimeRef = useRef<number>(0)

  // 清理轮询
  useEffect(() => {
    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current)
    }
  }, [])

  // 提交生成任务
  const handleGenerate = async () => {
    if (!prompt.trim()) return
    setStatus('submitting')
    setError('')
    setImageUrls([])

    try {
      const res = await apiClient.post('/images/generate', { prompt, num_outputs: 1 })
      const tid = res.data.task_id
      setTaskId(tid)
      setStatus('processing')
      startTimeRef.current = Date.now()

      // 开始轮询结果
      pollingRef.current = setInterval(async () => {
        try {
          const statusRes = await apiClient.get(`/images/status/${tid}`)
          const s = statusRes.data

          if (s.status === 'completed') {
            setImageUrls(s.image_urls || [])
            setStatus('completed')
            if (pollingRef.current) clearInterval(pollingRef.current)
          } else if (s.status === 'failed') {
            setError(s.error || '生成失败')
            setStatus('failed')
            if (pollingRef.current) clearInterval(pollingRef.current)
          }
          // 'processing' → 继续轮询
        } catch {
          // 忽略轮询错误
        }
      }, 1500)
    } catch (err: any) {
      setError(err?.response?.data?.detail || '提交失败')
      setStatus('failed')
    }
  }

  const elapsed = startTimeRef.current ? Math.floor((Date.now() - startTimeRef.current) / 1000) : 0

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="max-w-2xl mx-auto space-y-6">
      <div className="text-center">
        <h1 className="text-2xl font-bold tracking-tight flex items-center justify-center gap-2">
          <ImageIcon className="h-6 w-6 text-primary" />
          AI 商品图片生成
        </h1>
        <p className="text-muted-foreground mt-1">用阿里云通义万相生成商品主图</p>
      </div>

      <Card>
        <CardContent className="pt-6 space-y-4">
          <div className="space-y-2">
            <Label>图片描述</Label>
            <Input
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="例如：Professional product photo of wireless headphones, white background"
              disabled={status === 'submitting' || status === 'processing'}
            />
          </div>
          <Button
            className="w-full"
            onClick={handleGenerate}
            disabled={!prompt.trim() || status === 'submitting' || status === 'processing'}
          >
            {(status === 'submitting' || status === 'processing') ? (
              <><Loader2 className="mr-2 h-4 w-4 animate-spin" />生成中...</>
            ) : (
              <><Sparkles className="mr-2 h-4 w-4" />生成图片</>
            )}
          </Button>

          {/* 生成进度 */}
          {status === 'processing' && (
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                正在生成图片
                {elapsed > 0 && <span className="text-xs">（{elapsed} 秒）</span>}
              </div>
              <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                <div className="h-full bg-primary rounded-full animate-pulse" style={{ width: '60%' }} />
              </div>
              <p className="text-xs text-muted-foreground">AI 正在生成中，请稍候...</p>
            </div>
          )}

          {error && (
            <div className="flex items-center gap-2 text-sm text-destructive bg-destructive/10 p-3 rounded-md">
              <AlertCircle className="h-4 w-4" />
              {error}
            </div>
          )}
        </CardContent>
      </Card>

      {status === 'completed' && imageUrls.map((url: string, i: number) => (
        <Card key={i}>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-sm">生成结果 #{i + 1}</CardTitle>
            <Button variant="ghost" size="icon" onClick={() => { navigator.clipboard.writeText(url); setCopied(true); setTimeout(() => setCopied(false), 2000) }}>
              {copied ? <CheckCircle2 className="h-4 w-4 text-emerald-500" /> : <Copy className="h-4 w-4" />}
            </Button>
          </CardHeader>
          <CardContent>
            <img src={url} alt="Generated" className="w-full rounded-lg border" />
          </CardContent>
        </Card>
      ))}

      {status === 'idle' && (
        <Card className="bg-muted/30">
          <CardContent className="py-12 text-center text-muted-foreground">
            <ImageIcon className="h-12 w-12 mx-auto mb-3 opacity-30" />
            <p className="text-sm">输入图片描述，点击「生成图片」</p>
            <p className="text-xs mt-1">阿里云通义万相生成，约 10-15 秒</p>
          </CardContent>
        </Card>
      )}
    </motion.div>
  )
}
