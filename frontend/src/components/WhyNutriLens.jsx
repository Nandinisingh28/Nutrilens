import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, ScanText, ShieldCheck, ClipboardCheck } from 'lucide-react';

// eslint-disable-next-line react/prop-types
const FeatureItem = ({ icon: Icon, title, description }) => (
    <motion.div
        variants={{
            hidden: { opacity: 0, y: 20 },
            visible: { opacity: 1, y: 0 }
        }}
        className="p-8 rounded-2xl bg-white/5 border border-white/10
                  hover:bg-white/10 hover:border-white/20
                  transition-all duration-300 group h-full backdrop-blur-sm"
    >
        <div className="w-12 h-12 bg-nutri-mint/20 rounded-xl flex items-center justify-center mb-6
                    group-hover:scale-110 transition-transform duration-300">
            <Icon className="w-6 h-6 text-nutri-mint" />
        </div>
        <h3 className="text-xl font-bold text-white mb-3 tracking-tight">
            {title}
        </h3>
        <p className="text-gray-400 leading-relaxed font-light">
            {description}
        </p>
    </motion.div>
);

const WhyNutriLens = () => {
    const features = [
        {
            icon: CheckCircle,
            title: "Enhances Consumer Transparency",
            description:
                "Provides unbiased, explainable verification of front-of-pack claims (e.g., 'high protein', 'low sugar') against actual ingredients and FSSAI-aligned nutritional thresholds."
        },
        {
            icon: ScanText,
            title: "OCR-Powered Label Extraction",
            description:
                "Digitizes ingredient lists, nutrition facts, and marketing claims from uploaded packaging images using Optical Character Recognition."
        },
        {
            icon: ShieldCheck,
            title: "Rule-Based Claim Validation",
            description:
                "Analyzes parsed ingredients for hidden sugars, additives, preservatives, and consistency with health claims using predefined regulatory rules."
        },
        {
            icon: ClipboardCheck,
            title: "Clear & Explainable Results",
            description:
                "Delivers verdict status (Valid / Misleading / False) per claim with justified explanations to support informed dietary decisions."
        }
    ];

    return (
        <section
            id="features"
            className="relative py-32 bg-black"
        >
            {/* Subtle Gradient Background */}
            <div className="absolute inset-0 bg-gradient-to-b from-black via-gray-900 to-black pointer-events-none"></div>

            {/* Content */}
            <div className="relative max-w-[1200px] mx-auto px-6 z-10">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    className="text-center mb-20"
                >
                    <h2 className="text-sm font-bold text-nutri-mint tracking-widest uppercase mb-3">
                        Features
                    </h2>
                    <p className="text-4xl md:text-5xl font-bold tracking-tight text-white mb-6">
                        Why NutriLens?
                    </p>
                    <p className="text-xl text-gray-400 max-w-2xl mx-auto font-light">
                        Everything you need to make informed decisions about your nutrition, powered by advanced AI.
                    </p>
                </motion.div>

                <motion.div
                    initial="hidden"
                    whileInView="visible"
                    viewport={{ once: true }}
                    variants={{
                        hidden: {},
                        visible: {
                            transition: {
                                staggerChildren: 0.1
                            }
                        }
                    }}
                    className="grid grid-cols-1 md:grid-cols-2 gap-8"
                >
                    {features.map((feature, index) => (
                        <FeatureItem key={index} {...feature} />
                    ))}
                </motion.div>
            </div>
        </section>
    );
};

export default WhyNutriLens;
