import { useState, useRef } from 'react'
import { motion } from 'framer-motion'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import {
    User,
    Camera,
    Loader2,
    Save,
    Mail,
    Calendar,
    Target,
} from 'lucide-react'
import { useAuthStore } from '@/app/authStore'
import { userApi, User as UserType } from '@/app/api'

const profileSchema = z.object({
    name: z.string().min(2, 'Name must be at least 2 characters'),
    bio: z.string().max(200, 'Bio must be 200 characters or less').optional(),
    age: z.number().min(13).max(120).optional().nullable(),
    gender: z.enum(['male', 'female', 'other', '']).optional(),
    goal: z.string().max(100).optional(),
})

type ProfileForm = z.infer<typeof profileSchema>

export default function Profile() {
    const queryClient = useQueryClient()
    const user = useAuthStore((s) => s.user)
    const setUser = useAuthStore((s) => s.setUser)
    const [isUploading, setIsUploading] = useState(false)
    const fileInputRef = useRef<HTMLInputElement>(null)

    const { data: userData, isLoading } = useQuery({
        queryKey: ['user', 'me'],
        queryFn: async () => {
            const response = await userApi.getMe()
            return response.data.data
        },
    })

    const profile = userData || user

    const {
        register,
        handleSubmit,
        formState: { errors, isDirty },
    } = useForm<ProfileForm>({
        resolver: zodResolver(profileSchema),
        values: {
            name: profile?.name || '',
            bio: profile?.bio || '',
            age: profile?.age || null,
            gender: (profile?.gender as 'male' | 'female' | 'other' | '') || '',
            goal: profile?.goal || '',
        },
    })

    const updateMutation = useMutation({
        mutationFn: (data: ProfileForm) =>
            userApi.updateMe({
                name: data.name,
                bio: data.bio || undefined,
                age: data.age || undefined,
                gender: data.gender || undefined,
                goal: data.goal || undefined,
            }),
        onSuccess: (response) => {
            const updatedUser = response.data.data
            setUser(updatedUser)
            queryClient.setQueryData(['user', 'me'], updatedUser)
            toast.success('Profile updated!')
        },
        onError: () => {
            toast.error('Failed to update profile')
        },
    })

    const handleAvatarClick = () => {
        fileInputRef.current?.click()
    }

    const handleAvatarChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (!file) return

        if (!file.type.startsWith('image/')) {
            toast.error('Please select an image file')
            return
        }

        if (file.size > 5 * 1024 * 1024) {
            toast.error('Image must be less than 5MB')
            return
        }

        setIsUploading(true)
        try {
            const response = await userApi.uploadAvatar(file)
            const avatarUrl = response.data.data.avatar_url
            if (profile) {
                const updatedUser = { ...profile, avatar_url: avatarUrl }
                setUser(updatedUser as UserType)
                queryClient.setQueryData(['user', 'me'], updatedUser)
            }
            toast.success('Avatar updated!')
        } catch {
            toast.error('Failed to upload avatar')
        } finally {
            setIsUploading(false)
        }
    }

    const onSubmit = (data: ProfileForm) => {
        updateMutation.mutate(data)
    }

    if (isLoading) {
        return (
            <div className="flex items-center justify-center py-20">
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
        )
    }

    return (
        <div className="max-w-2xl mx-auto">
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-8"
            >
                <h1 className="text-3xl font-bold mb-2">Profile</h1>
                <p className="text-muted-foreground">
                    Manage your account information
                </p>
            </motion.div>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                {/* Avatar */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="glass-card p-6"
                >
                    <h2 className="font-semibold mb-4">Profile Picture</h2>
                    <div className="flex items-center gap-6">
                        <div className="relative">
                            <div className="w-24 h-24 rounded-full bg-gradient-to-br from-primary to-teal-500 flex items-center justify-center overflow-hidden">
                                {profile?.avatar_url ? (
                                    <img
                                        src={profile.avatar_url}
                                        alt="Avatar"
                                        className="w-full h-full object-cover"
                                    />
                                ) : (
                                    <User className="w-12 h-12 text-white" />
                                )}
                            </div>
                            <button
                                type="button"
                                onClick={handleAvatarClick}
                                disabled={isUploading}
                                className="absolute -bottom-1 -right-1 w-8 h-8 bg-primary text-white rounded-full flex items-center justify-center shadow-lg hover:bg-primary/90 transition-colors disabled:opacity-50"
                            >
                                {isUploading ? (
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                ) : (
                                    <Camera className="w-4 h-4" />
                                )}
                            </button>
                            <input
                                ref={fileInputRef}
                                type="file"
                                accept="image/*"
                                onChange={handleAvatarChange}
                                className="hidden"
                            />
                        </div>
                        <div>
                            <p className="font-medium">{profile?.name}</p>
                            <p className="text-sm text-muted-foreground">{profile?.email}</p>
                        </div>
                    </div>
                </motion.div>

                {/* Basic Info */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="glass-card p-6 space-y-4"
                >
                    <h2 className="font-semibold">Basic Information</h2>

                    <div className="space-y-2">
                        <label className="text-sm font-medium">Name</label>
                        <input
                            {...register('name')}
                            type="text"
                            className="w-full px-4 py-3 rounded-xl border border-input bg-background focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none"
                        />
                        {errors.name && (
                            <p className="text-sm text-destructive">{errors.name.message}</p>
                        )}
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium flex items-center gap-2">
                            <Mail className="w-4 h-4" />
                            Email
                        </label>
                        <input
                            type="email"
                            value={profile?.email || ''}
                            disabled
                            className="w-full px-4 py-3 rounded-xl border border-input bg-muted text-muted-foreground cursor-not-allowed"
                        />
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium">Bio</label>
                        <textarea
                            {...register('bio')}
                            rows={3}
                            placeholder="Tell us about yourself..."
                            className="w-full px-4 py-3 rounded-xl border border-input bg-background focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none resize-none"
                        />
                        {errors.bio && (
                            <p className="text-sm text-destructive">{errors.bio.message}</p>
                        )}
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <label className="text-sm font-medium flex items-center gap-2">
                                <Calendar className="w-4 h-4" />
                                Age
                            </label>
                            <input
                                {...register('age', { valueAsNumber: true })}
                                type="number"
                                min={13}
                                max={120}
                                placeholder="25"
                                className="w-full px-4 py-3 rounded-xl border border-input bg-background focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none"
                            />
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium">Gender</label>
                            <select
                                {...register('gender')}
                                className="w-full px-4 py-3 rounded-xl border border-input bg-background focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none"
                            >
                                <option value="">Prefer not to say</option>
                                <option value="male">Male</option>
                                <option value="female">Female</option>
                                <option value="other">Other</option>
                            </select>
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium flex items-center gap-2">
                            <Target className="w-4 h-4" />
                            Health Goal
                        </label>
                        <input
                            {...register('goal')}
                            type="text"
                            placeholder="e.g., Reduce sugar intake"
                            className="w-full px-4 py-3 rounded-xl border border-input bg-background focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none"
                        />
                    </div>
                </motion.div>

                {/* Submit */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                >
                    <button
                        type="submit"
                        disabled={!isDirty || updateMutation.isPending}
                        className="w-full py-3 px-4 rounded-xl bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                    >
                        {updateMutation.isPending ? (
                            <>
                                <Loader2 className="w-5 h-5 animate-spin" />
                                Saving...
                            </>
                        ) : (
                            <>
                                <Save className="w-5 h-5" />
                                Save Changes
                            </>
                        )}
                    </button>
                </motion.div>
            </form>
        </div>
    )
}
