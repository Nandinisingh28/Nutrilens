import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link, useNavigate, Outlet, useLocation } from 'react-router-dom';
import { Menu, X, User, History, LogOut, ChevronDown, Target, Zap, LayoutDashboard } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import Footer from './Footer';

const Layout = () => {
    const [mobileOpen, setMobileOpen] = useState(false);
    const [profileOpen, setProfileOpen] = useState(false);
    const [scrolled, setScrolled] = useState(false);
    const navigate = useNavigate();
    const location = useLocation();
    const { user, logout } = useAuth();

    useEffect(() => {
        const handleScroll = () => {
            setScrolled(window.scrollY > 20);
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const handleLogout = async () => {
        await logout();
        navigate('/');
    };

    const navLinks = [
        { label: 'Dashboard', href: '/dashboard' },
        { label: 'Precision Scan', href: '/scan/precision' },
        { label: 'Quick Scan', href: '/scan/quick' },
        { label: 'History', href: '/history' },
    ];

    const isActive = (href) => location.pathname === href;

    return (
        <div className="min-h-screen bg-black">
            {/* Header — mirrors Navbar.jsx structure */}
            <nav
                className={`fixed top-0 w-full z-50 transition-all duration-300 ${scrolled
                    ? 'bg-black/50 backdrop-blur-md border-b border-white/10 py-4'
                    : 'bg-transparent py-6'
                    }`}
            >
                <div className="max-w-[1400px] mx-auto px-6 md:px-12">
                    <div className="flex justify-between items-center">
                        {/* Logo */}
                        <Link to="/" className="flex-shrink-0 flex items-center cursor-pointer group gap-3">
                            <img src="/logo.png" alt="NutriLens Logo" className="h-10 w-auto brightness-0 invert" />
                            <span className="text-2xl font-bold text-white tracking-tight">
                                Nutri<span className="text-nutri-mint">Lens</span>
                            </span>
                        </Link>

                        {/* Desktop Nav Links — inline, matching pre-login style */}
                        <div className="hidden md:flex items-center space-x-10">
                            {navLinks.map((link) => (
                                <Link
                                    key={link.label}
                                    to={link.href}
                                    className={`relative text-sm font-medium overflow-hidden group ${isActive(link.href) ? 'text-white' : 'text-gray-300'}`}
                                >
                                    <span className="block transition-transform duration-300 group-hover:-translate-y-full">
                                        {link.label}
                                    </span>
                                    <span className="absolute inset-0 block translate-y-full transition-transform duration-300 group-hover:translate-y-0 text-white">
                                        {link.label}
                                    </span>
                                    {isActive(link.href) && (
                                        <span className="absolute -bottom-1 left-0 w-full h-0.5 bg-nutri-mint rounded-full" />
                                    )}
                                </Link>
                            ))}
                        </div>

                        {/* Right — Profile Avatar Dropdown */}
                        <div className="hidden md:flex items-center">
                            <div className="relative">
                                <motion.button
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                    onClick={() => setProfileOpen(!profileOpen)}
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

                        {/* Mobile menu button */}
                        <div className="md:hidden flex items-center">
                            <button
                                onClick={() => setMobileOpen(!mobileOpen)}
                                className="text-white hover:text-gray-300 focus:outline-none p-2"
                            >
                                {mobileOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
                            </button>
                        </div>
                    </div>
                </div>

                {/* Mobile Menu */}
                {mobileOpen && (
                    <div className="md:hidden bg-black/95 backdrop-blur-xl border-b border-white/10 absolute top-full left-0 w-full shadow-2xl">
                        <div className="px-6 pt-4 pb-8 space-y-1">
                            {navLinks.map((link) => (
                                <Link
                                    key={link.label}
                                    to={link.href}
                                    onClick={() => setMobileOpen(false)}
                                    className={`block px-4 py-3 text-lg font-medium rounded-xl transition-colors ${isActive(link.href) ? 'text-nutri-mint bg-nutri-mint/10' : 'text-gray-300 hover:text-white hover:bg-white/5'}`}
                                >
                                    {link.label}
                                </Link>
                            ))}
                            <div className="border-t border-white/10 my-2 pt-4 space-y-1">
                                <Link to="/profile" onClick={() => setMobileOpen(false)} className="block px-4 py-3 text-lg font-medium text-gray-300 hover:text-white hover:bg-white/5 rounded-xl transition-colors">
                                    Profile
                                </Link>
                                <button
                                    onClick={() => { setMobileOpen(false); handleLogout(); }}
                                    className="block w-full text-left px-4 py-3 text-lg font-medium text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-xl transition-colors"
                                >
                                    Logout
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </nav>

            {/* Main Content */}
            <main className="pt-20 min-h-screen">
                <Outlet />
            </main>

            {/* Click-outside overlay for dropdowns */}
            {profileOpen && (
                <div
                    className="fixed inset-0 z-40"
                    onClick={() => setProfileOpen(false)}
                />
            )}

            {/* Footer */}
            <Footer />
        </div>
    );
};

export default Layout;
