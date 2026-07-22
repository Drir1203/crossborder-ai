import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Sparkles, Loader2, AlertCircle, ImageIcon, Copy, CheckCircle2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import apiClient from '@/api/client'

export default function ImagesPage() {
  const [prompt, setPrompt] = useState('')
  const [copied, setCopied] = useState(false)

  const mutation = useMutation({
    mutationFn: async () => {
      const res = await apiClient.post('/images/generate', { prompt, num_outputs: 1 })
      return res.data
    },
  })

  const copyUrl = (url: string) => {
    navigator.clipboard.writeText(url)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="max-w-2xl mx-auto space-y-6">
      <div className="text-center">
        <h1 className="text-2xl font-bold tracking-tight flex items-center justify-center gap-2">
          <ImageIcon className="h-6 w-6 text-primary" />
          AI 商品图片生成
        </h1>
        <p className="text-muted-foreground mt-1">用 FLUX AI 生成商品主图</p>
      </div>

      <Card>
        <CardContent className="pt-6 space-y-4">
          <div className="space-y-2">
            <Label>图片描述</Label>
            <Input
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="例如：Professional product photo of wireless headphones, white background, studio lighting"
            />
          </div>
          <Button
            className="w-full"
            onClick={() => mutation.mutate()}
            disabled={!prompt.trim() || mutation.isPending}
          >
            {mutation.isPending ? (
              <><Loader2 className="mr-2 h-4 w-4 animate-spin" />生成中...</>
            ) : (
              <><Sparkles className="mr-2 h-4 w-4" />生成图片</>
            )}
          </Button>

          {mutation.isError && (
            <div className="flex items-center gap-2 text-sm text-destructive bg-destructive/10 p-3 rounded-md">
              <AlertCircle className="h-4 w-4" />
              {(mutation.error as any)?.response?.data?.detail || '生成失败'}
            </div>
          )}
        </CardContent>
      </Card>

      {mutation.data?.image_urls?.map((url: string, i: number) => (
        <Card key={i}>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-sm">生成结果 #{i + 1}</CardTitle>
            <Button variant="ghost" size="icon" onClick={() => copyUrl(url)}>
              {copied ? <CheckCircle2 className="h-4 w-4 text-emerald-500" /> : <Copy className="h-4 w-4" />}
            </Button>
          </CardHeader>
          <CardContent>
            <img src={url} alt="Generated" className="w-full rounded-lg border" />
          </CardContent>
        </Card>
      ))}
    </motion.div>
  )
}
