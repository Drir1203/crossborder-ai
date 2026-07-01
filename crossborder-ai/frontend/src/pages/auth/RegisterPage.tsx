import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useTranslation } from 'react-i18next'
import { Globe } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { useAuthStore } from '@/stores/authStore'

const registerSchema = z.object({
  email: z.string().email('Invalid email address'),
  username: z.string().min(3, 'Username must be at least 3 characters').max(100),
  password: z.string().min(6, 'Password must be at least 6 characters'),
  confirmPassword: z.string(),
  full_name: z.string().optional(),
  company_name: z.string().optional(),
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword'],
})

type RegisterForm = z.infer<typeof registerSchema>

export default function RegisterPage() {
  const navigate = useNavigate()
  const { register: registerUser, isLoading, error, clearError } = useAuthStore()
  const { t } = useTranslation()
  const [step, setStep] = useState<1 | 2>(1)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
    defaultValues: { email: '', username: '', password: '', confirmPassword: '' },
  })

  const onSubmit = async (data: RegisterForm) => {
    clearError()
    try {
      await registerUser({
        email: data.email,
        username: data.username,
        password: data.password,
        full_name: data.full_name,
        company_name: data.company_name,
      })
      navigate('/dashboard')
    } catch {
      // Error handled by store
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-background via-background to-primary/5 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1 text-center">
          <div className="mb-4 flex justify-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary">
              <Globe className="h-6 w-6 text-primary-foreground" />
            </div>
          </div>
          <CardTitle className="text-2xl font-bold">{t('auth.createAccount')}</CardTitle>
          <CardDescription>
            {t('auth.startJourney')}
          </CardDescription>
        </CardHeader>

        <form onSubmit={handleSubmit(onSubmit)}>
          <CardContent className="space-y-4">
            {error && (
              <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
                {error}
              </div>
            )}

            {step === 1 ? (
              <>
                <div className="space-y-2">
                  <Label htmlFor="email">{t('auth.email')}</Label>
                  <Input id="email" type="email" placeholder="you@company.com" {...register('email')} />
                  {errors.email && <p className="text-xs text-destructive">{t('auth.invalidEmail')}</p>}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="username">{t('auth.username')}</Label>
                  <Input id="username" placeholder="your-username" {...register('username')} />
                  {errors.username && <p className="text-xs text-destructive">{t('auth.usernameMin')}</p>}
                </div>
                <Button type="button" className="w-full" onClick={() => setStep(2)}>
                  {t('auth.continue')}
                </Button>
              </>
            ) : (
              <>
                <div className="space-y-2">
                  <Label htmlFor="full_name">{t('auth.fullName')}</Label>
                  <Input id="full_name" placeholder="John Doe" {...register('full_name')} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="company_name">{t('auth.companyName')}</Label>
                  <Input id="company_name" placeholder="My Store Inc." {...register('company_name')} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="password">{t('auth.password')}</Label>
                  <Input id="password" type="password" placeholder="At least 6 characters" {...register('password')} />
                  {errors.password && <p className="text-xs text-destructive">{t('auth.passwordMin')}</p>}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">{t('auth.confirmPassword')}</Label>
                  <Input id="confirmPassword" type="password" placeholder="Repeat password" {...register('confirmPassword')} />
                  {errors.confirmPassword && <p className="text-xs text-destructive">{t('auth.passwordsNotMatch')}</p>}
                </div>
                <div className="flex gap-2">
                  <Button type="button" variant="outline" className="flex-1" onClick={() => setStep(1)}>
                    {t('auth.back')}
                  </Button>
                  <Button type="submit" className="flex-1" disabled={isLoading}>
                    {isLoading ? t('common.loading') : t('auth.signUpBtn')}
                  </Button>
                </div>
              </>
            )}
          </CardContent>

          <CardFooter className="justify-center">
            <p className="text-sm text-muted-foreground">
              {t('auth.hasAccount')}{' '}
              <Link to="/login" className="font-medium text-primary hover:underline">
                {t('auth.signInBtn')}
              </Link>
            </p>
          </CardFooter>
        </form>
      </Card>
    </div>
  )
}
