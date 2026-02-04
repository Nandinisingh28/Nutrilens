import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useMutation } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { toast } from 'sonner'
import {
    Settings as SettingsIcon,
    Lock,
    Eye,
    EyeOff,
    Loader2,
    LogOut,
    Trash2,
    Shield,
    Bell,
    Moon,
    Check,
    X,
} from 'lucide-react'
import { useAuthStore } from '@/app/authStore'
import { useTheme } from '@/app/useTheme'
import { userApi, authApi } from '@/app/api'

const passwordSchema = z.object({
    current_password: z.string().min(1, 'Current password is required'),
    new_password: z
        .string()
        .min(8, 'Password must be at least 8 characters')
        .regex(/[A-Z]/, 'Password must contain an uppercase letter')
        .regex(/[a-z]/, 'Password must contain a lowercase letter')
        .regex(/[0-9]/, 'Password must contain a number'),
    confirm_password: z.string(),
}).refine((data) => data.new_password === data.confirm_password, {
    message: "Passwords don't match",
    path: ['confirm_password'],
})

type PasswordForm = z.infer<typeof passwordSchema>

const passwordRules = [
    { label: 'At least 8 characters', test: (p: string) => p.length >= 8 },
    { label: 'One uppercase letter', test: (p: string) => /[A-Z]/.test(p) },
    { label: 'One lowercase letter', test: (p: string) => /[a-z]/.test(p) },
    { label: 'One number', test: (p: string) => /[0-9]/.test(p) },
]

