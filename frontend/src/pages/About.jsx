import React, { useRef } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import { Eye, Shield, Sparkles, Target, Users, Leaf } from 'lucide-react';

const About = () => {
    const sectionRef = useRef(null);
    const { scrollYProgress } = useScroll({
        target: sectionRef,
        offset: ["start start", "end start"]
    });

    const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0.8]);

    const features = [
        {
            icon: Eye,
            title: "Ingredient Analysis",
            description: "Decode complex food labels into clear, understandable insights"
        },
        {
            icon: Shield,
            title: "Additive Detection",
            description: "Identify preservatives and additives in your packaged foods"
        },
        {
            icon: Sparkles,
            title: "Clear Insights",
            description: "Transform complex terms into simple, readable information"
        }
    ];

    const values = [
        {
            icon: Target,
            title: "Transparency",
            description: "We believe everyone deserves to know what's in their food"
        },
        {
            icon: Users,
            title: "Accessibility",
            description: "Making ingredient information easy to understand for everyone"
        },
        {
            icon: Leaf,
            title: "Awareness",
            description: "Empowering informed food choices through knowledge"
        }
    ];

    return (
        <div ref={sectionRef} className="min-h-screen bg-black pt-24">
            {/* Hero Section */}
            <motion.section
                style={{ opacity }}
                className="relative py-20 overflow-hidden"
            >
                {/* Background Gradient */}
                <div className="absolute inset-0 bg-gradient-to-b from-nutri-mint/5 via-transparent to-transparent" />
                <div className="absolute top-20 left-1/4 w-96 h-96 bg-nutri-mint/10 rounded-full blur-3xl" />
                <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-teal-500/10 rounded-full blur-3xl" />

                <div className="relative max-w-[1200px] mx-auto px-6 text-center">
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8 }}
                    >
                        <div className="inline-flex items-center space-x-2 mb-6 px-4 py-1.5 rounded-full bg-white/10 backdrop-blur-md border border-white/20">
                            <span className="w-2 h-2 rounded-full bg-nutri-mint animate-pulse"></span>
                            <span className="text-xs font-medium uppercase tracking-wider text-nutri-mint-light">About Us</span>
                        </div>

                        <h1 className="text-5xl md:text-7xl font-bold tracking-tighter mb-8 leading-[1.1] text-white">
                            About{' '}
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-nutri-mint-light to-teal-200">
                                NutriLens
                            </span>
                        </h1>

                        <p className="text-lg md:text-xl text-gray-300 max-w-3xl mx-auto leading-relaxed">
                            A smart ingredient-checking platform created to help users better understand
                            the ingredients listed on food products.
                        </p>
                    </motion.div>
                </div>
            </motion.section>

            {/* Mission Section */}
            <section className="py-20 relative">
                <div className="max-w-[1200px] mx-auto px-6">
                    <motion.div
                        initial={{ opacity: 0, y: 40 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8 }}
                        viewport={{ once: true }}
                        className="bg-gradient-to-br from-white/5 to-white/[0.02] rounded-3xl p-8 md:p-12 border border-white/10 backdrop-blur-sm"
                    >
                        <div className="max-w-3xl mx-auto text-center">
                            <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
                                Our Mission
                            </h2>
                            <p className="text-gray-300 text-lg leading-relaxed mb-6">
                                Many food labels contain complex terms that are hard to interpret, and NutriLens
                                simplifies this information into clear and readable insights.
                            </p>
                            <p className="text-gray-300 text-lg leading-relaxed">
                                The platform is designed specifically for <span className="text-nutri-mint font-semibold">ingredient analysis</span>,
                                focusing on identifying additives, preservatives, and commonly used components in packaged foods.
                            </p>
                        </div>
                    </motion.div>
                </div>
            </section>

            {/* What We Do Section */}
            <section className="py-20 relative">
                <div className="max-w-[1200px] mx-auto px-6">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6 }}
                        viewport={{ once: true }}
                        className="text-center mb-16"
                    >
                        <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                            What We Do
                        </h2>
                        <p className="text-gray-400 max-w-2xl mx-auto">
                            NutriLens focuses on making ingredient information accessible and understandable
                        </p>
                    </motion.div>

                    <div className="grid md:grid-cols-3 gap-6">
                        {features.map((feature, index) => (
                            <motion.div
                                key={feature.title}
                                initial={{ opacity: 0, y: 30 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.6, delay: index * 0.1 }}
                                viewport={{ once: true }}
                                whileHover={{ y: -5, transition: { duration: 0.2 } }}
                                className="group p-8 rounded-2xl bg-white/[0.03] border border-white/10 hover:border-nutri-mint/30 hover:bg-white/[0.05] transition-all duration-300"
                            >
                                <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-nutri-mint/20 to-teal-500/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                                    <feature.icon className="w-7 h-7 text-nutri-mint" />
                                </div>
                                <h3 className="text-xl font-bold text-white mb-3">{feature.title}</h3>
                                <p className="text-gray-400 leading-relaxed">{feature.description}</p>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* What We Don't Do Section */}
            <section className="py-20 relative">
                <div className="max-w-[1200px] mx-auto px-6">
                    <motion.div
                        initial={{ opacity: 0, y: 40 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8 }}
                        viewport={{ once: true }}
                        className="bg-gradient-to-r from-nutri-red/10 to-orange-500/10 rounded-3xl p-8 md:p-12 border border-nutri-red/20"
                    >
                        <div className="max-w-3xl mx-auto text-center">
                            <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
                                What We <span className="text-nutri-red">Don't</span> Do
                            </h2>
                            <p className="text-gray-300 text-lg leading-relaxed">
                                NutriLens <span className="font-semibold">does not provide diet plans or meal recommendations</span>.
                                Instead, we focus purely on promoting awareness by helping users understand what's inside
                                the products they consume.
                            </p>
                        </div>
                    </motion.div>
                </div>
            </section>

            {/* Our Values Section */}
            <section className="py-20 relative">
                <div className="max-w-[1200px] mx-auto px-6">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6 }}
                        viewport={{ once: true }}
                        className="text-center mb-16"
                    >
                        <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                            Our Values
                        </h2>
                        <p className="text-gray-400 max-w-2xl mx-auto">
                            The principles that guide everything we do
                        </p>
                    </motion.div>

                    <div className="grid md:grid-cols-3 gap-6">
                        {values.map((value, index) => (
                            <motion.div
                                key={value.title}
                                initial={{ opacity: 0, y: 30 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.6, delay: index * 0.1 }}
                                viewport={{ once: true }}
                                className="text-center p-8"
                            >
                                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-nutri-mint/20 to-teal-500/10 flex items-center justify-center mx-auto mb-6">
                                    <value.icon className="w-8 h-8 text-nutri-mint" />
                                </div>
                                <h3 className="text-xl font-bold text-white mb-3">{value.title}</h3>
                                <p className="text-gray-400 leading-relaxed">{value.description}</p>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Closing Section */}
            <section className="py-20 relative">
                <div className="max-w-[1200px] mx-auto px-6">
                    <motion.div
                        initial={{ opacity: 0, y: 40 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8 }}
                        viewport={{ once: true }}
                        className="text-center bg-gradient-to-br from-nutri-mint/10 to-teal-500/5 rounded-3xl p-12 border border-nutri-mint/20"
                    >
                        <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
                            Make Informed Choices
                        </h2>
                        <p className="text-gray-300 text-lg max-w-2xl mx-auto leading-relaxed mb-8">
                            With a clean interface and an easy-to-use design, NutriLens aims to make ingredient
                            information accessible to everyone and encourage informed food choices through
                            <span className="text-nutri-mint font-semibold"> transparency</span> and
                            <span className="text-nutri-mint font-semibold"> clarity</span>.
                        </p>
                        <motion.a
                            href="/"
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="inline-flex items-center bg-white text-gray-900 text-lg font-bold px-8 py-4 rounded-xl hover:bg-gray-100 transition-all duration-300 shadow-[0_0_20px_rgba(255,255,255,0.3)]"
                        >
                            Get Started
                        </motion.a>
                    </motion.div>
                </div>
            </section>
        </div>
    );
};

export default About;
