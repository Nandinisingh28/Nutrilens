import { lazy, Suspense } from 'react'
import { Routes, Route } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import { AppShell } from '@/components/layout/AppShell'
import { LoadingScreen } from '@/components/common/LoadingScreen'
import { ProtectedRoute } from '@/components/common/ProtectedRoute'

// Lazy load pages for better performance
const Landing = lazy(() => import('@/pages/Landing'))
const Login = lazy(() => import('@/pages/Auth/Login'))
const Signup = lazy(() => import('@/pages/Auth/Signup'))
const ForgotPassword = lazy(() => import('@/pages/Auth/ForgotPassword'))
const ResetPassword = lazy(() => import('@/pages/Auth/ResetPassword'))
const CategorySelect = lazy(() => import('@/pages/App/CategorySelect'))
const Scan = lazy(() => import('@/pages/App/Scan'))
const Results = lazy(() => import('@/pages/App/Results'))
const History = lazy(() => import('@/pages/App/History'))
const Profile = lazy(() => import('@/pages/App/Profile'))
const Settings = lazy(() => import('@/pages/App/Settings'))

export function AppRouter() {
    return (
        <AnimatePresence mode="wait">
            <Suspense fallback={<LoadingScreen />}>
                <Routes>
                    {/* Public routes */}
                    <Route path="/" element={<Landing />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/signup" element={<Signup />} />
                    <Route path="/forgot-password" element={<ForgotPassword />} />
                    <Route path="/reset-password" element={<ResetPassword />} />

                    {/* Protected app routes */}
                    <Route element={<ProtectedRoute><AppShell /></ProtectedRoute>}>
                        <Route path="/app" element={<CategorySelect />} />
                        <Route path="/app/scan" element={<Scan />} />
                        <Route path="/app/results/:id" element={<Results />} />
                        <Route path="/app/history" element={<History />} />
                        <Route path="/app/profile" element={<Profile />} />
                        <Route path="/app/settings" element={<Settings />} />
                    </Route>
                </Routes>
            </Suspense>
        </AnimatePresence>
    )
}
