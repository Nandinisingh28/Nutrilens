import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { ThemeProvider } from './context/ThemeContext'
import ProtectedRoute from './components/ProtectedRoute'
import Layout from './components/Layout'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import ScrollToTop from './components/ScrollToTop'

// Pages
import Landing from './pages/Landing'
import About from './pages/About'
import Welcome from './pages/Welcome'
import Login from './pages/Login'
import Signup from './pages/Signup'
import Dashboard from './pages/Dashboard'
import PrecisionScan from './pages/PrecisionScan'
import QuickScan from './pages/QuickScan'
import Results from './pages/Results'
import History from './pages/History'
import Profile from './pages/Profile'
import EditProfile from './pages/EditProfile'
import ForgotPassword from './pages/ForgotPassword'
import ResetPassword from './pages/ResetPassword'

// Public layout: Navbar + Footer wrapping child routes
const PublicLayout = () => (
    <div className="min-h-screen bg-black font-sans text-white">
        <Navbar />
        <main>
            <Outlet />
        </main>
        <Footer />
    </div>
)

function App() {
    return (
        <BrowserRouter>
            <ScrollToTop />
            <ThemeProvider>
                <AuthProvider>
                    <Routes>
                        {/* Welcome — standalone, no chrome */}
                        <Route path="/welcome" element={<Welcome />} />

                        {/* Protected Routes — require auth, wrapped in DashboardLayout */}
                        <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
                            <Route path="/dashboard" element={<Dashboard />} />
                            <Route path="/scan/precision" element={<PrecisionScan />} />
                            <Route path="/scan/quick" element={<QuickScan />} />
                            <Route path="/results/:id" element={<Results />} />
                            <Route path="/history" element={<History />} />
                            <Route path="/profile" element={<Profile />} />
                            <Route path="/profile/edit" element={<EditProfile />} />
                        </Route>

                        {/* Public Routes — Navbar + Footer */}
                        <Route element={<PublicLayout />}>
                            <Route path="/" element={<Landing />} />
                            <Route path="/login" element={<Login />} />
                            <Route path="/signup" element={<Signup />} />
                            <Route path="/about" element={<About />} />
                            <Route path="/forgot-password" element={<ForgotPassword />} />
                            <Route path="/reset-password" element={<ResetPassword />} />
                        </Route>

                        {/* Catch all */}
                        <Route path="*" element={<Navigate to="/" replace />} />
                    </Routes>
                </AuthProvider>
            </ThemeProvider>
        </BrowserRouter>
    )
}

export default App
