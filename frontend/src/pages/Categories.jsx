import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Dumbbell, Cookie, Milk, Zap, ChevronRight } from 'lucide-react';

const Categories = () => {
    const navigate = useNavigate();

    const categories = [
        {
            id: 'protein-powder',
            name: 'Protein Powder',
            description: 'Whey, casein, plant-based proteins and more',
            icon: Dumbbell,
            color: 'from-purple-500 to-indigo-600',
            bgColor: 'bg-purple-500/10',
            borderColor: 'border-purple-500/30',
            hoverBorder: 'hover:border-purple-400'
        },
        {
            id: 'protein-bars',
            name: 'Protein Bars',
            description: 'Energy bars, snack bars and meal replacements',
            icon: Cookie,
            color: 'from-orange-500 to-amber-600',
            bgColor: 'bg-orange-500/10',
            borderColor: 'border-orange-500/30',
            hoverBorder: 'hover:border-orange-400'
        },
        {
            id: 'dairy-products',
            name: 'Dairy Products',
            description: 'Milk, yogurt, cheese and dairy alternatives',
            icon: Milk,
            color: 'from-blue-400 to-cyan-500',
            bgColor: 'bg-blue-500/10',
            borderColor: 'border-blue-500/30',
            hoverBorder: 'hover:border-blue-400'
        },
        {
            id: 'energy-drinks',
            name: 'Energy Drinks',
            description: 'Sports drinks, pre-workouts and caffeinated beverages',
            icon: Zap,
            color: 'from-green-400 to-emerald-500',
            bgColor: 'bg-green-500/10',
            borderColor: 'border-green-500/30',
            hoverBorder: 'hover:border-green-400'
        }
    ];

    const handleCategorySelect = (categoryId) => {
        navigate(`/dashboard/scan/${categoryId}`);
    };

    return (
        <div className="min-h-screen py-12 px-6 relative overflow-hidden">
            {/* Background Effects */}
            <div className="absolute top-20 left-1/4 w-[500px] h-[500px] bg-nutri-mint/10 rounded-full blur-[120px] pointer-events-none" />
            <div className="absolute bottom-20 right-1/4 w-[400px] h-[400px] bg-teal-500/10 rounded-full blur-[100px] pointer-events-none" />

            <div className="max-w-4xl mx-auto relative z-10">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                    className="text-center mb-12"
                >
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-nutri-mint/10 border border-nutri-mint/30 mb-6">
                        <span className="w-2 h-2 rounded-full bg-nutri-mint animate-pulse" />
                        <span className="text-sm font-medium text-nutri-mint">Select Category</span>
                    </div>
                    <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
                        What would you like to{' '}
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-nutri-mint to-teal-300">
                            analyze?
                        </span>
                    </h1>
                    <p className="text-gray-400 text-lg max-w-xl mx-auto">
                        Choose a product category to scan and analyze ingredients
                    </p>
                </motion.div>

                {/* Category Cards Grid */}
                <div className="grid md:grid-cols-2 gap-6">
                    {categories.map((category, index) => (
                        <motion.button
                            key={category.id}
                            initial={{ opacity: 0, y: 30 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5, delay: index * 0.1 }}
                            whileHover={{ y: -5, transition: { duration: 0.2 } }}
                            whileTap={{ scale: 0.98 }}
                            onClick={() => handleCategorySelect(category.id)}
                            className={`group relative p-6 rounded-2xl ${category.bgColor} border ${category.borderColor} ${category.hoverBorder} text-left transition-all duration-300 overflow-hidden`}
                        >
                            {/* Gradient Overlay on Hover */}
                            <div className={`absolute inset-0 bg-gradient-to-br ${category.color} opacity-0 group-hover:opacity-10 transition-opacity duration-300`} />

                            <div className="relative z-10 flex items-start gap-4">
                                {/* Icon */}
                                <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${category.color} flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform duration-300`}>
                                    <category.icon className="w-7 h-7 text-white" />
                                </div>

                                {/* Content */}
                                <div className="flex-1">
                                    <h3 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
                                        {category.name}
                                        <ChevronRight className="w-5 h-5 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-300 text-nutri-mint" />
                                    </h3>
                                    <p className="text-gray-400 text-sm leading-relaxed">
                                        {category.description}
                                    </p>
                                </div>
                            </div>

                            {/* Shimmer Effect */}
                            <motion.div
                                className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent opacity-0 group-hover:opacity-100"
                                initial={{ x: "-100%" }}
                                whileHover={{ x: "100%" }}
                                transition={{ duration: 0.6 }}
                            />
                        </motion.button>
                    ))}
                </div>

                {/* Bottom Info */}
                <motion.p
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.8 }}
                    className="text-center text-gray-500 text-sm mt-10"
                >
                    More categories coming soon...
                </motion.p>
            </div>
        </div>
    );
};

export default Categories;
