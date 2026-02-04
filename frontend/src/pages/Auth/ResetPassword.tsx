import { useState, useMemo } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { toast } from 'sonner'
import { Eye, EyeOff, Loader2, KeyRound, Leaf, Check, X, CheckCircle } from 'lucide-react'
import { authApi } from '@/app/api'

const resetSchema = z.object({
    password: z
        .string()
        .min(8, 'Password must be at least 8 characters')
        .regex(/[A-Z]/, 'Password must contain an uppercase letter')
        .regex(/[a-z]/, 'Password must contain a lowercase letter')
        .regex(/[0-9]/, 'Password must contain a number'),
    confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ['confirmPassword'],
})

type ResetForm = z.infer<typeof resetSchema>

const passwordRules = [
    { label: 'At least 8 characters', test: (p: string) => p.length >= 8 },
    { label: 'One uppercase letter', test: (p: string) => /[A-Z]/.test(p) },
    { label: 'One lowercase letter', test: (p: string) => /[a-z]/.test(p) },
    { label: 'One number', test: (p: string) => /[0-9]/.test(p) },
]

export default function ResetPassword() {
    const navigate = useNavigate()
    const [searchParams] = useSearchParams()
    const token = searchParams.get('token')
    const [showPassword, setShowPassword] = useState(false)
    const [isLoading, setIsLoading] = useState(false)
    const [isSuccess, setIsSuccess] = useState(false)

    const {
        register,
        handleSubmit,
        watch,
        formState: { errors },
    } = useForm<ResetForm>({
        resolver: zodResolver(resetSchema),
    })

    const password = watch('password', '')

    const passwordStrength = useMemo(() => {
        const passed = passwordRules.filter((r) => r.test(password)).length
        return {
            score: passed,
            percent: (passed / passwordRules.length) * 100,
            color:
                passed === 0 ? 'bg-gray-200' :
                    passed === 1 ? 'bg-red-500' :
                        passed === 2 ? 'bg-orange-500' :
                            passed === 3 ? 'bg-yellow-500' :
                                'bg-green-500',
        }
    }, [password])

    const onSubmit = async (data: ResetForm) => {
        if (!token) {
            toast.error('Invalid reset link')
            return
        }

        setIsLoading(true)
        try {
            await authApi.resetPassword(token, data.password)
            setIsSuccess(true)
            toast.success('Password reset successfully!')
            setTimeout(() => navigate('/login'), 2000)
        } catch (error: any) {
            const message = error.response?.data?.message || 'Failed to reset password'
            toast.error(message)
        } finally {
            setIsLoading(false)
        }
    }

    if (!token) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50 flex items-center justify-center p-4">
                <div className="glass-card p-8 max-w-md text-center">
                    <h2 className="text-xl font-semibold mb-4">Invalid Reset Link</h2>
                    <p className="text-muted-foreground mb-4">
                        This password reset link is invalid or has expired.
                    </p>
                    <Link
                        to="/forgot-password"
                        className="inline-flex items-center justify-center py-2 px-4 rounded-xl bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-all"
                    >
                        Request a new link
                    </Link>
                </div>
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50 flex items-center justify-center p-4">
            <div className="absolute inset-0 overflow-hidden">
                <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary/10 rounded-full blur-3xl" />
                <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-teal-500/10 rounded-full blur-3xl" />
            </div>

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="relative w-full max-w-md"
            >
                <div className="glass-card p-8">
                    <div className="text-center mb-8">
                        <Link to="/" className="inline-flex items-center gap-2 text-2xl font-bold">
                            <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center">
                                <Leaf className="w-6 h-6 text-white" />
                            </div>
                            <span className="gradient-text">NutriLens</span>
                        </Link>
                    </div>

                    {isSuccess ? (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="text-center space-y-4"
                        >
                            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto">
                                <CheckCircle className="w-8 h-8 text-green-600" />
                            </div>
                            <h2 className="text-xl font-semibold">Password Reset!</h2>
                            <p className="text-muted-foreground">
                                Your password has been successfully reset. Redirecting to login...
                            </p>
                        </motion.div>
                    ) : (
                        <>
                            <div className="text-center mb-6">
                                <h2 className="text-xl font-semibold mb-2">Set new password</h2>
                                <p className="text-muted-foreground text-sm">
                                    Create a strong password for your account.
                                </p>
                            </div>

                            <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
                                <div className="space-y-2">
                                    <label className="text-sm font-medium">New Password</label>
                                    <div className="relative">
                                        <input
                                            {...register('password')}
                                            type={showPassword ? 'text' : 'password'}
                                            placeholder="••••••••"
                                            className="w-full px-4 py-3 rounded-xl border border-input bg-background focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none pr-12"
                                            disabled={isLoading}
                                        />
                                        <button
                                            type="button"
                                            onClick={() => setShowPassword(!showPassword)}
                                            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                                        >
                                            {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                                        </button>
                                    </div>

                                    {password && (
                                        <div className="space-y-2">
                                            <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                                                <motion.div
                                                    className={`h-full ${passwordStrength.color} transition-colors`}
                                                    initial={{ width: 0 }}
                                                    animate={{ width: `${passwordStrength.percent}%` }}
                                                    transition={{ duration: 0.3 }}
                                                />
                                            </div>
                                            <div className="grid grid-cols-2 gap-1">
                                                {passwordRules.map((rule) => (
                                                    <div
                                                        key={rule.label}
                                                        className={`flex items-center gap-1 text-xs ${rule.test(password) ? 'text-green-600' : 'text-muted-foreground'
                                                            }`}
                                                    >
                                                        {rule.test(password) ? (
                                                            <Check className="w-3 h-3" />
                                                        ) : (
                                                            <X className="w-3 h-3" />
                                                        )}
                                                        {rule.label}
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>

                                <div className="space-y-2">
                                    <label className="text-sm font-medium">Confirm Password</label>
                                    <input
                                        {...register('confirmPassword')}
                                        type="password"
                                        placeholder="••••••••"
                                        className="w-full px-4 py-3 rounded-xl border border-input bg-background focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none"
                                        disabled={isLoading}
                                    />
                                    {errors.confirmPassword && (
                                        <p className="text-sm text-destructive">{errors.confirmPassword.message}</p>
                                    )}
                                </div>

                                <button
                                    type="submit"
                                    disabled={isLoading}
                                    className="w-full py-3 px-4 rounded-xl bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                                >
                                    {isLoading ? (
                                        <>
                                            <Loader2 className="w-5 h-5 animate-spin" />
                                            Resetting...
                                        </>
                                    ) : (
                                        <>
                                            <KeyRound className="w-5 h-5" />
                                            Reset Password
                                        </>
                                    )}
                                </button>
                            </form>
                        </>
                    )}
                </div>
            </motion.div>
        </div>
    )
}
