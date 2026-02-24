import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, User, Mail, Save, CheckCircle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import * as api from '../utils/api';

const pageVariants = {
    initial: { opacity: 0, y: 16 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -16 },
};

const EditProfile = () => {
    const navigate = useNavigate();
    const { user, updateUser } = useAuth();

    const [form, setForm] = useState({ name: user?.name || '', email: user?.email || '' });
    const [errors, setErrors] = useState({});
    const [serverError, setServerError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [saved, setSaved] = useState(false);

    const validate = () => {
        const errs = {};
        if (!form.name.trim()) errs.name = 'Name is required';
        if (!form.email.trim()) {
            errs.email = 'Email is required';
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
            errs.email = 'Enter a valid email address';
        }
        return errs;
    };

    const handleChange = (e) => {
        setForm((p) => ({ ...p, [e.target.name]: e.target.value }));
        setErrors((p) => ({ ...p, [e.target.name]: '' }));
        setServerError('');
    };

    const handleSave = async (e) => {
        e.preventDefault();
        const errs = validate();
        if (Object.keys(errs).length) { setErrors(errs); return; }

        setIsLoading(true);
        try {
            const updated = await api.updateMe({ name: form.name, email: form.email });
            updateUser({ name: updated.name, email: updated.email });
            setSaved(true);
            setTimeout(() => navigate('/profile'), 1200);
        } catch (err) {
            setServerError(err.message || 'Failed to update profile. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    const fields = [
        { name: 'name', label: 'Full Name', type: 'text', placeholder: 'Your name', icon: User },
        { name: 'email', label: 'Email Address', type: 'email', placeholder: 'you@example.com', icon: Mail },
    ];

    return (
        <motion.div
            variants={pageVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={{ duration: 0.4 }}
            className="min-h-screen py-10 px-6 relative overflow-hidden"
        >
            <div className="absolute top-20 right-1/4 w-[400px] h-[400px] bg-nutri-mint/6 rounded-full blur-[100px] pointer-events-none" />

            <div className="max-w-xl mx-auto relative z-10">
                {/* Back */}
                <motion.button
                    initial={{ opacity: 0, x: -16 }}
                    animate={{ opacity: 1, x: 0 }}
                    onClick={() => navigate('/profile')}
                    className="flex items-center gap-2 text-gray-400 hover:text-white mb-8 transition-colors"
                >
                    <ArrowLeft className="w-4 h-4" /> Back to Profile
                </motion.button>

                <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
                    <h1 className="text-3xl font-bold text-white mb-2">Edit Profile</h1>
                    <p className="text-gray-400">Update your name or email address.</p>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="bg-white/[0.03] border border-white/10 rounded-2xl p-7"
                >
                    {saved ? (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="flex flex-col items-center py-8 gap-4"
                        >
                            <div className="w-16 h-16 rounded-full bg-nutri-mint/20 flex items-center justify-center">
                                <CheckCircle className="w-8 h-8 text-nutri-mint" />
                            </div>
                            <p className="text-white font-semibold text-lg">Profile updated!</p>
                            <p className="text-gray-400 text-sm">Redirecting...</p>
                        </motion.div>
                    ) : (
                        <form onSubmit={handleSave} className="space-y-5" noValidate>
                            {serverError && (
                                <motion.div
                                    initial={{ opacity: 0, y: -8 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="px-4 py-3 rounded-xl bg-nutri-red/10 border border-nutri-red/30 text-nutri-red text-sm text-center"
                                >
                                    {serverError}
                                </motion.div>
                            )}
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
                                            className={`w-full bg-black/20 border rounded-xl py-3 pl-12 pr-4 text-white placeholder-gray-600 focus:outline-none focus:ring-1 transition-all ${errors[field.name] ? 'border-nutri-red/60 focus:border-nutri-red focus:ring-nutri-red/30' : 'border-white/10 focus:border-nutri-mint/50 focus:ring-nutri-mint/30'}`}
                                        />
                                    </div>
                                    {errors[field.name] && (
                                        <p className="mt-1.5 text-xs text-nutri-red">{errors[field.name]}</p>
                                    )}
                                </div>
                            ))}

                            <div className="flex gap-3 pt-2">
                                <motion.button
                                    type="button"
                                    whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
                                    onClick={() => navigate('/profile')}
                                    className="flex-1 py-3 rounded-xl bg-white/5 border border-white/10 text-gray-300 hover:text-white hover:bg-white/10 transition-colors font-medium"
                                >
                                    Cancel
                                </motion.button>
                                <motion.button
                                    type="submit"
                                    whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
                                    disabled={isLoading}
                                    className="flex-1 py-3 rounded-xl bg-nutri-mint text-black font-bold hover:bg-nutri-mint-light transition-all flex items-center justify-center gap-2 disabled:opacity-70"
                                >
                                    {isLoading ? (
                                        <span className="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin" />
                                    ) : (
                                        <><Save className="w-4 h-4" /> Save Changes</>
                                    )}
                                </motion.button>
                            </div>
                        </form>
                    )}
                </motion.div>
            </div>
        </motion.div>
    );
};

export default EditProfile;
