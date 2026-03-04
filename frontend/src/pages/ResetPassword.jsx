import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { Lock, Eye, EyeOff, CheckCircle2, AlertCircle, ArrowRight } from 'lucide-react';
import api from '../api/client';

const pageVariants = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 },
};

const ResetPassword = () => {
    const [searchParams] = useSearchParams();
    const token = searchParams.get('token');
    const navigate = useNavigate();

    const [form, setForm] = useState({ password: '', confirmPassword: '' });
    const [errors, setErrors] = useState({});
    const [serverError, setServerError] = useState('');
    const [isSuccess, setIsSuccess] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        if (!token) {
            setServerError('Invalid or missing reset token.');
        }
    }, [token]);

    const handleChange = (e) => {
        setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
        setErrors((prev) => ({ ...prev, [e.target.name]: '' }));
        setServerError('');
    };

    const validate = () => {
        const errs = {};
        if (form.password.length < 6) errs.password = 'Password must be at least 6 characters';
        if (form.password !== form.confirmPassword) errs.confirmPassword = 'Passwords do not match';
        return errs;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const errs = validate();
        if (Object.keys(errs).length) { setErrors(errs); return; }

        setIsLoading(true);
        try {
            await api.post('/auth/reset-password', { token, new_password: form.password });
            setIsSuccess(true);
            setTimeout(() => navigate('/login'), 3000);
        } catch (err) {
            setServerError(err.response?.data?.detail || 'Failed to reset password. The link may be expired.');
        } finally {
            setIsLoading(false);
        }
    };

    if (isSuccess) {
        return (
            <div className="min-h-[80vh] flex items-center justify-center px-6">
                <div className="bg-white/5 border border-white/10 backdrop-blur-xl rounded-3xl p-10 shadow-2xl max-w-md w-full text-center">
                    <div className="inline-flex items-center justify-center w-16 h-16 bg-nutri-mint/10 rounded-full mb-6 text-nutri-mint">
                        <CheckCircle2 className="w-10 h-10" />
                    </div>
                    <h2 className="text-2xl font-bold text-white mb-4">Password Reset!</h2>
                    <p className="text-gray-400 mb-8">
                        Your password has been successfully updated. You will be redirected to the login page shortly.
                    </p>
                    <Link
                        to="/login"
                        className="inline-flex items-center gap-2 text-nutri-mint font-medium hover:text-nutri-mint-light transition-colors"
                    >
                        Go to Login <ArrowRight className="w-4 h-4" />
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <motion.div
            variants={pageVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={{ duration: 0.4 }}
            className="min-h-[80vh] flex items-center justify-center px-6 py-24 relative overflow-hidden"
        >
            <div className="absolute -left-40 top-20 w-[600px] h-[600px] bg-nutri-mint/10 rounded-full blur-[100px] pointer-events-none" />

            <div className="w-full max-w-md relative z-10">
                <div className="bg-white/5 border border-white/10 backdrop-blur-xl rounded-3xl p-8 shadow-2xl">
                    <div className="text-center mb-10">
                        <h2 className="text-2xl font-semibold text-white mb-2">Set new password</h2>
                        <p className="text-gray-400">Please enter and confirm your new password.</p>
                    </div>

                    {serverError && (
                        <div className="mb-6 px-4 py-3 rounded-xl bg-nutri-red/10 border border-nutri-red/30 text-nutri-red text-sm flex items-center gap-3">
                            <AlertCircle className="w-5 h-5 flex-shrink-0" />
                            <span>{serverError}</span>
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-5">
                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-2">New Password</label>
                            <div className="relative">
                                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                                <input
                                    type={showPassword ? 'text' : 'password'}
                                    name="password"
                                    value={form.password}
                                    onChange={handleChange}
                                    placeholder="••••••••"
                                    disabled={!token || isLoading}
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

                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-2">Confirm Password</label>
                            <div className="relative">
                                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                                <input
                                    type="password"
                                    name="confirmPassword"
                                    value={form.confirmPassword}
                                    onChange={handleChange}
                                    placeholder="••••••••"
                                    disabled={!token || isLoading}
                                    className={`w-full bg-black/20 border rounded-xl py-3 pl-12 pr-4 text-white placeholder-gray-600 focus:outline-none focus:ring-1 transition-all ${errors.confirmPassword ? 'border-nutri-red/60 focus:border-nutri-red focus:ring-nutri-red/30' : 'border-white/10 focus:border-nutri-mint/50 focus:ring-nutri-mint/30'}`}
                                />
                            </div>
                            {errors.confirmPassword && <p className="mt-1.5 text-xs text-nutri-red">{errors.confirmPassword}</p>}
                        </div>

                        <motion.button
                            type="submit"
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            disabled={!token || isLoading}
                            className="w-full bg-nutri-mint text-black font-bold py-4 rounded-xl hover:bg-nutri-mint-light transition-all shadow-lg shadow-nutri-mint/20 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isLoading ? (
                                <span className="flex items-center gap-2">
                                    <span className="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin" />
                                    Updating...
                                </span>
                            ) : (
                                'Reset Password'
                            )}
                        </motion.button>
                    </form>
                </div>
            </div>
        </motion.div>
    );
};

export default ResetPassword;
