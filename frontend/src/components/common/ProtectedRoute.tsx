import { Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/app/authStore'
import { LoadingScreen } from './LoadingScreen'

interface ProtectedRouteProps {
    children: React.ReactNode
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
    const { isAuthenticated, isLoading } = useAuthStore()
    const location = useLocation()

    if (isLoading) {
        return <LoadingScreen />
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" state={{ from: location }} replace />
    }

    return <>{children}</>
}
