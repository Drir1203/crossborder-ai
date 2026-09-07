import { useQuery } from '@tanstack/react-query'
import apiClient from '@/api/client'

// ============================================================================
// Dashboard 新手激活引导 + 图结果历史 —— 共享类型 / 本地标记 / 信号探测 hooks
//
// 信号判定（前端本地信号，真实取自已绑定的后端端点）：
//   ① 店铺已绑定   → GET /api/v1/shopify/channels 返回非空数组
//   ② 品牌调性已填 → GET /api/v1/settings/persona 至少填了品牌名/标语/描述/违禁词
//   ③ 素材已跑     → GET /api/v1/images/history 中存在 status === 'completed'
//
// 所有探测端点都可能尚未接线或网络抖动，统一 retry:false + 调用方 try/catch
// 静默降级：拿不到就当「未完成 / 隐藏区块」，绝不让页面崩。
// ============================================================================

/** localStorage 标记：用户跳过引导 / 已完成首个闭环后不再打扰 */
export const ONBOARDING_SEEN_KEY = 'veyaship_onboarded_seen'

export function isOnboardingSeen(): boolean {
  try {
    return localStorage.getItem(ONBOARDING_SEEN_KEY) === '1'
  } catch {
    return false
  }
}

export function markOnboardingSeen(): void {
  try {
    localStorage.setItem(ONBOARDING_SEEN_KEY, '1')
  } catch {
    /* 隐私模式等场景写入失败不影响使用 */
  }
}

// ── 契约类型（与后端约定一致） ──────────────────────────────
export interface ShopifyChannel {
  id: string
  shop_name: string
  domain: string
  created_at: string
}

export interface PersonaData {
  brand_name?: string | null
  tagline?: string | null
  description?: string | null
  tone?: string
  tone_custom?: string | null
  banned_words?: string[]
}

export interface ImageHistoryItem {
  id: string
  prompt: string
  status: string // pending / processing / completed / failed
  image_urls: string[]
  model_used?: string
  error?: string | null
  created_at?: string
}

/** 探测类查询统一选项：失败即静默，不重试轰炸、不随窗口聚焦刷新 */
const PROBE_OPTIONS = { retry: false, refetchOnWindowFocus: false } as const

/** 已绑定 Shopify 店铺列表（未绑定时后端返回空数组） */
export function useShopifyChannels() {
  return useQuery<ShopifyChannel[]>({
    ...PROBE_OPTIONS,
    queryKey: ['onboarding', 'shopify-channels'],
    queryFn: async () => {
      const res = await apiClient.get('/shopify/channels')
      return Array.isArray(res.data) ? res.data : []
    },
  })
}

/** 品牌调性是否已填写过（只要保存过关键字段即视为已设置） */
export function usePersonaFilled() {
  return useQuery<boolean>({
    ...PROBE_OPTIONS,
    queryKey: ['onboarding', 'persona'],
    queryFn: async () => {
      const res = await apiClient.get('/settings/persona')
      const p = (res.data ?? {}) as PersonaData
      return Boolean(
        p.brand_name ||
          p.tagline ||
          p.description ||
          (Array.isArray(p.banned_words) && p.banned_words.length > 0),
      )
    },
  })
}

/** 图片生成历史（仅本人，时间倒序）。端点未接通时 isError=true，由调用方隐藏区块 */
export function useImageHistory() {
  return useQuery<ImageHistoryItem[]>({
    ...PROBE_OPTIONS,
    queryKey: ['dashboard', 'image-history'],
    queryFn: async () => {
      const res = await apiClient.get('/images/history')
      const items = (res.data as { items?: ImageHistoryItem[] } | undefined)?.items
      return Array.isArray(items) ? items : []
    },
  })
}

/** 相对时间文案（与 DashboardPage 时间习惯一致，画廊局部使用） */
export function formatRelativeTime(dateStr?: string): string {
  if (!dateStr) return ''
  const diff = Date.now() - new Date(dateStr).getTime()
  if (Number.isNaN(diff) || diff < 0) return ''
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return '刚刚'
  if (mins < 60) return `${mins} 分钟前`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours} 小时前`
  return `${Math.floor(hours / 24)} 天前`
}
