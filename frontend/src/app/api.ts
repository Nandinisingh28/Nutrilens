import axios from 'axios'
import { useAuthStore } from '@/app/authStore'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
    baseURL: `${API_URL}/api`,
    headers: {
        'Content-Type': 'application/json',
    },
})

// Request interceptor to add auth token
api.interceptors.request.use(
    (config) => {
        const token = useAuthStore.getState().accessToken
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => Promise.reject(error)
)

// Response interceptor to handle token refresh
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config

        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true

            const refreshToken = useAuthStore.getState().refreshToken

            if (refreshToken) {
                try {
                    const response = await axios.post(`${API_URL}/api/auth/refresh`, {
                        refresh_token: refreshToken,
                    })

                    const { access_token, refresh_token } = response.data.data
                    useAuthStore.getState().setTokens(access_token, refresh_token)

                    originalRequest.headers.Authorization = `Bearer ${access_token}`
                    return api(originalRequest)
                } catch (refreshError) {
                    useAuthStore.getState().logout()
                    window.location.href = '/login'
                    return Promise.reject(refreshError)
                }
            }
        }

        return Promise.reject(error)
    }
)

// Types
export interface ApiResponse<T> {
    success: boolean
    message: string
    data: T
    error: { code: string; details?: unknown } | null
}

export interface User {
    id: number
    email: string
    name: string
    bio?: string
    age?: number
    gender?: string
    goal?: string
    avatar_url?: string
    is_verified: boolean
    created_at: string
}

export interface Category {
    id: number
    slug: string
    title: string
    description?: string
}

export interface ClaimResult {
    claim: string
    normalized_claim_key: string
    verdict: 'true' | 'misleading' | 'false' | 'unknown'
    confidence: number
    evidence: string[]
    explanation: string
    suggestions: string[]
}

export interface ScanResults {
    product: {
        name?: string
        brand?: string
        category_id?: number
    }
    ocr: {
        raw_text: string
        cleaned_text: string
        confidence: number
        word_count: number
    }
    ingredients: {
        raw_text: string
        count: number
        list: Array<{
            name: string
            position: number
            is_sugar_alias: boolean
            is_additive: boolean
            is_preservative: boolean
        }>
        sugar_aliases_found: string[]
        has_sugar_alias: boolean
        has_preservatives: boolean
    }
    nutrition: {
        raw_text: string
        reference: string
        serving_size?: { value: number; unit: string }
        values: Record<string, number>
        normalized_per_100g: Record<string, number>
        has_values: boolean
    }
    claims: ClaimResult[]
    overall: {
        verdict: 'true' | 'misleading' | 'false' | 'mixed' | 'unknown'
        confidence: number
        summary: string
        claim_count: number
        breakdown: Record<string, number>
    }
    metadata?: {
        processing_time_seconds: number
        timestamp: string
    }
}

export interface Scan {
    id: number
    product_name?: string
    brand?: string
    category_id: number
    claim_text?: string
    overall_verdict: 'true' | 'misleading' | 'false' | 'mixed' | 'unknown'
    results?: ScanResults
    ocr_raw_text?: string
    parsed_ingredients?: Record<string, unknown>
    parsed_nutrition?: Record<string, unknown>
    created_at: string
    updated_at?: string
}

export interface TokenResponse {
    access_token: string
    refresh_token: string
    token_type: string
    expires_in: number
    user: User
}

// API functions
export const authApi = {
    signup: (data: { email: string; password: string; name: string }) =>
        api.post<ApiResponse<{ user: User }>>('/auth/signup', data),

    login: (data: { email: string; password: string }) =>
        api.post<ApiResponse<TokenResponse>>('/auth/login', data),

    logout: () => api.post<ApiResponse<null>>('/auth/logout'),

    refresh: (refreshToken: string) =>
        api.post<ApiResponse<TokenResponse>>('/auth/refresh', { refresh_token: refreshToken }),

    forgotPassword: (email: string) =>
        api.post<ApiResponse<null>>('/auth/forgot-password', { email }),

    resetPassword: (token: string, password: string) =>
        api.post<ApiResponse<null>>('/auth/reset-password', { token, new_password: password }),
}

export const userApi = {
    getMe: () => api.get<ApiResponse<User>>('/users/me'),

    updateMe: (data: Partial<{ name: string; bio: string; age: number; gender: string; goal: string }>) =>
        api.put<ApiResponse<User>>('/users/me', data),

    uploadAvatar: (file: File) => {
        const formData = new FormData()
        formData.append('file', file)
        return api.post<ApiResponse<{ avatar_url: string }>>('/users/me/avatar', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        })
    },

    changePassword: (data: { current_password: string; new_password: string }) =>
        api.put<ApiResponse<null>>('/users/me/password', data),
}

export const categoryApi = {
    getAll: () => api.get<ApiResponse<Category[]>>('/categories'),
}

export const scanApi = {
    create: (data: {
        image?: File
        ingredients_image?: File
        nutrition_image?: File
        category_id: number
        claim_text?: string
        product_name?: string
        brand?: string
    }) => {
        const formData = new FormData()
        if (data.image) formData.append('image', data.image)
        if (data.ingredients_image) formData.append('ingredients_image', data.ingredients_image)
        if (data.nutrition_image) formData.append('nutrition_image', data.nutrition_image)

        formData.append('category_id', data.category_id.toString())
        if (data.claim_text) formData.append('claim_text', data.claim_text)
        if (data.product_name) formData.append('product_name', data.product_name)
        if (data.brand) formData.append('brand', data.brand)

        return api.post<ApiResponse<Scan>>('/scans', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        })
    },

    getAll: (params?: { page?: number; per_page?: number; category_id?: number; verdict?: string }) =>
        api.get<ApiResponse<Scan[]> & { meta: { page: number; per_page: number; total: number; total_pages: number } }>('/scans', { params }),

    getById: (id: number) => api.get<ApiResponse<Scan>>(`/scans/${id}`),

    delete: (id: number) => api.delete<ApiResponse<null>>(`/scans/${id}`),

    bulkDelete: (ids: number[]) => api.delete<ApiResponse<{ deleted_count: number }>>('/scans', { params: { scan_ids: ids } }),

    reprocess: (id: number) => api.post<ApiResponse<Scan>>(`/scans/${id}/reprocess`),
}
