import React from 'react';
import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

const QuestionCard = () => {
    return (
        <section className="py-24 bg-black relative">
            <div className="max-w-[1000px] mx-auto px-6 relative z-10">
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5 }}
                    className="relative rounded-[2.5rem] p-10 md:p-16 overflow-hidden
                        bg-gradient-to-br from-gray-900 to-black
                        border border-white/10 shadow-2xl"
                >
                    {/* Decorative background blur */}
                    <div className="absolute top-0 right-0 w-80 h-80 bg-nutri-mint/10
                          rounded-full blur-[80px] -mr-20 -mt-20
                          pointer-events-none z-0">
                    </div>

                    {/* Content */}
                    <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-10">
                        <div className="flex items-start gap-8 max-w-xl">
                            {/* ICON */}
                            <div className="hidden sm:flex relative z-20">
                                <motion.img
                                    initial={{ rotate: -10, y: 10 }}
                                    whileInView={{ rotate: 0, y: 0 }}
                                    transition={{ duration: 0.8, type: "spring" }}
                                    src="/question.png"
                                    alt="Question icon"
                                    className="w-24 h-24 object-contain drop-shadow-[0_0_15px_rgba(255,255,255,0.1)]"
                                />
                            </div>

                            <div>
                                <h3 className="text-3xl md:text-4xl font-bold text-white mb-4 tracking-tight">
                                    Unsure about the ingredients?
                                </h3>
                                <p className="text-lg text-gray-400 font-light leading-relaxed">
                                    Don't guess with your health. Let NutriLens decode the label for you
                                    in seconds with hospital-grade accuracy.
                                </p>
                            </div>
                        </div>

                        <div className="flex-shrink-0">
                            <Link to="/signup">
                                <motion.button
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                    className="bg-white text-gray-900 text-lg font-bold py-4 px-8 rounded-full shadow-[0_0_20px_rgba(255,255,255,0.2)] hover:shadow-[0_0_30px_rgba(255,255,255,0.4)] transition-all flex items-center group"
                                >
                                    Try NutriLens
                                    <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
                                </motion.button>
                            </Link>
                        </div>

                    </div>
                </motion.div>
            </div>
        </section>
    );
};

export default QuestionCard;
