import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Target, Zap, Shield, History, ChevronRight, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';

function Dashboard() {
    const { user } = useAuth();
    const navigate = useNavigate();

    return (
        <div className="max-w-[1200px] mx-auto px-6 pb-20 animate-fadeIn">
            {/* Hero Section */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-gray-900 via-black to-gray-900 border border-white/10 mb-16 p-8 md:p-12 shadow-2xl"
            >
                {/* Background decorative elements */}
                <div className="absolute top-0 right-0 -mt-20 -mr-20 w-80 h-80 bg-nutri-mint/10 rounded-full blur-3xl"></div>

                <div className="relative z-10 max-w-2xl">
                    <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-nutri-mint-light text-xs font-medium uppercase tracking-wider mb-6">
                        <span className="w-1.5 h-1.5 rounded-full bg-nutri-mint animate-pulse"></span>
                        Overview
                    </div>

                    <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-white mb-4">
                        Hey, <span className="text-transparent bg-clip-text bg-gradient-to-r from-nutri-mint to-teal-400">{user?.name?.split(' ')[0] || 'there'}!</span> 👋
                    </h1>

                    <p className="text-lg text-gray-400 mb-8 leading-relaxed">
                        Ready to verify food claims? Upload a product label and we'll analyze
                        whether those "High Protein" or "Low Sugar" claims are actually true.
                    </p>

                    <div className="flex flex-col sm:flex-row gap-4">
                        <button
                            className="bg-nutri-mint text-black px-6 py-3 rounded-xl font-bold hover:bg-teal-400 transition-colors flex items-center justify-center gap-2 group"
                            onClick={() => navigate('/scan/precision')}
                        >
                            <Target className="w-5 h-5 group-hover:scale-110 transition-transform" />
                            Precision Scan
                        </button>
                        <button
                            className="bg-white/10 text-white border border-white/20 px-6 py-3 rounded-xl font-bold hover:bg-white/20 transition-colors flex items-center justify-center gap-2 group"
                            onClick={() => navigate('/scan/quick')}
                        >
                            <Zap className="w-5 h-5 group-hover:scale-110 transition-transform text-yellow-400" />
                            Quick Scan
                        </button>
                    </div>
                </div>
            </motion.div>

            {/* Scan Mode Selection */}
            <div className="mb-16">
                <div className="text-center mb-10">
                    <h2 className="text-3xl font-bold text-white mb-3">Choose Your Scan Mode</h2>
                    <p className="text-gray-400 max-w-2xl mx-auto">Select the scanning method that best fits your current needs.</p>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                    <motion.div
                        whileHover={{ y: -5 }}
                        className="bg-white/5 backdrop-blur-sm border border-white/10 p-8 rounded-3xl hover:bg-white/10 transition-all cursor-pointer group"
                        onClick={() => navigate('/scan/precision')}
                    >
                        <div className="w-16 h-16 bg-nutri-mint/20 rounded-2xl flex items-center justify-center mb-6 text-nutri-mint group-hover:scale-110 group-hover:bg-nutri-mint/30 transition-all">
                            <Target className="w-8 h-8" />
                        </div>
                        <h3 className="text-2xl font-bold text-white mb-3">Precision Scan</h3>
                        <p className="text-gray-400 mb-6 leading-relaxed">
                            Upload separate photos of the nutrition facts and ingredients list for the highest accuracy analysis. Best for complex labels.
                        </p>
                        <button className="text-nutri-mint font-medium flex items-center gap-1 group-hover:gap-2 transition-all">
                            Start Precision Scan <ChevronRight className="w-4 h-4" />
                        </button>
                    </motion.div>

                    <motion.div
                        whileHover={{ y: -5 }}
                        className="bg-white/5 backdrop-blur-sm border border-white/10 p-8 rounded-3xl hover:bg-white/10 transition-all cursor-pointer group"
                        onClick={() => navigate('/scan/quick')}
                    >
                        <div className="w-16 h-16 bg-yellow-500/20 rounded-2xl flex items-center justify-center mb-6 text-yellow-500 group-hover:scale-110 group-hover:bg-yellow-500/30 transition-all">
                            <Zap className="w-8 h-8" />
                        </div>
                        <h3 className="text-2xl font-bold text-white mb-3">Quick Scan</h3>
                        <p className="text-gray-400 mb-6 leading-relaxed">
                            Upload a single image containing both sections. Faster processing but may be less accurate for very dense or blurry labels.
                        </p>
                        <button className="text-yellow-500 font-medium flex items-center gap-1 group-hover:gap-2 transition-all">
                            Start Quick Scan <ChevronRight className="w-4 h-4" />
                        </button>
                    </motion.div>
                </div>
            </div>

            {/* Features */}
            <div className="mb-20">
                <div className="text-center mb-10">
                    <h2 className="text-3xl font-bold text-white mb-3">How NutriLens Works</h2>
                </div>

                <div className="grid md:grid-cols-3 gap-6">
                    {[
                        { icon: Sparkles, title: "AI-Powered OCR", desc: "Our advanced OCR extracts nutrition facts and ingredients from your photos with high accuracy.", color: "text-purple-400", bg: "bg-purple-500/10" },
                        { icon: Shield, title: "FSSAI Standards", desc: "We verify claims against official Indian food safety guidelines for accurate, reliable results.", color: "text-nutri-mint", bg: "bg-nutri-mint/10" },
                        { icon: History, title: "Scan History", desc: "All your scans are saved securely so you can review past products anytime you want.", color: "text-blue-400", bg: "bg-blue-500/10" }
                    ].map((feature, idx) => (
                        <div key={idx} className="bg-white/5 border border-white/10 p-6 rounded-2xl">
                            <div className={`w-12 h-12 ${feature.bg} ${feature.color} rounded-xl flex items-center justify-center mb-4`}>
                                <feature.icon className="w-6 h-6" />
                            </div>
                            <h3 className="text-lg font-bold text-white mb-2">{feature.title}</h3>
                            <p className="text-gray-400 text-sm leading-relaxed">{feature.desc}</p>
                        </div>
                    ))}
                </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
                {/* Supported Claims */}
                <div className="bg-white/5 border border-white/10 p-8 rounded-3xl">
                    <h3 className="text-xl font-bold text-white mb-6">Supported Claim Types</h3>
                    <div className="flex flex-wrap gap-2 mb-4">
                        {[
                            { label: 'High Protein', icon: '💪' },
                            { label: 'Source of Protein', icon: '🥩' },
                            { label: 'Low Sugar', icon: '🍬' },
                            { label: 'Sugar Free', icon: '🚫' },
                            { label: 'No Added Sugar', icon: '⛔' },
                            { label: 'High Fiber', icon: '🌾' },
                            { label: 'Source of Fiber', icon: '🥦' },
                            { label: 'Low Fat', icon: '🥑' },
                            { label: 'Fat Free', icon: '🫙' },
                            { label: 'Low Saturated Fat', icon: '🧈' },
                            { label: 'Trans Fat Free', icon: '❌' },
                            { label: 'Low Energy', icon: '🔋' },
                            { label: 'Cholesterol Free', icon: '🫀' },
                            { label: 'Low Cholesterol', icon: '💊' },
                            { label: 'Gluten Free', icon: '🌾' },
                            { label: 'Vegan', icon: '🌱' },
                            { label: 'No Preservatives', icon: '🧪' },
                            { label: 'No Artificial Colors', icon: '🎨' },
                            { label: 'No Artificial Flavors', icon: '👅' },
                            { label: 'No Palm Oil', icon: '🌴' },
                            { label: 'Lactose Free', icon: '🥛' },
                            { label: 'Eggless', icon: '🥚' },
                            { label: 'Whole Grain', icon: '🌾' },
                            { label: 'No Added MSG', icon: '🫗' },
                            { label: 'Clean Ingredients', icon: '✨' },
                        ].map((claim) => (
                            <span
                                key={claim.label}
                                className="px-3 py-1.5 bg-white/5 border border-white/10 rounded-full text-xs text-gray-300 flex items-center gap-1.5"
                            >
                                <span>{claim.icon}</span>
                                {claim.label}
                            </span>
                        ))}
                    </div>
                    <p className="text-gray-500 text-xs mt-4">
                        Compound claims like "High Protein and Low Sugar" are also supported.
                    </p>
                </div>

                {/* Supported Categories */}
                <div className="bg-white/5 border border-white/10 p-8 rounded-3xl">
                    <h3 className="text-xl font-bold text-white mb-6">Supported Categories</h3>
                    <div className="grid grid-cols-3 sm:grid-cols-4 gap-3">
                        {[
                            { label: 'Protein Bars', icon: '🥜', color: 'text-amber-500' },
                            { label: 'Breakfast Cereals', icon: '🥣', color: 'text-blue-400' },
                            { label: 'Biscuits & Cookies', icon: '🍪', color: 'text-orange-400' },
                            { label: 'Snacks', icon: '🍿', color: 'text-red-400' },
                            { label: 'Chocolates', icon: '🍫', color: 'text-purple-400' },
                            { label: 'Beverages', icon: '🥤', color: 'text-nutri-mint' },
                            { label: 'Energy Drinks', icon: '⚡', color: 'text-amber-400' },
                            { label: 'Dairy Products', icon: '🥛', color: 'text-blue-300' },
                            { label: 'Noodles & RTE', icon: '🍜', color: 'text-orange-300' },
                            { label: 'Sauces & Spreads', icon: '🫙', color: 'text-red-500' },
                            { label: 'Health Supplements', icon: '💊', color: 'text-purple-300' },
                            { label: 'Frozen Foods', icon: '🧊', color: 'text-teal-400' },
                        ].map((cat) => (
                            <div
                                key={cat.label}
                                className="flex flex-col items-center gap-1.5 p-2 bg-black/20 rounded-xl border border-white/5"
                            >
                                <span className={`text-2xl ${cat.color}`}>{cat.icon}</span>
                                <span className="text-[10px] font-medium text-gray-300 text-center w-full truncate">
                                    {cat.label}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Dashboard;
