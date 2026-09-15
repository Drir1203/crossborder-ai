/**
 * 把任意请求异常压成一句「可以直接显示给卖家」的中文提示。
 *
 * 后端 detail 有四种形态：字符串、{code, message} 对象、FastAPI 422 的
 * 对象数组、以及压根没有 detail（502 / 超时 / 断网）。
 * 直接把 detail 塞进 JSX，遇到对象或数组会抛
 * "Objects are not valid as a React child"，把整页顶成 ErrorBoundary 的报错页 ——
 * 所以显示前必须在这里拍平成字符串。
 *
 * 只放行含中文的文案：axios 自己的 message（"Network Error"、
 * "Request failed with status code 500"）和 Pydantic 的英文校验信息都不外露。
 */

const CJK_RE = /[一-鿿]/

interface DetailLike {
  message?: unknown
  msg?: unknown
}

/** 取第一个含中文的候选文案，全都不合格时返回 undefined */
function pickChinese(...candidates: unknown[]): string | undefined {
  for (const candidate of candidates) {
    if (typeof candidate === 'string' && candidate.trim() && CJK_RE.test(candidate)) {
      return candidate
    }
  }
  return undefined
}

export function toErrorMessage(err: unknown, fallback = '操作失败，请稍后重试'): string {
  const detail = (err as { response?: { data?: { detail?: unknown } } } | null)?.response?.data?.detail

  const fromDetailObject =
    detail && typeof detail === 'object' && !Array.isArray(detail)
      ? (detail as DetailLike).message
      : undefined

  const fromDetailArray = Array.isArray(detail)
    ? detail
        .map((item) => (item as DetailLike)?.message ?? (item as DetailLike)?.msg)
        .filter((msg): msg is string => typeof msg === 'string')
    : []

  return (
    pickChinese(
      typeof detail === 'string' ? detail : undefined,
      fromDetailObject,
      ...fromDetailArray,
      (err as { message?: unknown } | null)?.message,
    ) ?? fallback
  )
}
