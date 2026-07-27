import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/stores/authStore'
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
  { icon: Bot, title: 'AI 选品决策', desc: '告诉 AI "我想做蓝牙耳机"，自动分析 Amazon 市场容量、竞争格局、利润空间，给出能不能做的判断。' },
  { icon: DollarSign, title: '利润自动计算', desc: 'AI 自动从 1688 获取供货价，结合平台费率运费广告成本，算出真实净利润和利润率。' },
  { icon: Zap, title: 'AI 生成 Listing', desc: '确定要卖的商品后，AI 自动生成适配 Amazon/Shopify/eBay 的标题、描述、卖点和 SEO。' },
  { icon: Languages, title: '多语言翻译 + 对照', desc: '支持英日韩法德等 16 种语言，原文译文对照显示，质量可查验，适合多站点运营。' },
  { icon: Shield, title: '合规审查', desc: '正则 + AI 双重检测违禁词和平台违规风险，避免下架罚款，降低运营风险。' },
  { icon: ShoppingBag, title: 'Shopify 一键发布', desc: 'AI 生成内容后直接发布到绑定的 Shopify 店铺。自有商品支持 CSV 批量导入批量处理。' },
]

const PLATFORMS = ['Amazon', 'Shopify', 'eBay', 'Etsy', 'Temu', 'TikTok Shop', 'Walmart', 'AliExpress']

