import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { User, Mail, Calendar, Edit3, History, Target, LogOut, ShieldCheck } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import * as api from '../utils/api';

const pageVariants = {
    initial: { opacity: 0, y: 16 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -16 },
};

const Profile = () => {
    const navigate = useNavigate();
    const { user, logout } = useAuth();
    const [scanCount, setScanCount] = useState(null);

    useEffect(() => {
        api.getScanHistory()
            .then((scans) => setScanCount(scans.length))
            .catch(() => setScanCount(0));
    }, []);

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    const joinDate = user?.created_at
        ? new Date(user.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
        : 'Member';

    const stats = [
        { label: 'Total Scans', value: scanCount != null ? scanCount.toString() : '…', icon: Target },
        { label: 'Verified True', value: '—', icon: ShieldCheck },
        { label: 'Member Since', value: user?.created_at ? new Date(user.created_at).getFullYear().toString() : '—', icon: History },
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
            <div className="absolute top-20 left-1/4 w-[500px] h-[400px] bg-nutri-mint/6 rounded-full blur-[100px] pointer-events-none" />

            <div className="max-w-2xl mx-auto relative z-10">
                {/* Header */}
                <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
                    <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-nutri-mint/10 border border-nutri-mint/30 mb-4">
                        <User className="w-3.5 h-3.5 text-nutri-mint" />
                        <span className="text-xs font-semibold text-nutri-mint">My Profile</span>
                    </div>
                    <h1 className="text-3xl md:text-4xl font-bold text-white">Account Details</h1>
                </motion.div>

                {/* Profile card */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="bg-white/[0.03] border border-white/10 rounded-2xl p-7 mb-5"
                >
                    <div className="flex items-start gap-5">
                        {/* Avatar */}
                        <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-nutri-mint to-teal-400 flex items-center justify-center flex-shrink-0 shadow-lg shadow-nutri-mint/20">
                            <span className="text-2xl font-bold text-black">
                                {user?.name?.charAt(0).toUpperCase() || 'U'}
                            </span>
                        </div>
                        <div className="flex-1 min-w-0">
                            <h2 className="text-2xl font-bold text-white mb-1 truncate">{user?.name || 'User'}</h2>
                            <div className="flex flex-col gap-1.5 text-sm text-gray-400">
                                <span className="flex items-center gap-2">
                                    <Mail className="w-4 h-4 text-gray-500 flex-shrink-0" />
                                    <span className="truncate">{user?.email || '—'}</span>
                                </span>
                                <span className="flex items-center gap-2">
                                    <Calendar className="w-4 h-4 text-gray-500 flex-shrink-0" />
                                    Joined {joinDate}
                                </span>
                            </div>
                        </div>
                        <motion.button
                            whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                            onClick={() => navigate('/profile/edit')}
                            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-white/5 border border-white/10 text-gray-300 hover:text-white hover:bg-white/10 transition-colors text-sm font-medium flex-shrink-0"
                        >
                            <Edit3 className="w-4 h-4" /> Edit
                        </motion.button>
                    </div>
                </motion.div>

                {/* Stats */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="grid grid-cols-3 gap-4 mb-5"
                >
                    {stats.map((stat) => (
                        <div key={stat.label} className="p-4 rounded-xl bg-white/[0.03] border border-white/10 text-center">
                            <stat.icon className="w-5 h-5 text-nutri-mint mx-auto mb-2" />
                            <p className="text-2xl font-bold text-white">{stat.value}</p>
                            <p className="text-xs text-gray-500 mt-0.5">{stat.label}</p>
                        </div>
                    ))}
                </motion.div>

                {/* Actions */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="bg-white/[0.03] border border-white/10 rounded-2xl overflow-hidden"
                >
                    {[
                        { icon: Edit3, label: 'Edit Profile', sub: 'Update name or email', action: () => navigate('/profile/edit') },
                        { icon: History, label: 'Scan History', sub: 'View all past scans', action: () => navigate('/history') },
                    ].map((item, i) => (
                        <button
                            key={item.label}
                            onClick={item.action}
                            className={`w-full flex items-center gap-4 px-6 py-4 hover:bg-white/5 transition-colors text-left group ${i > 0 ? 'border-t border-white/10' : ''}`}
                        >
                            <div className="w-10 h-10 rounded-xl bg-nutri-mint/10 flex items-center justify-center flex-shrink-0">
                                <item.icon className="w-5 h-5 text-nutri-mint" />
                            </div>
                            <div className="flex-1">
                                <p className="text-white font-medium text-sm">{item.label}</p>
                                <p className="text-gray-500 text-xs mt-0.5">{item.sub}</p>
                            </div>
                        </button>
                    ))}
                    <div className="border-t border-white/10">
                        <button
                            onClick={handleLogout}
                            className="w-full flex items-center gap-4 px-6 py-4 hover:bg-red-500/5 transition-colors text-left"
                        >
                            <div className="w-10 h-10 rounded-xl bg-red-500/10 flex items-center justify-center flex-shrink-0">
                                <LogOut className="w-5 h-5 text-red-400" />
                            </div>
                            <div>
                                <p className="text-red-400 font-medium text-sm">Sign Out</p>
                                <p className="text-gray-500 text-xs mt-0.5">Log out of your account</p>
                            </div>
                        </button>
                    </div>
                </motion.div>
            </div>
        </motion.div>
    );
};

export default Profile;
