import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Button } from '@/components/ui/button'
import {
  Sparkles, Globe, ShoppingBag, Bot, DollarSign, Shield, ArrowRight, CheckCircle2,
  Languages, Zap,
} from 'lucide-react'

const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.08 } },
}
const item = {
  hidden: { opacity: 0, y: 24 },
  show: { opacity: 1, y: 0, transition: { duration: 0.5, ease: [0.25, 0.1, 0.25, 1] } },
}

const FEATURES = [
  { icon: Zap, title: 'AI Listing 生成', desc: '粘贴 1688 链接，AI 自动抓取商品信息，生成适配 Amazon / Shopify / eBay 等平台的标题、描述和卖点。' },
  { icon: Languages, title: '多语言翻译 + 对照', desc: '支持英日韩法德等 16 种语言，保持 SEO 关键词优化，原文译文对照显示，质量可查验。' },
  { icon: Shield, title: '合规审查', desc: '正则 + AI 双重审查，自动检测违禁词和平台违规风险，避免下架和罚款。' },
  { icon: DollarSign, title: '利润计算器', desc: '输入售价、成本、运费和平台费率，自动计算净利润和利润率，辅助定价决策。' },
  { icon: Bot, title: 'AI 智能助手', desc: '自然语言指令操作：「帮我抓这个商品」「算下利润」「生成 Amazon Listing」。' },
  { icon: ShoppingBag, title: 'Shopify 一键发布', desc: 'AI 生成内容后，选择绑定的店铺直接发布，无需复制粘贴。更多平台对接中。' },
]

const PLATFORMS = ['Amazon', 'Shopify', 'eBay', 'Etsy', 'Temu', 'TikTok Shop', 'Walmart', 'AliExpress']

