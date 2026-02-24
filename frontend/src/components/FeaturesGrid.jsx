import React from 'react';
import { motion } from 'framer-motion';
import { Scan, Eye, Info, Check } from 'lucide-react';

const FeaturesGrid = () => {
    const features = [
        {
            icon: Scan,
            title: "Fast Label Scanning",
            description: "Get results in milliseconds with our optimized OCR technology."
        },
        {
            icon: Eye,
            title: "Detect Harmful Ingredients",
            description: "Instantly spot additives and preservatives you want to avoid."
        },
        {
            icon: Info,
            title: "Nutrition Transparency",
            description: "Understand the nutritional value beyond just the calorie count."
        },
        {
            icon: Check,
            title: "Informed Food Decisions",
            description: "Empower your grocery shopping with data-backed insights."
        }
    ];

    return (
        <section className="py-24 bg-black border-t border-white/5 relative overflow-hidden">
            {/* Background Glow */}
            <div className="absolute -left-40 top-20 w-[600px] h-[600px] bg-nutri-mint/5 rounded-full blur-[100px] pointer-events-none"></div>

            <div className="max-w-[1200px] mx-auto px-6 relative z-10">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                    {features.map((feature, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: index * 0.1 }}
                            className="bg-white/5 rounded-2xl p-8 border border-white/10
                         hover:bg-white/10 hover:border-white/20 hover:-translate-y-1
                         transition-all duration-300 group backdrop-blur-sm"
                        >
                            <div className="w-14 h-14 bg-nutri-mint/10 rounded-xl flex items-center justify-center mb-6 text-nutri-mint group-hover:bg-nutri-mint group-hover:text-black transition-colors duration-300">
                                <feature.icon className="w-7 h-7" />
                            </div>
                            <h3 className="text-lg font-bold text-white mb-3">
                                {feature.title}
                            </h3>
                            <p className="text-gray-400 text-sm leading-relaxed font-light">
                                {feature.description}
                            </p>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
};

export default FeaturesGrid;
