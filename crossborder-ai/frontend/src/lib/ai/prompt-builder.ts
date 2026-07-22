// VeyaShip AI Prompt Builder
// 构建发送给 DeepSeek 的 system prompt，不修改 Service 入参出参

export interface Persona {
  brand_name?: string | null
  tagline?: string | null
  description?: string | null
  tone?: string | null
  tone_custom?: string | null
  banned_words?: string[]
}

// 平台通用违禁词硬性规则
const PLATFORM_BANNED_RULES = [
  '最（最好/最优/最棒/最强/最大/最低价）',
  '第一（销量第一/行业第一/全国第一）',
  '顶级',
  '绝对',
  '国家级',
  '100%',
  '零风险',
  '无效退款',
  '永久',
  '全网唯一',
  '销量冠军',
]

/**
 * 构建文案生成的完整 system prompt
 *
 * @param rawTitle - 原始商品标题
 * @param persona - 用户的品牌调性配置（可为 null）
 * @param platform - 目标平台（amazon / ebay / shopify / temu / shein 等）
 * @param language - 输出语言
 * @returns 完整的 system prompt 字符串
 */
export function buildCopyPrompt(
  rawTitle: string,
  persona: Persona | null,
  platform: string = 'amazon',
  language: string = 'en',
): string {
  // 基础 prompt
  let prompt = `你是 ${platform} 平台专业运营，精通 SEO 和转化率优化。`
  prompt += `将以下商品信息改写为面向 ${language} 市场的 ${platform} Listing。`
  prompt += `输出格式：标题（不超过200字符） + 5条卖点 + 商品描述（含HTML标签）`

  // 拼接品牌调性（F5 Persona）
  if (persona) {
    const toneText = persona.tone_custom || persona.tone || 'professional'
    prompt += `\n\n品牌调性：${toneText}`

    if (persona.brand_name) {
      prompt += `\n品牌名称：${persona.brand_name}`
    }
    if (persona.tagline) {
      prompt += `\n品牌标语：${persona.tagline}`
    }
    if (persona.description) {
      prompt += `\n品牌描述：${persona.description}`
    }
    if (persona.banned_words && persona.banned_words.length > 0) {
      prompt += `\n用户指定禁用词：${persona.banned_words.join('、')}`
    }
  }

  // 追加平台违禁词硬性规则
  prompt += `\n\n平台违禁词硬性规则（命中必须改写或移除）：`
  prompt += `\n${PLATFORM_BANNED_RULES.join('\n')}`

  prompt += `\n\n原始商品信息：\n${rawTitle}`

  return prompt
}
