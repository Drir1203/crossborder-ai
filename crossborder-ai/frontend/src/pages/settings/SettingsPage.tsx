import { useState, useEffect } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Settings, CheckCircle2, Palette, X } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import apiClient from '@/api/client'

export default function SettingsPage() {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState('persona')

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <Settings className="h-6 w-6 text-primary" />
          系统设置
        </h1>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="persona">品牌调性</TabsTrigger>
        </TabsList>

        <TabsContent value="persona" className="space-y-4">
          <PersonaForm />
        </TabsContent>
      </Tabs>
    </motion.div>
  )
}

function PersonaForm() {
  const queryClient = useQueryClient()
  const [brandName, setBrandName] = useState('')
  const [tagline, setTagline] = useState('')
  const [description, setDescription] = useState('')
  const [tone, setTone] = useState('professional')
  const [toneCustom, setToneCustom] = useState('')
  const [bannedWords, setBannedWords] = useState<string[]>([])
  const [newWord, setNewWord] = useState('')

  const { data } = useQuery({
    queryKey: ['persona'],
    queryFn: async () => { const r = await apiClient.get('/settings/persona'); return r.data },
  })

  useEffect(() => {
    if (data) {
      setBrandName(data.brand_name || '')
      setTagline(data.tagline || '')
      setDescription(data.description || '')
      setTone(data.tone || 'professional')
      setToneCustom(data.tone_custom || '')
      setBannedWords(data.banned_words || [])
    }
  }, [data])

  const saveMutation = useMutation({
    mutationFn: async (body: any) => { const r = await apiClient.put('/settings/persona', body); return r.data },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['persona'] }),
  })

  const addWord = () => {
    const w = newWord.trim()
    if (w && !bannedWords.includes(w)) { setBannedWords([...bannedWords, w]); setNewWord('') }
  }

  const handleSave = () => {
    saveMutation.mutate({
      brand_name: brandName, tagline, description, tone,
      tone_custom: tone === 'custom' ? toneCustom : '',
      banned_words: bannedWords,
    })
  }

  return (
    <Card>
      <CardHeader><CardTitle className="text-base flex items-center gap-2"><Palette className="h-4 w-4" />品牌调性</CardTitle>
      <CardDescription>配置后，AI 生成的内容会自动按品牌风格输出</CardDescription></CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2"><Label>品牌名</Label><Input value={brandName} onChange={e => setBrandName(e.target.value)} placeholder="如：ABC Store" /></div>
          <div className="space-y-2"><Label>标语</Label><Input value={tagline} onChange={e => setTagline(e.target.value)} placeholder="如：Quality You Can Trust" /></div>
        </div>
        <div className="space-y-2"><Label>品牌描述</Label>
          <textarea value={description} onChange={e => setDescription(e.target.value)} placeholder="简单描述你的品牌定位、目标客户..."
            className="flex min-h-[80px] w-full rounded-md border bg-background px-3 py-2 text-sm" />
        </div>
        <div className="space-y-2">
          <Label>默认语气</Label>
          <div className="flex flex-wrap gap-2">
            {['professional','casual','luxury','friendly','persuasive','humorous','custom'].map(t => (
              <Badge key={t} variant={tone === t ? 'default' : 'outline'} className="cursor-pointer" onClick={() => setTone(t)}>{t}</Badge>
            ))}
          </div>
          {tone === 'custom' && <Input value={toneCustom} onChange={e => setToneCustom(e.target.value)} placeholder="自定义语气描述" className="mt-2" />}
        </div>
        <div className="space-y-2">
          <Label>违禁词（AI 生成时会自动避免使用）</Label>
          <div className="flex gap-2">
            <Input value={newWord} onChange={e => setNewWord(e.target.value)} onKeyDown={e => e.key === 'Enter' && addWord()} placeholder="输入违禁词，回车添加" />
            <Button variant="outline" onClick={addWord}>添加</Button>
          </div>
          {bannedWords.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {bannedWords.map((w, i) => (
                <Badge key={i} variant="secondary" className="gap-1">
                  {w}
                  <X className="h-3 w-3 cursor-pointer" onClick={() => setBannedWords(bannedWords.filter((_, j) => j !== i))} />
                </Badge>
              ))}
            </div>
          )}
        </div>
        <Button onClick={handleSave} disabled={saveMutation.isPending}>
          {saveMutation.isPending ? '保存中...' : '保存品牌配置'}
        </Button>
        {saveMutation.isSuccess && <p className="text-sm text-emerald-600 flex items-center gap-1"><CheckCircle2 className="h-4 w-4" />已保存</p>}
      </CardContent>
    </Card>
  )
}

