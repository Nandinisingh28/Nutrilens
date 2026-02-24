import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link, useNavigate, Outlet, useLocation } from 'react-router-dom';
import { Menu, X, User, History, LogOut, ChevronDown, Target, Zap, LayoutDashboard } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const DashboardLayout = () => {
    const [menuOpen, setMenuOpen] = useState(false);
    const [profileOpen, setProfileOpen] = useState(false);
    const navigate = useNavigate();
    const location = useLocation();
    const { user, logout } = useAuth();

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    const menuItems = [
        { icon: LayoutDashboard, label: 'Dashboard', href: '/dashboard' },
        { icon: Target, label: 'Precision Scan', href: '/scan/precision' },
        { icon: Zap, label: 'Quick Scan', href: '/scan/quick' },
        { icon: History, label: 'History', href: '/history' },
        { icon: User, label: 'Profile', href: '/profile' },
    ];

    const isActive = (href) => location.pathname === href;

    return (
        <div className="min-h-screen bg-black">
            {/* Header */}
            <header className="fixed top-0 left-0 right-0 z-50 bg-black/80 backdrop-blur-xl border-b border-white/10">
                <div className="max-w-[1400px] mx-auto px-6 py-4 flex items-center justify-between">
                    {/* Left - Menu Button */}
                    <div className="relative">
                        <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={() => { setMenuOpen(!menuOpen); setProfileOpen(false); }}
                            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 border border-white/10 text-white hover:bg-white/10 transition-colors"
                        >
                            {menuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
                            <span className="hidden sm:inline text-sm font-medium">Menu</span>
                        </motion.button>

                        <AnimatePresence>
                            {menuOpen && (
                                <motion.div
                                    initial={{ opacity: 0, y: 10, scale: 0.95 }}
                                    animate={{ opacity: 1, y: 0, scale: 1 }}
                                    exit={{ opacity: 0, y: 10, scale: 0.95 }}
                                    transition={{ duration: 0.15 }}
                                    className="absolute top-full left-0 mt-2 w-60 bg-gray-950/95 backdrop-blur-xl rounded-2xl border border-white/10 shadow-2xl overflow-hidden"
                                >
                                    <div className="p-2">
                                        {menuItems.map((item) => (
                                            <Link
                                                key={item.label}
                                                to={item.href}
                                                onClick={() => setMenuOpen(false)}
                                                className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-colors ${isActive(item.href) ? 'bg-nutri-mint/10 text-nutri-mint' : 'text-gray-300 hover:text-white hover:bg-white/10'}`}
                                            >
                                                <item.icon className={`w-5 h-5 ${isActive(item.href) ? 'text-nutri-mint' : 'text-gray-500'}`} />
                                                <span className="font-medium text-sm">{item.label}</span>
                                            </Link>
                                        ))}
                                        <div className="border-t border-white/10 my-2" />
                                        <button
                                            onClick={handleLogout}
                                            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-red-400 hover:text-red-300 hover:bg-red-500/10 transition-colors"
                                        >
                                            <LogOut className="w-5 h-5" />
                                            <span className="font-medium text-sm">Logout</span>
                                        </button>
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>

                    {/* Center - Logo */}
                    <Link to="/dashboard" className="flex items-center gap-2">
                        <img src="/logo.png" alt="NutriLens" className="w-8 h-8" />
                        <span className="text-xl font-bold text-white">
                            Nutri<span className="text-nutri-mint">Lens</span>
                        </span>
                    </Link>

                    {/* Right - Profile */}
                    <div className="relative">
                        <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={() => { setProfileOpen(!profileOpen); setMenuOpen(false); }}
                            className="flex items-center gap-2 px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white hover:bg-white/10 transition-colors"
                        >
                            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-nutri-mint to-teal-500 flex items-center justify-center">
                                <span className="text-sm font-bold text-black">
                                    {user?.name?.charAt(0).toUpperCase() || 'U'}
                                </span>
                            </div>
                            <ChevronDown className={`w-4 h-4 transition-transform duration-200 ${profileOpen ? 'rotate-180' : ''}`} />
                        </motion.button>

                        <AnimatePresence>
                            {profileOpen && (
                                <motion.div
                                    initial={{ opacity: 0, y: 10, scale: 0.95 }}
                                    animate={{ opacity: 1, y: 0, scale: 1 }}
                                    exit={{ opacity: 0, y: 10, scale: 0.95 }}
                                    transition={{ duration: 0.15 }}
                                    className="absolute top-full right-0 mt-2 w-64 bg-gray-950/95 backdrop-blur-xl rounded-2xl border border-white/10 shadow-2xl overflow-hidden"
                                >
                                    <div className="p-4 border-b border-white/10">
                                        <div className="flex items-center gap-3">
                                            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-nutri-mint to-teal-500 flex items-center justify-center">
                                                <span className="text-lg font-bold text-black">
                                                    {user?.name?.charAt(0).toUpperCase() || 'U'}
                                                </span>
                                            </div>
                                            <div className="min-w-0">
                                                <p className="font-semibold text-white truncate">{user?.name || 'User'}</p>
                                                <p className="text-sm text-gray-400 truncate">{user?.email}</p>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="p-2">
                                        <Link
                                            to="/profile"
                                            onClick={() => setProfileOpen(false)}
                                            className="flex items-center gap-3 px-4 py-3 rounded-xl text-gray-300 hover:text-white hover:bg-white/10 transition-colors"
                                        >
                                            <User className="w-5 h-5 text-nutri-mint" />
                                            <span className="font-medium text-sm">View Profile</span>
                                        </Link>
                                        <Link
                                            to="/history"
                                            onClick={() => setProfileOpen(false)}
                                            className="flex items-center gap-3 px-4 py-3 rounded-xl text-gray-300 hover:text-white hover:bg-white/10 transition-colors"
                                        >
                                            <History className="w-5 h-5 text-nutri-mint" />
                                            <span className="font-medium text-sm">Scan History</span>
                                        </Link>
                                        <button
                                            onClick={handleLogout}
                                            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-red-400 hover:text-red-300 hover:bg-red-500/10 transition-colors"
                                        >
                                            <LogOut className="w-5 h-5" />
                                            <span className="font-medium text-sm">Logout</span>
                                        </button>
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="pt-20 min-h-screen">
                <Outlet />
            </main>

            {/* Click-outside overlay for dropdowns */}
            {(menuOpen || profileOpen) && (
                <div
                    className="fixed inset-0 z-40"
                    onClick={() => { setMenuOpen(false); setProfileOpen(false); }}
                />
            )}
        </div>
    );
};

export default DashboardLayout;
