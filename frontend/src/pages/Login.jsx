import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Mail, Lock, Eye, EyeOff, ArrowRight, ArrowLeft } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import * as api from '../utils/api';

const pageVariants = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 },
};

const Login = () => {
    const [form, setForm] = useState({ email: '', password: '' });
    const [errors, setErrors] = useState({});
    const [serverError, setServerError] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [isLoading, setIsLoading] = useState(false);

    const { login } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();
    const from = location.state?.from?.pathname || '/dashboard';

    const validate = () => {
        const errs = {};
        if (!form.email.trim()) errs.email = 'Email is required';
        if (!form.password) errs.password = 'Password is required';
        return errs;
    };

    const handleChange = (e) => {
        setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
        setErrors((prev) => ({ ...prev, [e.target.name]: '' }));
        setServerError('');
    };

    const handleLogin = async (e) => {
        e.preventDefault();
        const errs = validate();
        if (Object.keys(errs).length) { setErrors(errs); return; }

        setIsLoading(true);
        try {
            const tokenData = await api.login({ email: form.email, password: form.password });
            // Fetch user profile using the new token
            localStorage.setItem('nutrilens_token', tokenData.access_token);
            const userData = await api.getMe();
            login(userData, tokenData.access_token);
            navigate(from, { replace: true });
        } catch (err) {
            setServerError(err.message || 'Invalid email or password');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <motion.div
            variants={pageVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={{ duration: 0.4 }}
            className="min-h-[80vh] flex items-center justify-center px-6 py-24 relative overflow-hidden"
        >
            {/* Background Glow */}
            <div className="absolute -left-40 top-20 w-[600px] h-[600px] bg-nutri-mint/10 rounded-full blur-[100px] pointer-events-none" />

            <div className="w-full max-w-md relative z-10">
                <Link to="/" className="inline-flex items-center text-gray-400 hover:text-white mb-8 transition-colors">
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    Back to Home
                </Link>

                <div className="bg-white/5 border border-white/10 backdrop-blur-xl rounded-3xl p-8 shadow-2xl">
                    <div className="text-center mb-10">
                        <Link to="/" className="inline-flex items-center gap-2 mb-6 hover:opacity-80 transition-opacity">
                            <img src="/logo.png" alt="NutriLens" className="w-10 h-10" />
                            <span className="text-2xl font-bold text-white">
                                Nutri<span className="text-nutri-mint">Lens</span>
                            </span>
                        </Link>
                        <h2 className="text-2xl font-semibold text-white mb-2">Welcome back</h2>
                        <p className="text-gray-400">Sign in to continue to your dashboard</p>
                    </div>

                    {serverError && (
                        <motion.div
                            initial={{ opacity: 0, y: -8 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="mb-6 px-4 py-3 rounded-xl bg-nutri-red/10 border border-nutri-red/30 text-nutri-red text-sm text-center"
                        >
                            {serverError}
                        </motion.div>
                    )}

                    <form onSubmit={handleLogin} className="space-y-5" noValidate>
                        {/* Email */}
                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-2">Email</label>
                            <div className="relative">
                                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                                <input
                                    type="email"
                                    name="email"
                                    value={form.email}
                                    onChange={handleChange}
                                    placeholder="you@example.com"
                                    className={`w-full bg-black/20 border rounded-xl py-3 pl-12 pr-4 text-white placeholder-gray-600 focus:outline-none focus:ring-1 transition-all ${errors.email ? 'border-nutri-red/60 focus:border-nutri-red focus:ring-nutri-red/30' : 'border-white/10 focus:border-nutri-mint/50 focus:ring-nutri-mint/30'}`}
                                />
                            </div>
                            {errors.email && <p className="mt-1.5 text-xs text-nutri-red">{errors.email}</p>}
                        </div>

                        {/* Password */}
                        <div>
                            <div className="flex justify-between items-center mb-2">
                                <label className="block text-sm font-medium text-gray-400">Password</label>
                                <Link to="/forgot-password" size="sm" className="text-sm text-nutri-mint hover:text-nutri-mint-light transition-colors">
                                    Forgot password?
                                </Link>
                            </div>
                            <div className="relative">
                                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                                <input
                                    type={showPassword ? 'text' : 'password'}
                                    name="password"
                                    value={form.password}
                                    onChange={handleChange}
                                    placeholder="••••••••"
                                    className={`w-full bg-black/20 border rounded-xl py-3 pl-12 pr-12 text-white placeholder-gray-600 focus:outline-none focus:ring-1 transition-all ${errors.password ? 'border-nutri-red/60 focus:border-nutri-red focus:ring-nutri-red/30' : 'border-white/10 focus:border-nutri-mint/50 focus:ring-nutri-mint/30'}`}
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white transition-colors"
                                >
                                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                                </button>
                            </div>
                            {errors.password && <p className="mt-1.5 text-xs text-nutri-red">{errors.password}</p>}
                        </div>

                        <motion.button
                            type="submit"
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            disabled={isLoading}
                            className="w-full bg-nutri-mint text-black font-bold py-4 rounded-xl hover:bg-nutri-mint-light transition-all shadow-lg shadow-nutri-mint/20 flex items-center justify-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed"
                        >
                            {isLoading ? (
                                <span className="flex items-center gap-2">
                                    <span className="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin" />
                                    Signing in...
                                </span>
                            ) : (
                                <>Sign In <ArrowRight className="w-5 h-5" /></>
                            )}
                        </motion.button>
                    </form>

                    <div className="mt-8 pt-8 border-t border-white/10 text-center">
                        <p className="text-gray-400">
                            Don't have an account?{' '}
                            <Link to="/signup" className="text-nutri-mint font-medium hover:text-nutri-mint-light transition-colors">
                                Sign up
                            </Link>
                        </p>
                    </div>
                </div>
            </div>
        </motion.div>
    );
};

export default Login;
