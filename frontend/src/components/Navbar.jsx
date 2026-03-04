import React, { useState, useEffect } from 'react';
import { Menu, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link } from 'react-router-dom';

const Navbar = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [scrolled, setScrolled] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            setScrolled(window.scrollY > 20);
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const navLinks = [
        { name: "Home", href: "/", isRoute: true },
        { name: "Features", href: "/#features", isRoute: true },
        { name: "About", href: "/about", isRoute: true },
    ];

    return (
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

                    {/* Desktop Menu */}
                    <div className="hidden md:flex items-center space-x-10">
                        {navLinks.map((link) => (
                            link.isRoute ? (
                                <Link
                                    key={link.name}
                                    to={link.href}
                                    className="relative text-sm font-medium text-gray-300 overflow-hidden group"
                                >
                                    <span className="block transition-transform duration-300 group-hover:-translate-y-full">
                                        {link.name}
                                    </span>
                                    <span className="absolute inset-0 block translate-y-full transition-transform duration-300 group-hover:translate-y-0 text-white">
                                        {link.name}
                                    </span>
                                </Link>
                            ) : (
                                <a
                                    key={link.name}
                                    href={link.href}
                                    className="relative text-sm font-medium text-gray-300 overflow-hidden group"
                                >
                                    <span className="block transition-transform duration-300 group-hover:-translate-y-full">
                                        {link.name}
                                    </span>
                                    <span className="absolute inset-0 block translate-y-full transition-transform duration-300 group-hover:translate-y-0 text-white">
                                        {link.name}
                                    </span>
                                </a>
                            )
                        ))}
                    </div>

                    {/* Desktop Buttons */}
                    <div className="hidden md:flex items-center space-x-4">
                        <Link to="/login">
                            <motion.button
                                whileHover="hover"
                                initial="initial"
                                className="text-sm font-medium text-gray-300 px-4 py-2 relative overflow-hidden"
                            >
                                <motion.span
                                    variants={{
                                        initial: { y: 0 },
                                        hover: { y: -25 }
                                    }}
                                    transition={{ duration: 0.3, ease: 'easeInOut' }}
                                    className="block"
                                >
                                    Login
                                </motion.span>
                                <motion.span
                                    variants={{
                                        initial: { y: 25 },
                                        hover: { y: 0 }
                                    }}
                                    transition={{ duration: 0.3, ease: 'easeInOut' }}
                                    className="absolute inset-0 flex items-center justify-center text-white"
                                >
                                    Login
                                </motion.span>
                            </motion.button>
                        </Link>

                        <Link to="/signup">
                            <motion.button
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                transition={{ type: "spring", stiffness: 400, damping: 17 }}
                                className="bg-white text-gray-900 text-sm font-bold px-5 py-2.5 rounded-full shadow-[0_0_15px_rgba(255,255,255,0.15)] hover:bg-gray-100 hover:shadow-[0_0_20px_rgba(255,255,255,0.3)]"
                            >
                                Sign up
                            </motion.button>
                        </Link>
                    </div>

                    {/* Mobile menu button */}
                    <div className="md:hidden flex items-center">
                        <button
                            onClick={() => setIsOpen(!isOpen)}
                            className="text-white hover:text-gray-300 focus:outline-none p-2"
                        >
                            {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
                        </button>
                    </div>
                </div>
            </div>

            {/* Mobile Menu */}
            {isOpen && (
                <div className="md:hidden bg-black/95 backdrop-blur-xl border-b border-white/10 absolute top-full left-0 w-full shadow-2xl">
                    <div className="px-6 pt-4 pb-8 space-y-4">
                        <Link to="/" onClick={() => setIsOpen(false)} className="block px-4 py-3 text-lg font-medium text-gray-300 hover:text-white hover:bg-white/5 rounded-xl transition-colors">Home</Link>
                        <Link to="/#features" onClick={() => setIsOpen(false)} className="block px-4 py-3 text-lg font-medium text-gray-300 hover:text-white hover:bg-white/5 rounded-xl transition-colors">Features</Link>
                        <Link to="/about" onClick={() => setIsOpen(false)} className="block px-4 py-3 text-lg font-medium text-gray-300 hover:text-white hover:bg-white/5 rounded-xl transition-colors">About</Link>
                        <div className="border-t border-white/10 my-2 pt-6 space-y-4">
                            <Link to="/login" className="block w-full text-center px-4 py-3 text-lg font-medium text-gray-300 hover:text-white rounded-xl transition-colors">
                                Login
                            </Link>
                            <Link to="/signup" className="block w-full text-center bg-white text-gray-900 px-4 py-3 text-lg font-bold rounded-xl shadow-lg active:scale-95 transition-all">
                                Sign up
                            </Link>
                        </div>
                    </div>
                </div>
            )}
        </nav>
    );
};

export default Navbar;
