import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Mail, ArrowLeft, Send, CheckCircle2 } from 'lucide-react';
import api from '../api/client';

const pageVariants = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 },
};

const ForgotPassword = () => {
    const [email, setEmail] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isSent, setIsSent] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!email.trim()) {
            setError('Email is required');
            return;
        }

        setIsLoading(true);
        setError('');
        try {
            await api.post('/auth/forgot-password', { email });
            setIsSent(true);
        } catch (err) {
            setError(err.response?.data?.detail || 'Something went wrong. Please try again.');
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
                <Link to="/login" className="inline-flex items-center text-gray-400 hover:text-white mb-8 transition-colors">
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    Back to Login
                </Link>

                <div className="bg-white/5 border border-white/10 backdrop-blur-xl rounded-3xl p-8 shadow-2xl">
                    <div className="text-center mb-10">
                        <div className="inline-flex items-center justify-center w-16 h-16 bg-nutri-mint/10 rounded-2xl mb-6">
                            <Mail className="w-8 h-8 text-nutri-mint" />
                        </div>
                        <h2 className="text-2xl font-semibold text-white mb-2">Forgot password?</h2>
                        <p className="text-gray-400">No worries, we'll send you reset instructions.</p>
                    </div>

                    {isSent ? (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="text-center py-4"
                        >
                            <div className="inline-flex items-center gap-2 px-4 py-3 rounded-xl bg-nutri-mint/10 border border-nutri-mint/30 text-nutri-mint mb-8">
                                <CheckCircle2 className="w-5 h-5" />
                                <span className="text-sm font-medium">Reset link sent!</span>
                            </div>
                            <p className="text-gray-400 mb-8">
                                We've sent a password reset link to <span className="text-white font-medium">{email}</span>.
                                Please check your inbox.
                            </p>
                            <Link
                                to="/login"
                                className="inline-block w-full bg-white/5 border border-white/10 text-white font-bold py-4 rounded-xl hover:bg-white/10 transition-all text-center"
                            >
                                Back to Login
                            </Link>
                        </motion.div>
                    ) : (
                        <form onSubmit={handleSubmit} className="space-y-6">
                            {error && (
                                <motion.div
                                    initial={{ opacity: 0, y: -8 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="px-4 py-3 rounded-xl bg-nutri-red/10 border border-nutri-red/30 text-nutri-red text-sm text-center"
                                >
                                    {error}
                                </motion.div>
                            )}

                            <div>
                                <label className="block text-sm font-medium text-gray-400 mb-2">Email Address</label>
                                <div className="relative">
                                    <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                                    <input
                                        type="email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        placeholder="you@example.com"
                                        className={`w-full bg-black/20 border rounded-xl py-3 pl-12 pr-4 text-white placeholder-gray-600 focus:outline-none focus:ring-1 transition-all ${error ? 'border-nutri-red/60 focus:border-nutri-red focus:ring-nutri-red/30' : 'border-white/10 focus:border-nutri-mint/50 focus:ring-nutri-mint/30'}`}
                                    />
                                </div>
                            </div>

                            <motion.button
                                type="submit"
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                disabled={isLoading}
                                className="w-full bg-nutri-mint text-black font-bold py-4 rounded-xl hover:bg-nutri-mint-light transition-all shadow-lg shadow-nutri-mint/20 flex items-center justify-center gap-2 disabled:opacity-70"
                            >
                                {isLoading ? (
                                    <span className="flex items-center gap-2">
                                        <span className="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin" />
                                        Sending...
                                    </span>
                                ) : (
                                    <>Send Reset Link <Send className="w-4 h-4" /></>
                                )}
                            </motion.button>
                        </form>
                    )}
                </div>
            </div>
        </motion.div>
    );
};

export default ForgotPassword;
