import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Target, Zap, Clock, CheckCircle, ArrowRight } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const pageVariants = {
    initial: { opacity: 0, y: 16 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -16 },
};

const scanModes = [
    {
        id: 'precision',
        href: '/scan/precision',
        icon: Target,
        title: 'Precision Scan',
        subtitle: 'Deep Analysis',
        description: 'Upload separate Nutrition Facts and Ingredients images for the most thorough, detailed verification.',
        images: 2,
        badge: 'Recommended',
        badgeColor: 'bg-nutri-mint/15 text-nutri-mint border-nutri-mint/30',
        gradient: 'from-nutri-mint/20 to-teal-500/10',
        border: 'border-nutri-mint/30',
        iconBg: 'from-nutri-mint to-teal-400',
        features: ['Nutrition label OCR', 'Ingredient list analysis', 'Full claim verification'],
    },
    {
        id: 'quick',
        href: '/scan/quick',
        icon: Zap,
        title: 'Quick Scan',
        subtitle: 'Fast Check',
        description: 'Upload a single combined label image for a rapid claim check — ideal when you are short on time.',
        images: 1,
        badge: 'Fast',
        badgeColor: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
        gradient: 'from-amber-500/10 to-orange-500/5',
        border: 'border-amber-500/20',
        iconBg: 'from-amber-400 to-orange-500',
        features: ['Single combined label', 'Basic claim check', 'Instant results'],
    },
];

const Dashboard = () => {
    const navigate = useNavigate();
    const { user } = useAuth();

    const firstName = user?.name?.split(' ')[0] || 'there';

    return (
        <motion.div
            variants={pageVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={{ duration: 0.4 }}
            className="min-h-screen py-12 px-6 relative overflow-hidden"
        >
            {/* Background glows */}
            <div className="absolute top-20 left-1/4 w-[500px] h-[500px] bg-nutri-mint/8 rounded-full blur-[120px] pointer-events-none" />
            <div className="absolute bottom-20 right-1/4 w-[400px] h-[400px] bg-teal-500/8 rounded-full blur-[100px] pointer-events-none" />

            <div className="max-w-4xl mx-auto relative z-10">
                {/* Greeting */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                    className="mb-12 text-center"
                >
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-nutri-mint/10 border border-nutri-mint/30 mb-5">
                        <span className="w-2 h-2 rounded-full bg-nutri-mint animate-pulse" />
                        <span className="text-sm font-medium text-nutri-mint">Ready to scan</span>
                    </div>
                    <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
                        Hello, {firstName}!
                    </h1>
                    <p className="text-gray-400 text-lg max-w-xl mx-auto">
                        Choose your scan mode to start verifying product claims.
                    </p>
                </motion.div>

                {/* Mode cards */}
                <div className="grid md:grid-cols-2 gap-6 mb-12">
                    {scanModes.map((mode, idx) => (
                        <motion.button
                            key={mode.id}
                            initial={{ opacity: 0, y: 30 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5, delay: idx * 0.12 }}
                            whileHover={{ y: -6, transition: { duration: 0.2 } }}
                            whileTap={{ scale: 0.98 }}
                            onClick={() => navigate(mode.href)}
                            className={`group relative p-7 rounded-2xl bg-gradient-to-br ${mode.gradient} border ${mode.border} text-left transition-all duration-300 overflow-hidden`}
                        >
                            {/* Badge */}
                            <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border mb-5 ${mode.badgeColor}`}>
                                {mode.badge}
                            </span>

                            {/* Icon + title row */}
                            <div className="flex items-start gap-4 mb-4">
                                <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${mode.iconBg} flex items-center justify-center flex-shrink-0 shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                                    <mode.icon className="w-7 h-7 text-black" />
                                </div>
                                <div>
                                    <p className="text-xs font-medium text-gray-500 mb-0.5">{mode.subtitle}</p>
                                    <h2 className="text-2xl font-bold text-white">{mode.title}</h2>
                                </div>
                            </div>

                            <p className="text-gray-400 text-sm leading-relaxed mb-5">{mode.description}</p>

                            {/* Features */}
                            <ul className="space-y-2 mb-6">
                                {mode.features.map((f) => (
                                    <li key={f} className="flex items-center gap-2 text-sm text-gray-300">
                                        <CheckCircle className="w-4 h-4 text-nutri-mint flex-shrink-0" />
                                        {f}
                                    </li>
                                ))}
                            </ul>

                            {/* Images required pill */}
                            <div className="flex items-center justify-between">
                                <span className="text-xs text-gray-500 bg-white/5 border border-white/10 px-3 py-1.5 rounded-full">
                                    {mode.images} image{mode.images > 1 ? 's' : ''} required
                                </span>
                                <span className="flex items-center gap-1 text-sm font-semibold text-nutri-mint group-hover:gap-2 transition-all">
                                    Start <ArrowRight className="w-4 h-4" />
                                </span>
                            </div>
                        </motion.button>
                    ))}
                </div>

                {/* Quick stats row */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.5 }}
                    className="grid grid-cols-3 gap-4"
                >
                    {[
                        { icon: CheckCircle, label: 'Scans done', value: '3' },
                        { icon: Clock, label: 'This week', value: '2' },
                        { icon: Target, label: 'Avg accuracy', value: '69%' },
                    ].map((stat) => (
                        <div key={stat.label} className="p-4 rounded-xl bg-white/[0.03] border border-white/10 text-center">
                            <stat.icon className="w-5 h-5 text-nutri-mint mx-auto mb-2" />
                            <p className="text-xl font-bold text-white">{stat.value}</p>
                            <p className="text-xs text-gray-500 mt-0.5">{stat.label}</p>
                        </div>
                    ))}
                </motion.div>
            </div>
        </motion.div>
    );
};

export default Dashboard;
