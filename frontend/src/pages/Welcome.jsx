import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Sparkles, ArrowRight } from 'lucide-react';

const Welcome = () => {
    const navigate = useNavigate();
    const [step, setStep] = useState(0);

    const steps = [
        {
            title: "Welcome to",
            highlight: "NutriLens",
            description: "Your smart companion for understanding food labels"
        },
        {
            title: "Scan &",
            highlight: "Analyze",
            description: "Upload food label images and get instant nutritional insights"
        },
        {
            title: "Make",
            highlight: "Informed Choices",
            description: "Verify health claims against FSSAI standards"
        }
    ];

    const handleContinue = () => {
        if (step < steps.length - 1) {
            setStep(step + 1);
        } else {
            navigate('/login');
        }
    };

    useEffect(() => {
        const timer = setTimeout(() => {
            if (step < steps.length - 1) {
                setStep(s => s + 1);
            }
        }, 4000);
        return () => clearTimeout(timer);
    }, [step]);

    return (
        <div className="min-h-screen bg-black flex items-center justify-center relative overflow-hidden">
            {/* Background Effects */}
            <div className="absolute inset-0">
                <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-nutri-mint/10 rounded-full blur-3xl animate-pulse" />
                <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-teal-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-nutri-mint/5 rounded-full blur-3xl" />
            </div>

            {/* Content */}
            <div className="relative z-10 max-w-2xl mx-auto px-6 text-center">
                <AnimatePresence mode="wait">
                    <motion.div
                        key={step}
                        initial={{ opacity: 0, y: 40 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -40 }}
                        transition={{ duration: 0.6 }}
                        className="flex flex-col items-center"
                    >
                        {/* Icon */}
                        <motion.div
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
                            className="w-20 h-20 rounded-2xl bg-gradient-to-br from-nutri-mint/20 to-teal-500/10 flex items-center justify-center mb-8 border border-nutri-mint/20"
                        >
                            <Sparkles className="w-10 h-10 text-nutri-mint" />
                        </motion.div>

                        {/* Title */}
                        <h1 className="text-5xl md:text-7xl font-bold tracking-tighter mb-6 leading-[1.1] text-white">
                            {steps[step].title}{' '}
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-nutri-mint-light to-teal-200">
                                {steps[step].highlight}
                            </span>
                        </h1>

                        {/* Description */}
                        <p className="text-lg md:text-xl text-gray-400 max-w-lg leading-relaxed mb-12">
                            {steps[step].description}
                        </p>

                        {/* Progress Dots */}
                        <div className="flex items-center gap-3 mb-10">
                            {steps.map((_, i) => (
                                <motion.div
                                    key={i}
                                    className={`h-2 rounded-full transition-all duration-300 ${i === step ? 'w-8 bg-nutri-mint' : i < step ? 'w-2 bg-nutri-mint/50' : 'w-2 bg-white/20'}`}
                                />
                            ))}
                        </div>

                        {/* Continue Button */}
                        <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={handleContinue}
                            className="bg-white text-gray-900 text-lg font-bold px-8 py-4 rounded-xl hover:bg-gray-100 transition-all duration-300 flex items-center gap-2 shadow-[0_0_20px_rgba(255,255,255,0.3)]"
                        >
                            {step < steps.length - 1 ? 'Next' : 'Get Started'}
                            <ArrowRight className="w-5 h-5" />
                        </motion.button>
                    </motion.div>
                </AnimatePresence>
            </div>

            {/* Skip Button */}
            <motion.button
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1 }}
                onClick={() => navigate('/login')}
                className="absolute bottom-8 right-8 text-sm text-gray-500 hover:text-white transition-colors"
            >
                Skip →
            </motion.button>
        </div>
    );
};

export default Welcome;
