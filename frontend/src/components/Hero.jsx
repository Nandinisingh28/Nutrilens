import React, { useRef } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import { ChevronRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import heroImage from '../assets/hero-image.jpg';

const Hero = () => {
    const sectionRef = useRef(null);
    const { scrollYProgress } = useScroll({
        target: sectionRef,
        offset: ["start start", "end start"]
    });

    const y = useTransform(scrollYProgress, [0, 1], ["0%", "50%"]);
    const opacity = useTransform(scrollYProgress, [0, 1], [1, 0]);
    const scale = useTransform(scrollYProgress, [0, 1], [1, 1.1]);

    return (
        <section ref={sectionRef} id="home" className="relative h-screen w-full flex items-center justify-center overflow-hidden bg-black">
            {/* Parallax Background Image */}
            <motion.div
                style={{ y, scale, opacity }}
                className="absolute inset-0 z-0"
            >
                <div className="absolute inset-0 bg-black/40 z-10" />
                <img
                    src={heroImage}
                    alt="NutriLens Hero"
                    className="w-full h-full object-cover"
                />
            </motion.div>

            {/* Content */}
            <div className="relative z-10 max-w-[1200px] mx-auto px-6 text-center text-white">
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.2 }}
                    className="flex flex-col items-center"
                >
                    <div className="inline-flex items-center space-x-2 mb-6 px-4 py-1.5 rounded-full bg-white/10 backdrop-blur-md border border-white/20">
                        <span className="w-2 h-2 rounded-full bg-nutri-mint animate-pulse"></span>
                        <span className="text-xs font-medium uppercase tracking-wider text-nutri-mint-light">Rule-Based Nutrition Analysis</span>
                    </div>

                    <h1 className="text-5xl md:text-7xl lg:text-8xl font-bold tracking-tighter mb-8 leading-[1.1]">
                        See what you <br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-nutri-mint-light to-teal-200">really eat.</span>
                    </h1>

                    <p className="inline-flex items-center space-x-2 mb-6 px-4 py-1.5 rounded-lg bg-white/10 backdrop-blur-sm border border-white/20 text-lg md:text-2xl text-gray-200 mb-10 max-w-2xl font-medium leading-relaxed text-nutri-mint-light">
                        Instantly analyze ingredients, detect allergens, and verify health claims with a single scan.
                    </p>

                    <div className="flex flex-col sm:flex-row items-center gap-5">
                        <Link to="/signup">
                            <motion.button
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                className="bg-white text-gray-900 text-lg font-bold px-8 py-4 rounded-xl hover:bg-gray-100 transition-all duration-300 flex items-center shadow-[0_0_20px_rgba(255,255,255,0.3)]"
                            >
                                Get Started
                                <ChevronRight className="ml-2 w-5 h-5" />
                            </motion.button>
                        </Link>
                    </div>
                </motion.div>
            </div>

            {/* Scroll Indicator */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1, duration: 1 }}
                className="absolute bottom-10 left-1/2 -translate-x-1/2 text-white/50 flex flex-col items-center"
            >
                <div className="w-[1px] h-12 bg-gradient-to-b from-transparent via-white/50 to-transparent"></div>
            </motion.div>
        </section>
    );
};

export default Hero;
