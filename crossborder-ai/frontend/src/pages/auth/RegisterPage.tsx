import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Globe, Eye, EyeOff, ArrowLeft } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useAuthStore } from '@/stores/authStore'

const registerSchema = z.object({
  email: z.string().email('邮箱格式不正确'),
  username: z.string().min(3, '用户名至少 3 个字符').max(100),
  password: z.string().min(6, '密码至少 6 个字符'),
  confirmPassword: z.string(),
}).refine((d) => d.password === d.confirmPassword, { message: '两次密码不一致', path: ['confirmPassword'] })

type RegisterForm = z.infer<typeof registerSchema>

export default function RegisterPage() {
  const navigate = useNavigate()
  const { register: registerUser, isLoading, error, clearError } = useAuthStore()
  const [step, setStep] = useState(1)
  const [showPassword, setShowPassword] = useState(false)

  const { register, handleSubmit, formState: { errors }, trigger } = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
    defaultValues: { email: '', username: '', password: '', confirmPassword: '' },
  })

  const onSubmit = async (data: RegisterForm) => {
    clearError()
    try {
      await registerUser({ email: data.email, username: data.username, password: data.password })
      navigate('/app/dashboard')
    } catch { /* handled by store */ }
  }

  const nextStep = async () => {
    const ok = await trigger(['email', 'username'])
    if (ok) setStep(2)
  }

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="w-full max-w-sm space-y-6">
        <div className="text-center">
          <Link to="/" className="inline-flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-indigo-600 flex items-center justify-center">
              <Globe className="h-4 w-4 text-white" />
            </div>
            <span className="font-bold text-lg text-slate-800">VeyaShip</span>
          </Link>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-5">
          <div>
            <h1 className="text-lg font-semibold text-slate-800">创建账号</h1>
            <p className="text-sm text-slate-500 mt-0.5">免费注册，开始使用</p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {error && (
              <div className="rounded-lg bg-red-50 border border-red-100 p-3 text-sm text-red-600">{error}</div>
            )}

            {step === 1 ? (
              <>
                <div className="space-y-1.5">
                  <Label className="text-sm text-slate-700">邮箱</Label>
                  <Input type="email" placeholder="you@company.com" {...register('email')}
                    className="h-10 rounded-lg border-slate-200" />
                  {errors.email && <p className="text-xs text-red-500">{errors.email.message}</p>}
                </div>
                <div className="space-y-1.5">
                  <Label className="text-sm text-slate-700">用户名</Label>
                  <Input placeholder="your-name" {...register('username')}
                    className="h-10 rounded-lg border-slate-200" />
                  {errors.username && <p className="text-xs text-red-500">{errors.username.message}</p>}
                </div>
                <Button type="button" onClick={nextStep} className="w-full h-10 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg">继续</Button>
              </>
            ) : (
              <>
                <button type="button" onClick={() => setStep(1)} className="flex items-center gap-1 text-sm text-slate-500 hover:text-slate-700">
                  <ArrowLeft className="h-3.5 w-3.5" />返回
                </button>
                <div className="space-y-1.5">
                  <Label className="text-sm text-slate-700">密码</Label>
                  <div className="relative">
                    <Input type={showPassword ? 'text' : 'password'} placeholder="至少 6 位" {...register('password')}
                      className="h-10 rounded-lg border-slate-200 pr-10" />
                    <button type="button" onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400">
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                  {errors.password && <p className="text-xs text-red-500">{errors.password.message}</p>}
                </div>
                <div className="space-y-1.5">
                  <Label className="text-sm text-slate-700">确认密码</Label>
                  <Input type="password" placeholder="再次输入密码" {...register('confirmPassword')}
                    className="h-10 rounded-lg border-slate-200" />
                  {errors.confirmPassword && <p className="text-xs text-red-500">{errors.confirmPassword.message}</p>}
                </div>
                <Button type="submit" disabled={isLoading} className="w-full h-10 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg">
                  {isLoading ? '注册中...' : '创建账号'}
                </Button>
              </>
            )}
          </form>

          <p className="text-center text-sm text-slate-500">
            已有账号？<Link to="/login" className="text-indigo-600 hover:text-indigo-700 font-medium">登录</Link>
          </p>
        </div>

        <p className="text-center"><Link to="/" className="text-xs text-slate-400 hover:text-slate-600">← 返回首页</Link></p>
      </div>
    </div>
  )
}
