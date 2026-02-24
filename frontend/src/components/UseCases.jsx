import React from 'react';
import { motion } from 'framer-motion';
import { HeartPulse, Factory, Scale } from 'lucide-react';

// eslint-disable-next-line react/prop-types
const UseCaseCard = ({ icon: Icon, image, title, description, colorClass, bgClass }) => (
    <motion.div
        variants={{
            hidden: { opacity: 0, y: 20 },
            visible: { opacity: 1, y: 0 }
        }}
        className="relative overflow-hidden p-10 rounded-3xl bg-white/5 border border-white/10
                 hover:bg-white/10 hover:border-white/20 hover:-translate-y-2
                 transition-all duration-300 group h-full flex flex-col items-center text-center backdrop-blur-sm"
    >
        {/* Glow Effect */}
        <div className={`absolute -top-20 -right-20 w-40 h-40 rounded-full blur-[60px] opacity-0 group-hover:opacity-20 transition-opacity duration-500 ${bgClass.replace('bg-', 'bg-')}`}></div>

        <div className={`w-20 h-20 rounded-2xl flex items-center justify-center mb-8 bg-gray-900/50 border border-white/5 group-hover:scale-110 transition-transform duration-300`}>
            {image ? (
                <img src={image} alt={title} className="w-12 h-12 object-contain brightness-0 invert" />
            ) : (
                <Icon className={`w-10 h-10 ${colorClass}`} />
            )}
        </div>
        <h3 className="text-2xl font-bold text-white mb-4 tracking-tight">{title}</h3>
        <p className="text-gray-400 leading-relaxed font-light">{description}</p>
    </motion.div>
);

const UseCases = () => {
    return (
        <section className="py-32 bg-black relative overflow-hidden">
            {/* Background Elements */}
            <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-nutri-mint/10 rounded-full blur-3xl opacity-20 pointer-events-none"></div>

            <div className="max-w-[1200px] mx-auto px-6 relative z-10">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    className="text-center mb-20"
                >
                    <h2 className="text-4xl md:text-5xl font-bold text-white mb-6 tracking-tight">
                        Have a NutriLens for...
                    </h2>
                    <p className="text-xl text-gray-400 max-w-2xl mx-auto font-light">
                        Tailored solutions for every stakeholder in the food ecosystem.
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
                    className="grid grid-cols-1 md:grid-cols-3 gap-8"
                >
                    <UseCaseCard
                        image="/health-strong.png"
                        title="Health-conscious"
                        description="Individuals who prioritize clean eating and want to avoid specific ingredients, allergens, or additives."
                        colorClass="text-red-400"
                        bgClass="bg-red-400"
                    />

                    <UseCaseCard
                        image="/nutritionist.png"
                        title="Nutritionists"
                        description="Nutritionists seeking to analyze ingredient lists, assess nutritional quality, and provide evidence-based dietary guidance to clients."
                        colorClass="text-blue-400"
                        bgClass="bg-blue-400"
                    />

                    <UseCaseCard
                        image="/regulartory.png"
                        title="Regulatory Bodies"
                        description="Organizations monitoring food safety standards and compliance with local and international regulations."
                        colorClass="text-purple-400"
                        bgClass="bg-purple-400"
                    />
                </motion.div>
            </div>
        </section>
    );
};

export default UseCases;
