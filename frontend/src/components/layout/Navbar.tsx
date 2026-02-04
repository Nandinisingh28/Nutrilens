import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Menu, X, User, History, Settings, LogOut, Scan } from 'lucide-react'
import { useState } from 'react'
import { useAuthStore } from '@/app/authStore'
import { Button } from '@/components/ui/button'

export function Navbar() {
    const [isOpen, setIsOpen] = useState(false)
    const { user, logout, isAuthenticated } = useAuthStore()
    const navigate = useNavigate()

    const handleLogout = () => {
        logout()
        navigate('/login')
    }

    return (
        <nav className="sticky top-0 z-50 glass border-b border-gray-200/50">
            <div className="container">
                <div className="flex items-center justify-between h-16">
                    {/* Logo */}
                    <Link to={isAuthenticated ? '/app' : '/'} className="flex items-center space-x-2">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-teal-500 flex items-center justify-center">
                            <Scan className="w-5 h-5 text-white" />
                        </div>
                        <span className="font-bold text-xl gradient-text">NutriLens</span>
                    </Link>

                    {/* Desktop Navigation */}
                    {isAuthenticated && (
                        <div className="hidden md:flex items-center space-x-1">
                            <NavLink to="/app" icon={<Scan className="w-4 h-4" />}>
                                Scan
                            </NavLink>
                            <NavLink to="/app/history" icon={<History className="w-4 h-4" />}>
                                History
                            </NavLink>
                            <NavLink to="/app/profile" icon={<User className="w-4 h-4" />}>
                                Profile
                            </NavLink>
                            <NavLink to="/app/settings" icon={<Settings className="w-4 h-4" />}>
                                Settings
                            </NavLink>
                        </div>
                    )}

                    {/* User Menu */}
                    <div className="hidden md:flex items-center space-x-4">
                        {isAuthenticated ? (
                            <div className="flex items-center space-x-3">
                                <span className="text-sm text-muted-foreground">
                                    {user?.name || user?.email}
                                </span>
                                <Button variant="ghost" size="sm" onClick={handleLogout}>
                                    <LogOut className="w-4 h-4 mr-2" />
                                    Logout
                                </Button>
                            </div>
                        ) : (
                            <div className="flex items-center space-x-2">
                                <Button variant="ghost" asChild>
                                    <Link to="/login">Login</Link>
                                </Button>
                                <Button asChild>
                                    <Link to="/signup">Get Started</Link>
                                </Button>
                            </div>
                        )}
                    </div>

                    {/* Mobile menu button */}
                    <button
                        className="md:hidden p-2 rounded-lg hover:bg-gray-100"
                        onClick={() => setIsOpen(!isOpen)}
                    >
                        {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
                    </button>
                </div>

                {/* Mobile Navigation */}
                {isOpen && (
                    <motion.div
                        className="md:hidden py-4 border-t border-gray-200/50"
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                    >
                        {isAuthenticated ? (
                            <div className="space-y-2">
                                <MobileNavLink to="/app" onClick={() => setIsOpen(false)}>
                                    Scan
                                </MobileNavLink>
                                <MobileNavLink to="/app/history" onClick={() => setIsOpen(false)}>
                                    History
                                </MobileNavLink>
                                <MobileNavLink to="/app/profile" onClick={() => setIsOpen(false)}>
                                    Profile
                                </MobileNavLink>
                                <MobileNavLink to="/app/settings" onClick={() => setIsOpen(false)}>
                                    Settings
                                </MobileNavLink>
                                <button
                                    className="w-full text-left px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg"
                                    onClick={handleLogout}
                                >
                                    Logout
                                </button>
                            </div>
                        ) : (
                            <div className="space-y-2">
                                <MobileNavLink to="/login" onClick={() => setIsOpen(false)}>
                                    Login
                                </MobileNavLink>
                                <MobileNavLink to="/signup" onClick={() => setIsOpen(false)}>
                                    Sign Up
                                </MobileNavLink>
                            </div>
                        )}
                    </motion.div>
                )}
            </div>
        </nav>
    )
}

function NavLink({ to, icon, children }: { to: string; icon: React.ReactNode; children: React.ReactNode }) {
    return (
        <Link
            to={to}
            className="flex items-center space-x-2 px-3 py-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-gray-100 transition-colors"
        >
            {icon}
            <span>{children}</span>
        </Link>
    )
}

function MobileNavLink({ to, onClick, children }: { to: string; onClick: () => void; children: React.ReactNode }) {
    return (
        <Link
            to={to}
            className="block px-4 py-2 text-foreground hover:bg-gray-100 rounded-lg"
            onClick={onClick}
        >
            {children}
        </Link>
    )
}
