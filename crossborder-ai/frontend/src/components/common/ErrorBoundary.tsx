import { Component, type ErrorInfo, type ReactNode } from 'react'
import { Button } from '@/components/ui/button'

interface Props {
  children: ReactNode
}

interface State {
  error: Error | null
}

/**
 * 顶层错误边界：渲染期内任何组件 throw 都不至于白屏，
 * 而是落到这里给一个可恢复的兜底页（刷新即可）。
 * LLM 驱动的 UI 字段漂移（如 risks.map is not a function）就靠它兜住。
 */
export default class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null }

  static getDerivedStateFromError(error: Error): State {
    return { error }
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    // 记到控制台（接入 Sentry 后这里可上报）
    console.error('[ErrorBoundary] 页面渲染异常:', error, info)
  }

  handleReload = (): void => {
    // 渲染态错误往往已破坏 DOM，整页重载最稳妥
    window.location.reload()
  }

  render(): ReactNode {
    if (this.state.error) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-background p-6">
          <div className="max-w-md w-full text-center space-y-4">
            <div className="text-4xl">😵</div>
            <h1 className="text-xl font-bold tracking-tight">页面出了点问题</h1>
            <p className="text-sm text-muted-foreground">
              我们已记录这个错误。点击下方按钮刷新页面，通常就能恢复正常。
            </p>
            <Button onClick={this.handleReload}>刷新页面</Button>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}
