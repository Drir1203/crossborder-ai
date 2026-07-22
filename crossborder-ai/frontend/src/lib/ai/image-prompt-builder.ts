// VeyaShip AI Image Prompt Builder
// 构建发送给 FLUX 的图片 prompt，拼接品牌调性

export interface Persona {
  brand_name?: string | null
  tagline?: string | null
  tone?: string | null
  tone_custom?: string | null
}

/**
 * 构建 FLUX 图片生成的完整 prompt
 *
 * @param text - 用户输入的图片描述或商品标题
 * @param persona - 用户的品牌调性配置（可为 null）
 * @returns 完整的 FLUX prompt
 */
export function buildImagePrompt(text: string, persona: Persona | null): string {
  let prompt = `Professional e-commerce product photo, ${text}`

  // 拼接品牌调性
  if (persona) {
    const toneText = persona.tone_custom || persona.tone || 'modern'
    prompt += `, ${toneText} style`

    if (persona.brand_name) {
      prompt += `, ${persona.brand_name} brand identity`
    }
  }

  // 标准商品图后缀
  prompt += `, white background, studio lighting, 8K, photorealistic, commercial photography, sharp focus`

  return prompt
}