export default function LandingPage() {
  const navigate = useNavigate()
  const isLoggedIn = useAuthStore((s) => s.isAuthenticated)

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 via-white to-slate-50/50">
      {/* ── 导航 ────────────────────────────────────────── */}
      <header className="sticky top-0 z-50 border-b border-slate-200/60 bg-white/80 backdrop-blur-lg">
        <div className="max-w-5xl mx-auto flex items-center justify-between h-14 px-4 md:px-6">
          <div className="flex items-center gap-2">
            <div className="h-7 w-7 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center">
              <Globe className="h-3.5 w-3.5 text-white" />
            </div>
            <span className="font-bold text-sm">VeyaShip AI</span>
          </div>
          <div className="flex items-center gap-2">
            {isLoggedIn ? (
              <Button size="sm" onClick={() => navigate('/app/dashboard')} className="bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm">进入应用</Button>
            ) : (
              <>
                <Button variant="ghost" size="sm" onClick={() => navigate('/login')} className="text-slate-500">登录</Button>
                <Button size="sm" onClick={() => navigate('/register')} className="bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm">免费注册</Button>
              </>
            )}
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
                  <span className="text-slate-800">这个品能不能做？</span>
                  <br />
                  <span className="bg-gradient-to-r from-indigo-600 via-violet-600 to-purple-600 bg-clip-text text-transparent">
                    AI 帮你做跨境决策
                  </span>
                </h1>
                <p className="text-sm sm:text-base text-slate-500 max-w-lg mx-auto leading-relaxed">
                  输入品类名，AI 自动分析 Amazon 市场容量、竞争格局、利润空间。
                  <br />
                  从选品决策到 Listing 生成再到上架，一个平台完成。
                </p>
              </motion.div>

              <motion.div variants={item} className="flex items-center justify-center gap-3 pt-1">
                <Button size="lg" onClick={() => navigate(isLoggedIn ? '/app/dashboard' : '/register')} className="h-11 px-6 text-sm gap-1.5 bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm">
                  {isLoggedIn ? '进入应用' : '免费开始使用'} <ArrowRight className="h-3.5 w-3.5" />
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
          <h2 className="text-lg font-semibold text-center text-slate-800 mb-1">从选品到上架，四步完成</h2>
          <p className="text-sm text-slate-500 text-center mb-8">AI 分析品类 → 决定能不能做 → 生成 Listing → 发布到店铺</p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[
              { icon: Bot, step: '01', title: 'AI 选品分析', desc: '输入品类，AI 分析市场机会' },
              { icon: DollarSign, step: '02', title: '利润测算', desc: '自动算净利和利润率' },
              { icon: Sparkles, step: '03', title: 'AI 生成 Listing', desc: '自动写标题描述卖点' },
              { icon: ShoppingBag, step: '04', title: '一键上架', desc: '发布到 Shopify 店铺' },
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
          <h2 className="text-lg font-semibold text-center text-slate-800 mb-1">覆盖跨境卖家核心决策链路</h2>
          <p className="text-sm text-slate-500 text-center mb-8">选品分析 → 利润测算 → Listing 生成 → 上架发布，一个平台完成</p>
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

        {/* ── 产品展示 ────────────────────────────────────── */}
        <section className="max-w-5xl mx-auto px-4 py-16">
          <h2 className="text-lg font-semibold text-center text-slate-800 mb-1">看看 AI 生成的效果</h2>
          <p className="text-sm text-slate-500 text-center mb-8">AI 分析品类数据 → 给出选品建议 → 生成 Listing</p>
          <div className="grid md:grid-cols-2 gap-4">
            <motion.div initial={{ opacity: 0, x: -20 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }}
              className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <div className="text-xs font-medium text-slate-400 mb-3 uppercase tracking-wide">1688 商品信息</div>
              <div className="space-y-2 text-sm">
                <div className="flex gap-3">
                  <div className="w-12 h-12 rounded-lg bg-slate-100 flex items-center justify-center text-slate-300 text-xs">图片</div>
                  <div>
                    <p className="font-medium text-slate-800">无线蓝牙耳机 5.3 降噪 高音质</p>
                    <p className="text-slate-500">价格：¥36.50 | 已售 12,000+</p>
                    <p className="text-slate-500 text-xs mt-1">店铺：深圳市华强北科技有限公司</p>
                  </div>
                </div>
              </div>
            </motion.div>
            <motion.div initial={{ opacity: 0, x: 20 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }}
              className="rounded-xl border border-indigo-200 bg-indigo-50/50 p-4 shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <div className="text-xs font-medium text-indigo-600 uppercase tracking-wide">AI 生成的 Amazon Listing</div>
                <span className="text-xs text-emerald-600 bg-emerald-100 px-2 py-0.5 rounded-full">已翻译 英文</span>
              </div>
              <div className="space-y-2 text-sm">
                <p className="font-medium text-slate-800">Wireless Bluetooth 5.3 Headphones, Over-Ear Noise Cancelling, Hi-Fi Sound Quality, 40H Battery Life, Comfort Fit for Work Travel</p>
                <ul className="text-slate-600 text-xs space-y-1 mt-2">
                  <li>• Bluetooth 5.3 technology for stable, lag-free connection</li>
                  <li>• Active noise cancellation blocks up to 35dB ambient noise</li>
                  <li>• Hi-Fi stereo sound with deep bass and clear treble</li>
                  <li>• 40-hour battery life for all-day use</li>
                  <li>• Lightweight ergonomic design for comfortable wear</li>
                </ul>
              </div>
            </motion.div>
          </div>
          <p className="text-xs text-slate-400 text-center mt-3">左侧为 1688 原始商品数据，右侧为 AI 自动生成的 Amazon Listing</p>
        </section>

        {/* ── 定价 ────────────────────────────────────────── */}
        <section className="max-w-3xl mx-auto px-4 py-16">
          <h2 className="text-lg font-semibold text-center text-slate-800 mb-1">简单透明的定价</h2>
          <p className="text-sm text-slate-500 text-center mb-8">免费开始，按需升级</p>
          <div className="grid md:grid-cols-2 gap-4">
            <motion.div initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
              className="rounded-xl border border-slate-200 bg-white p-6">
              <h3 className="font-semibold text-slate-800">免费版</h3>
              <p className="text-2xl font-bold text-slate-800 mt-2">¥0<span className="text-sm font-normal text-slate-400">/月</span></p>
              <ul className="mt-4 space-y-2 text-sm text-slate-600">
                <li className="flex items-center gap-2"><CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 shrink-0" />100 次 AI 生成额度</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 shrink-0" />1688 商品抓取</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 shrink-0" />利润计算器</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 shrink-0" />合规审查</li>
              </ul>
              <Button size="sm" onClick={() => navigate(isLoggedIn ? '/app/dashboard' : '/register')} className="w-full mt-6 bg-indigo-600 hover:bg-indigo-700 text-white">{isLoggedIn ? '进入应用' : '免费开始'}</Button>
            </motion.div>
            <motion.div initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: 0.1 }}
              className="rounded-xl border-2 border-indigo-200 bg-indigo-50/50 p-6 relative">
              <div className="absolute -top-2.5 right-4 bg-indigo-600 text-white text-xs px-3 py-0.5 rounded-full">推荐</div>
              <h3 className="font-semibold text-slate-800">专业版</h3>
              <p className="text-2xl font-bold text-slate-800 mt-2">¥99<span className="text-sm font-normal text-slate-400">/月</span></p>
              <ul className="mt-4 space-y-2 text-sm text-slate-600">
                <li className="flex items-center gap-2"><CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 shrink-0" />无限 AI 生成</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 shrink-0" />AI 智能助手（Agent）</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 shrink-0" />Shopify 一键发布</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 shrink-0" />AI 图片生成</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 shrink-0" />优先客服支持</li>
              </ul>
              <Button size="sm" onClick={() => navigate(isLoggedIn ? '/app/dashboard' : '/register')} className="w-full mt-6 bg-indigo-600 hover:bg-indigo-700 text-white">{isLoggedIn ? '进入应用' : '选择专业版'}</Button>
            </motion.div>
          </div>
        </section>

        {/* ── 信任感 ──────────────────────────────────────── */}
        <section className="max-w-3xl mx-auto px-4 py-8 text-center">
          <div className="grid grid-cols-3 gap-8 text-center">
            <div>
              <p className="text-2xl font-bold text-slate-800">500+</p>
              <p className="text-xs text-slate-500 mt-1">内测用户</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-800">16</p>
              <p className="text-xs text-slate-500 mt-1">支持语言</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-800">8</p>
              <p className="text-xs text-slate-500 mt-1">支持平台</p>
            </div>
          </div>
        </section>

        {/* ── CTA ──────────────────────────────────────────── */}
        <section className="max-w-lg mx-auto px-4 py-16 text-center">
          <motion.div initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
            className="rounded-2xl bg-gradient-to-br from-indigo-50 via-white to-violet-50 border border-slate-200 p-8 space-y-4">
            <h2 className="text-lg font-semibold text-slate-800">开始免费使用</h2>
            <p className="text-sm text-slate-500">无需信用卡，无需配置 API Key</p>
            <Button size="lg" onClick={() => navigate(isLoggedIn ? '/app/dashboard' : '/register')} className="h-11 px-6 text-sm gap-1.5 bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm">
              {isLoggedIn ? '进入应用' : '创建免费账号'} <ArrowRight className="h-3.5 w-3.5" />
            </Button>
          </motion.div>
        </section>
      </main>

      <footer className="border-t border-slate-200 py-6 text-center text-xs text-slate-400 space-y-1">
        <p>© 2026 VeyaShip AI. All rights reserved.</p>
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
