import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Globe, Eye, EyeOff } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useAuthStore } from '@/stores/authStore'

const loginSchema = z.object({
  email: z.string().email('邮箱格式不正确'),
  password: z.string().min(1, '请输入密码'),
})

type LoginForm = z.infer<typeof loginSchema>

export default function LoginPage() {
  const navigate = useNavigate()
  const { login, isLoading, error, clearError } = useAuthStore()
  const [showPassword, setShowPassword] = useState(false)

  const { register, handleSubmit, formState: { errors } } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: '', password: '' },
  })

  const onSubmit = async (data: LoginForm) => {
    clearError()
    try {
      await login(data.email, data.password)
      navigate('/app/dashboard')
    } catch { /* handled by store */ }
  }

  return (
    <div className="relative min-h-screen flex items-center justify-center p-4 overflow-hidden">
      {/* 高级感背景：aurora 光晕 + 细腻颗粒 */}
      <div className="aurora-layer" aria-hidden />
      <div className="glow glow-1" aria-hidden />
      <div className="glow glow-2" aria-hidden />
      <div className="grain" aria-hidden />

      <div className="relative z-10 w-full max-w-sm space-y-6">
        {/* Logo */}
        <div className="text-center">
          <Link to="/" className="inline-flex items-center gap-2">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-[var(--gradient-from)] to-[var(--gradient-to)] flex items-center justify-center shadow-[0_8px_24px_-8px_var(--glow-primary)]">
              <Globe className="h-4 w-4 text-[var(--gradient-foreground)]" />
            </div>
            <span className="font-bold text-lg text-foreground">VeyaShip AI</span>
          </Link>
        </div>

        {/* 玻璃卡片 */}
        <div className="relative rounded-2xl border-glass-border bg-glass backdrop-blur-xl shadow-[var(--card-shadow)] p-6 space-y-5 overflow-hidden">
          {/* 顶部高光条 */}
          <div className="absolute top-0 left-12 right-12 h-px bg-gradient-to-r from-transparent via-glass-highlight to-transparent" />

          <div>
            <h1 className="text-lg font-semibold text-foreground">登录</h1>
            <p className="text-sm text-muted-foreground mt-0.5">登录你的账号继续使用</p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {error && (
              <div className="rounded-lg bg-red-500/10 border border-red-500/30 p-3 text-sm text-red-600">{error}</div>
            )}

            <div className="space-y-1.5">
              <Label htmlFor="email" className="text-sm text-foreground">邮箱</Label>
              <Input id="email" type="email" placeholder="you@company.com" {...register('email')}
                className="h-10 rounded-lg border-glass-border bg-black/10 dark:bg-black/30" />
              {errors.email && <p className="text-xs text-red-500">{errors.email.message}</p>}
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="password" className="text-sm text-foreground">密码</Label>
              <div className="relative">
                <Input id="password" type={showPassword ? 'text' : 'password'} placeholder="输入密码" {...register('password')}
                  className="h-10 rounded-lg border-glass-border bg-black/10 dark:bg-black/30 pr-10" />
                <button type="button" onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground">
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
              {errors.password && <p className="text-xs text-red-500">{errors.password.message}</p>}
            </div>

            <Button type="submit" disabled={isLoading} className="w-full h-10 rounded-lg">
              {isLoading ? '登录中...' : '登录'}
            </Button>
          </form>

          <p className="text-center text-sm text-muted-foreground">
            还没有账号？<Link to="/register" className="text-primary hover:opacity-80 font-medium">注册</Link>
          </p>
        </div>

        <p className="text-center"><Link to="/" className="text-xs text-muted-foreground hover:text-foreground">← 返回首页</Link></p>
      </div>
    </div>
  )
}
