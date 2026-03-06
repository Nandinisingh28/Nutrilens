import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Sparkles, ArrowRight } from 'lucide-react';

const Welcome = () => {
    const navigate = useNavigate();
    const [showContent, setShowContent] = useState(false);
    const [showButton, setShowButton] = useState(false);

    useEffect(() => {
        // Staggered content reveal
        const contentTimer = setTimeout(() => setShowContent(true), 1200);
        const buttonTimer = setTimeout(() => setShowButton(true), 2000);

        return () => {
            clearTimeout(contentTimer);
            clearTimeout(buttonTimer);
        };
    }, []);

    const handleContinue = () => {
        navigate('/dashboard');
    };

    // Floating particles animation
    const particles = Array.from({ length: 20 }, (_, i) => ({
        id: i,
        x: Math.random() * 100,
        y: Math.random() * 100,
        size: Math.random() * 4 + 2,
        duration: Math.random() * 3 + 2,
        delay: Math.random() * 2,
    }));

    return (
        <div className="min-h-screen bg-black flex items-center justify-center relative overflow-hidden">
            {/* Animated Background Gradients */}
            <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 1.5, ease: "easeOut" }}
                className="absolute inset-0"
            >
                <div className="absolute top-1/4 left-1/4 w-[600px] h-[600px] bg-nutri-mint/20 rounded-full blur-[120px] animate-pulse" />
                <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-teal-500/15 rounded-full blur-[100px] animate-pulse" style={{ animationDelay: '0.5s' }} />
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] bg-emerald-500/10 rounded-full blur-[80px]" />
            </motion.div>

            {/* Floating Particles */}
            {particles.map((particle) => (
                <motion.div
                    key={particle.id}
                    className="absolute rounded-full bg-nutri-mint/30"
                    style={{
                        left: `${particle.x}%`,
                        top: `${particle.y}%`,
                        width: particle.size,
                        height: particle.size,
                    }}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{
                        opacity: [0, 0.6, 0],
                        y: [-20, -60, -100],
                    }}
                    transition={{
                        duration: particle.duration,
                        delay: particle.delay,
                        repeat: Infinity,
                        ease: "easeOut"
                    }}
                />
            ))}

            {/* Main Content */}
            <div className="relative z-10 text-center px-6">
                {/* Logo Animation */}
                <motion.div
                    initial={{ scale: 0, opacity: 0, rotateY: -180 }}
                    animate={{ scale: 1, opacity: 1, rotateY: 0 }}
                    transition={{
                        duration: 0.8,
                        ease: [0.34, 1.56, 0.64, 1], // Custom spring-like easing
                    }}
                    className="mb-8"
                >
                    <motion.div
                        animate={{
                            boxShadow: [
                                "0 0 20px rgba(167, 239, 193, 0.3)",
                                "0 0 60px rgba(167, 239, 193, 0.5)",
                                "0 0 20px rgba(167, 239, 193, 0.3)",
                            ]
                        }}
                        transition={{ duration: 2, repeat: Infinity }}
                        className="inline-block p-6 rounded-3xl bg-gradient-to-br from-nutri-mint/20 to-teal-500/10 border border-nutri-mint/30"
                    >
                        <motion.img
                            src="/logo.png"
                            alt="NutriLens"
                            className="w-24 h-24 md:w-32 md:h-32"
                            animate={{ rotate: [0, 5, -5, 0] }}
                            transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
                        />
                    </motion.div>
                </motion.div>

                {/* Brand Name with Stagger Animation */}
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.5 }}
                    className="mb-4"
                >
                    <h1 className="text-5xl md:text-7xl font-bold tracking-tighter">
                        <motion.span
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.5, delay: 0.6 }}
                            className="text-white"
                        >
                            Nutri
                        </motion.span>
                        <motion.span
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.5, delay: 0.8 }}
                            className="text-transparent bg-clip-text bg-gradient-to-r from-nutri-mint to-teal-300"
                        >
                            Lens
                        </motion.span>
                    </h1>
                </motion.div>

                {/* Welcome Message */}
                <AnimatePresence>
                    {showContent && (
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            transition={{ duration: 0.6 }}
                            className="mb-8"
                        >
                            <motion.div
                                initial={{ scale: 0 }}
                                animate={{ scale: 1 }}
                                transition={{ duration: 0.4, delay: 0.2 }}
                                className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-nutri-mint/10 border border-nutri-mint/30 mb-6"
                            >
                                <Sparkles className="w-4 h-4 text-nutri-mint" />
                                <span className="text-sm font-medium text-nutri-mint">Welcome aboard!</span>
                            </motion.div>

                            <h2 className="text-2xl md:text-3xl font-semibold text-white mb-4">
                                You're all set!
                            </h2>
                            <p className="text-gray-400 text-lg max-w-md mx-auto leading-relaxed">
                                Start scanning ingredients and make informed food choices with NutriLens.
                            </p>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Continue Button */}
                <AnimatePresence>
                    {showButton && (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.8 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ duration: 0.5, type: "spring", stiffness: 200 }}
                        >
                            <motion.button
                                onClick={handleContinue}
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                className="group relative px-8 py-4 bg-gradient-to-r from-nutri-mint to-teal-400 text-black font-bold text-lg rounded-2xl shadow-lg shadow-nutri-mint/30 overflow-hidden"
                            >
                                {/* Button Shimmer Effect */}
                                <motion.div
                                    className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent"
                                    initial={{ x: "-100%" }}
                                    animate={{ x: "100%" }}
                                    transition={{ duration: 1.5, repeat: Infinity, repeatDelay: 1 }}
                                />
                                <span className="relative flex items-center gap-2">
                                    Get Started
                                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                                </span>
                            </motion.button>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Loading Dots (shown before button appears) */}
                {!showButton && showContent && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="flex justify-center gap-2 mt-8"
                    >
                        {[0, 1, 2].map((i) => (
                            <motion.div
                                key={i}
                                className="w-3 h-3 rounded-full bg-nutri-mint/50"
                                animate={{ scale: [1, 1.3, 1], opacity: [0.5, 1, 0.5] }}
                                transition={{ duration: 0.8, repeat: Infinity, delay: i * 0.2 }}
                            />
                        ))}
                    </motion.div>
                )}
            </div>

            {/* Radial Light Burst Behind Logo */}
            <motion.div
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 0.3, scale: 1 }}
                transition={{ duration: 1, delay: 0.3 }}
                className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] pointer-events-none"
            >
                <div className="w-full h-full bg-gradient-radial from-nutri-mint/20 via-transparent to-transparent rounded-full" />
            </motion.div>
        </div>
    );
};

export default Welcome;
