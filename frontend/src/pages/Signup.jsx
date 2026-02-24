import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, User, Eye, EyeOff, ArrowRight, ArrowLeft } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import * as api from '../utils/api';

const pageVariants = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 },
};

const Signup = () => {
    const [form, setForm] = useState({ name: '', email: '', password: '', confirmPassword: '' });
    const [errors, setErrors] = useState({});
    const [serverError, setServerError] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirm, setShowConfirm] = useState(false);
    const [isLoading, setIsLoading] = useState(false);

    const { login } = useAuth();
    const navigate = useNavigate();

    const validate = () => {
        const errs = {};
        if (!form.name.trim()) errs.name = 'Full name is required';
        if (!form.email.trim()) {
            errs.email = 'Email is required';
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
            errs.email = 'Enter a valid email address';
        }
        if (!form.password) {
            errs.password = 'Password is required';
        } else if (form.password.length < 6) {
            errs.password = 'Password must be at least 6 characters';
        }
        if (!form.confirmPassword) {
            errs.confirmPassword = 'Please confirm your password';
        } else if (form.password !== form.confirmPassword) {
            errs.confirmPassword = 'Passwords do not match';
        }
        return errs;
    };

    const handleChange = (e) => {
        setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
        setErrors((prev) => ({ ...prev, [e.target.name]: '' }));
        setServerError('');
    };

    const handleSignup = async (e) => {
        e.preventDefault();
        const errs = validate();
        if (Object.keys(errs).length) { setErrors(errs); return; }

        setIsLoading(true);
        try {
            const tokenData = await api.signup({ name: form.name, email: form.email, password: form.password });
            localStorage.setItem('nutrilens_token', tokenData.access_token);
            const userData = await api.getMe();
            login(userData, tokenData.access_token);
            navigate('/welcome');
        } catch (err) {
            setServerError(err.message || 'Failed to create account. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    const fields = [
        {
            name: 'name', label: 'Full Name', type: 'text',
            placeholder: 'John Doe', icon: User,
        },
        {
            name: 'email', label: 'Email', type: 'email',
            placeholder: 'you@example.com', icon: Mail,
        },
        {
            name: 'password', label: 'Password', type: showPassword ? 'text' : 'password',
            placeholder: '••••••••', icon: Lock,
            toggle: () => setShowPassword(!showPassword), showToggle: showPassword,
        },
        {
            name: 'confirmPassword', label: 'Confirm Password', type: showConfirm ? 'text' : 'password',
            placeholder: '••••••••', icon: Lock,
            toggle: () => setShowConfirm(!showConfirm), showToggle: showConfirm,
        },
    ];

    return (
        <motion.div
            variants={pageVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={{ duration: 0.4 }}
            className="min-h-[80vh] flex items-center justify-center px-6 py-24 relative overflow-hidden"
        >
            <div className="absolute -right-40 top-20 w-[600px] h-[600px] bg-purple-500/10 rounded-full blur-[100px] pointer-events-none" />

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
                        <h2 className="text-2xl font-semibold text-white mb-2">Create an account</h2>
                        <p className="text-gray-400">Join NutriLens and start eating smarter</p>
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

                    <form onSubmit={handleSignup} className="space-y-5" noValidate>
                        {fields.map((field) => (
                            <div key={field.name}>
                                <label className="block text-sm font-medium text-gray-400 mb-2">{field.label}</label>
                                <div className="relative">
                                    <field.icon className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                                    <input
                                        type={field.type}
                                        name={field.name}
                                        value={form[field.name]}
                                        onChange={handleChange}
                                        placeholder={field.placeholder}
                                        className={`w-full bg-black/20 border rounded-xl py-3 pl-12 ${field.toggle ? 'pr-12' : 'pr-4'} text-white placeholder-gray-600 focus:outline-none focus:ring-1 transition-all ${errors[field.name] ? 'border-nutri-red/60 focus:border-nutri-red focus:ring-nutri-red/30' : 'border-white/10 focus:border-nutri-mint/50 focus:ring-nutri-mint/30'}`}
                                    />
                                    {field.toggle && (
                                        <button
                                            type="button"
                                            onClick={field.toggle}
                                            className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white transition-colors"
                                        >
                                            {field.showToggle ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                                        </button>
                                    )}
                                </div>
                                {errors[field.name] && (
                                    <p className="mt-1.5 text-xs text-nutri-red">{errors[field.name]}</p>
                                )}
                            </div>
                        ))}

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
                                    Creating account...
                                </span>
                            ) : (
                                <>Create Account <ArrowRight className="w-5 h-5" /></>
                            )}
                        </motion.button>
                    </form>

                    <div className="mt-8 pt-8 border-t border-white/10 text-center">
                        <p className="text-gray-400">
                            Already have an account?{' '}
                            <Link to="/login" className="text-nutri-mint font-medium hover:text-nutri-mint-light transition-colors">
                                Log in
                            </Link>
                        </p>
                    </div>
                </div>
            </div>
        </motion.div>
    );
};

export default Signup;