export default function LandingPage() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 via-white to-slate-50/50">
      {/* ── 导航 ────────────────────────────────────────── */}
      <header className="sticky top-0 z-50 border-b border-slate-200/60 bg-white/80 backdrop-blur-lg">
        <div className="max-w-5xl mx-auto flex items-center justify-between h-14 px-4 md:px-6">
          <div className="flex items-center gap-2">
            <div className="h-7 w-7 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center">
              <Globe className="h-3.5 w-3.5 text-white" />
            </div>
            <span className="font-bold text-sm">VeyaShip</span>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" onClick={() => navigate('/login')} className="text-slate-500">登录</Button>
            <Button size="sm" onClick={() => navigate('/register')} className="bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm">
              免费注册
            </Button>
          </div>
        </div>
      </header>

      <main>
        {/* ── HERO ─────────────────────────────────────────── */}
        <section className="relative overflow-hidden">
          <div className="absolute inset-0 pointer-events-none">
            <div className="absolute top-20 -left-20 w-72 h-72 bg-indigo-200/40 rounded-full blur-[100px]" />
            <div className="absolute top-40 right-0 w-96 h-96 bg-violet-200/30 rounded-full blur-[120px]" />
            <div className="absolute -bottom-20 left-1/3 w-64 h-64 bg-sky-200/30 rounded-full blur-[80px]" />
          </div>

          <div className="max-w-4xl mx-auto px-4 pt-24 pb-16 relative">
            <motion.div variants={container} initial="hidden" animate="show" className="text-center space-y-7">

              <motion.div variants={item}>
                <span className="inline-flex items-center gap-1.5 rounded-full border border-indigo-200 bg-indigo-50 px-3.5 py-1 text-xs font-medium text-indigo-600">
                  <Sparkles className="h-3 w-3" /> 跨境电商 AI 工具
                </span>
              </motion.div>

              <motion.div variants={item} className="space-y-4">
                <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight leading-[1.15]">
                  <span className="text-slate-800">从 1688 到店铺上架，</span>
                  <br />
                  <span className="bg-gradient-to-r from-indigo-600 via-violet-600 to-purple-600 bg-clip-text text-transparent">
                    全流程 AI 自动化
                  </span>
                </h1>
                <p className="text-sm sm:text-base text-slate-500 max-w-lg mx-auto leading-relaxed">
                  粘贴 1688 链接 → AI 抓取商品信息 → 生成多平台 Listing → 翻译 → 合规审查 → 一键上架。
                  <br />
                  一个平台完成选品到出单的全流程。
                </p>
              </motion.div>

              <motion.div variants={item} className="flex items-center justify-center gap-3 pt-1">
                <Button size="lg" onClick={() => navigate('/register')} className="h-11 px-6 text-sm gap-1.5 bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm">
                  免费开始使用 <ArrowRight className="h-3.5 w-3.5" />
                </Button>
              </motion.div>

              <motion.div variants={item} className="flex items-center justify-center gap-5 text-xs text-slate-400">
                <span className="flex items-center gap-1"><CheckCircle2 className="h-3 w-3 text-emerald-500" />无需信用卡</span>
                <span className="flex items-center gap-1"><CheckCircle2 className="h-3 w-3 text-emerald-500" />无需配置 API</span>
                <span className="flex items-center gap-1"><CheckCircle2 className="h-3 w-3 text-emerald-500" />注册即用</span>
              </motion.div>

              <motion.div variants={item} className="flex flex-wrap items-center justify-center gap-2 pt-2">
                {PLATFORMS.map((p) => (
                  <span key={p} className="rounded-lg border border-slate-200 bg-white px-3 py-1 text-xs text-slate-500 shadow-sm">
                    {p}
                  </span>
                ))}
              </motion.div>
            </motion.div>
          </div>
        </section>

        {/* ── 流程 ────────────────────────────────────────── */}
        <section className="max-w-4xl mx-auto px-4 py-16">
          <h2 className="text-lg font-semibold text-center text-slate-800 mb-1">四步完成上架</h2>
          <p className="text-sm text-slate-500 text-center mb-8">从选定商品到店铺上架，最快 2 分钟</p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[
              { icon: LinkIcon, step: '01', title: '粘贴链接', desc: '复制 1688 商品链接' },
              { icon: Sparkles, step: '02', title: 'AI 生成', desc: '自动抓取 + 写标题描述' },
              { icon: Globe, step: '03', title: '选择平台', desc: '目标平台和语言' },
              { icon: ShoppingBag, step: '04', title: '一键上架', desc: '发布到你的店铺' },
            ].map((s, i) => (
              <motion.div key={i} initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.08 }}
                className="text-center p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
                <div className="text-xs font-mono text-indigo-500 mb-2">{s.step}</div>
                <s.icon className="h-5 w-5 text-indigo-500 mx-auto mb-2" />
                <h3 className="font-medium text-sm text-slate-700 mb-0.5">{s.title}</h3>
                <p className="text-xs text-slate-400">{s.desc}</p>
              </motion.div>
            ))}
          </div>
        </section>

        {/* ── 功能 ────────────────────────────────────────── */}
        <section className="max-w-5xl mx-auto px-4 py-16">
          <h2 className="text-lg font-semibold text-center text-slate-800 mb-1">覆盖跨境卖家核心工作流</h2>
          <p className="text-sm text-slate-500 text-center mb-8">选品、上架、合规、利润分析，一个平台完成</p>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
            {FEATURES.map((f, i) => (
              <motion.div key={i} initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.04 }}
                className="rounded-xl bg-white border border-slate-200 p-5 hover:shadow-md transition-shadow">
                <div className="h-8 w-8 rounded-lg bg-indigo-50 flex items-center justify-center mb-3">
                  <f.icon className="h-4 w-4 text-indigo-600" />
                </div>
                <h3 className="font-medium text-sm text-slate-800 mb-1">{f.title}</h3>
                <p className="text-sm text-slate-500 leading-relaxed">{f.desc}</p>
              </motion.div>
            ))}
          </div>
        </section>

        {/* ── CTA ──────────────────────────────────────────── */}
        <section className="max-w-lg mx-auto px-4 py-16 text-center">
          <motion.div initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
            className="rounded-2xl bg-gradient-to-br from-indigo-50 via-white to-violet-50 border border-slate-200 p-8 space-y-4">
            <h2 className="text-lg font-semibold text-slate-800">开始免费使用</h2>
            <p className="text-sm text-slate-500">无需信用卡，无需配置 API Key</p>
            <Button size="lg" onClick={() => navigate('/register')} className="h-11 px-6 text-sm gap-1.5 bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm">
              创建免费账号 <ArrowRight className="h-3.5 w-3.5" />
            </Button>
          </motion.div>
        </section>
      </main>

      <footer className="border-t border-slate-200 py-6 text-center text-xs text-slate-400 space-y-1">
        <p>© 2026 VeyaShip. All rights reserved.</p>
        <p className="text-[11px] text-slate-300">浙ICP备XXXXXXXX号-1</p>
        {/* ICP 备案号下来后替换上面的占位符 */}
      </footer>
    </div>
  )
}

function LinkIcon() {
  return (
    <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
      <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
    </svg>
  )
}