export default function Settings() {
    const navigate = useNavigate()
    const logout = useAuthStore((s) => s.logout)
    const { theme, setTheme } = useTheme()
    const [showCurrentPassword, setShowCurrentPassword] = useState(false)
    const [showNewPassword, setShowNewPassword] = useState(false)

    const {
        register,
        handleSubmit,
        watch,
        reset,
        formState: { errors },
    } = useForm<PasswordForm>({
        resolver: zodResolver(passwordSchema),
    })

    const newPassword = watch('new_password', '')

    const passwordMutation = useMutation({
        mutationFn: (data: PasswordForm) =>
            userApi.changePassword({
                current_password: data.current_password,
                new_password: data.new_password,
            }),
        onSuccess: () => {
            toast.success('Password changed successfully!')
            reset()
        },
        onError: (error: any) => {
            const message = error.response?.data?.message || 'Failed to change password'
            toast.error(message)
        },
    })

    const handleLogout = async () => {
        try {
            await authApi.logout()
        } catch {
            // Ignore logout errors
        }
        logout()
        navigate('/login')
        toast.success('Logged out successfully')
    }

    const onSubmit = (data: PasswordForm) => {
        passwordMutation.mutate(data)
    }

    return (
        <div className="max-w-2xl mx-auto">
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-8"
            >
                <h1 className="text-3xl font-bold mb-2">Settings</h1>
                <p className="text-muted-foreground">
                    Manage your account settings and preferences
                </p>
            </motion.div>

            <div className="space-y-6">
                {/* Security */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="glass-card p-6"
                >
                    <h2 className="font-semibold flex items-center gap-2 mb-6">
                        <Shield className="w-5 h-5 text-primary" />
                        Security
                    </h2>

                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Current Password</label>
                            <div className="relative">
                                <input
                                    {...register('current_password')}
                                    type={showCurrentPassword ? 'text' : 'password'}
                                    placeholder="••••••••"
                                    className="w-full px-4 py-3 rounded-xl border border-input bg-background focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none pr-12"
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                                >
                                    {showCurrentPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                                </button>
                            </div>
                            {errors.current_password && (
                                <p className="text-sm text-destructive">{errors.current_password.message}</p>
                            )}
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium">New Password</label>
                            <div className="relative">
                                <input
                                    {...register('new_password')}
                                    type={showNewPassword ? 'text' : 'password'}
                                    placeholder="••••••••"
                                    className="w-full px-4 py-3 rounded-xl border border-input bg-background focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none pr-12"
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowNewPassword(!showNewPassword)}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                                >
                                    {showNewPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                                </button>
                            </div>

                            {newPassword && (
                                <div className="grid grid-cols-2 gap-1 mt-2">
                                    {passwordRules.map((rule) => (
                                        <div
                                            key={rule.label}
                                            className={`flex items-center gap-1 text-xs ${rule.test(newPassword) ? 'text-green-600' : 'text-muted-foreground'
                                                }`}
                                        >
                                            {rule.test(newPassword) ? (
                                                <Check className="w-3 h-3" />
                                            ) : (
                                                <X className="w-3 h-3" />
                                            )}
                                            {rule.label}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium">Confirm New Password</label>
                            <input
                                {...register('confirm_password')}
                                type="password"
                                placeholder="••••••••"
                                className="w-full px-4 py-3 rounded-xl border border-input bg-background focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none"
                            />
                            {errors.confirm_password && (
                                <p className="text-sm text-destructive">{errors.confirm_password.message}</p>
                            )}
                        </div>

                        <button
                            type="submit"
                            disabled={passwordMutation.isPending}
                            className="w-full py-3 px-4 rounded-xl bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                        >
                            {passwordMutation.isPending ? (
                                <>
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                    Updating...
                                </>
                            ) : (
                                <>
                                    <Lock className="w-5 h-5" />
                                    Update Password
                                </>
                            )}
                        </button>
                    </form>
                </motion.div>

                {/* Preferences */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="glass-card p-6"
                >
                    <h2 className="font-semibold flex items-center gap-2 mb-6">
                        <SettingsIcon className="w-5 h-5 text-primary" />
                        Preferences
                    </h2>

                    <div className="space-y-4">
                        <div className="flex items-center justify-between py-3 border-b">
                            <div className="flex items-center gap-3">
                                <Bell className="w-5 h-5 text-muted-foreground" />
                                <div>
                                    <p className="font-medium">Push Notifications</p>
                                    <p className="text-sm text-muted-foreground">
                                        Get notified about scan results
                                    </p>
                                </div>
                            </div>
                            <label className="relative inline-flex items-center cursor-pointer">
                                <input type="checkbox" className="sr-only peer" />
                                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                            </label>
                        </div>

                        <div className="flex items-center justify-between py-3">
                            <div className="flex items-center gap-3">
                                <Moon className="w-5 h-5 text-muted-foreground" />
                                <div>
                                    <p className="font-medium">Dark Mode</p>
                                    <p className="text-sm text-muted-foreground">
                                        {theme === 'system' ? 'Follow system preference' : theme === 'dark' ? 'Always dark' : 'Always light'}
                                    </p>
                                </div>
                            </div>
                            <div className="flex items-center gap-2">
                                <button
                                    onClick={() => setTheme('light')}
                                    className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${theme === 'light'
                                        ? 'bg-primary text-primary-foreground'
                                        : 'bg-gray-100 dark:bg-gray-800 text-muted-foreground hover:bg-gray-200 dark:hover:bg-gray-700'
                                        }`}
                                >
                                    Light
                                </button>
                                <button
                                    onClick={() => setTheme('dark')}
                                    className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${theme === 'dark'
                                        ? 'bg-primary text-primary-foreground'
                                        : 'bg-gray-100 dark:bg-gray-800 text-muted-foreground hover:bg-gray-200 dark:hover:bg-gray-700'
                                        }`}
                                >
                                    Dark
                                </button>
                                <button
                                    onClick={() => setTheme('system')}
                                    className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${theme === 'system'
                                        ? 'bg-primary text-primary-foreground'
                                        : 'bg-gray-100 dark:bg-gray-800 text-muted-foreground hover:bg-gray-200 dark:hover:bg-gray-700'
                                        }`}
                                >
                                    System
                                </button>
                            </div>
                        </div>
                    </div>
                </motion.div>

                {/* Danger Zone */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="glass-card p-6 border-destructive/20"
                >
                    <h2 className="font-semibold text-destructive mb-6">Danger Zone</h2>

                    <div className="space-y-4">
                        <button
                            onClick={handleLogout}
                            className="w-full py-3 px-4 rounded-xl border border-input hover:bg-accent transition-all flex items-center justify-center gap-2"
                        >
                            <LogOut className="w-5 h-5" />
                            Sign Out
                        </button>

                        <button
                            className="w-full py-3 px-4 rounded-xl border border-destructive/30 text-destructive hover:bg-destructive/10 transition-all flex items-center justify-center gap-2"
                            onClick={() => toast.error('This feature is not yet available')}
                        >
                            <Trash2 className="w-5 h-5" />
                            Delete Account
                        </button>
                    </div>
                </motion.div>
            </div>
        </div>
    )
}
