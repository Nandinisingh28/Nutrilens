import React from 'react';
import { motion } from 'framer-motion';

const ScoreCircle = ({ score, label, sublabel, color = '#A7EFC1' }) => {
    const radius = 44;
    const circumference = 2 * Math.PI * radius;
    const strokeDashoffset = circumference - (score / 100) * circumference;

    return (
        <div className="flex flex-col items-center gap-3">
            <div className="relative w-28 h-28">
                <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                    {/* Track */}
                    <circle cx="50" cy="50" r={radius} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="8" />
                    {/* Progress */}
                    <motion.circle
                        cx="50" cy="50" r={radius}
                        fill="none"
                        stroke={color}
                        strokeWidth="8"
                        strokeLinecap="round"
                        strokeDasharray={circumference}
                        initial={{ strokeDashoffset: circumference }}
                        animate={{ strokeDashoffset }}
                        transition={{ duration: 1.2, ease: 'easeOut', delay: 0.3 }}
                    />
                </svg>
                {/* Score text */}
                <div className="absolute inset-0 flex items-center justify-center">
                    <motion.span
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.5 }}
                        className="text-2xl font-bold text-white"
                    >
                        {score}
                    </motion.span>
                </div>
            </div>
            <div className="text-center">
                <p className="text-sm font-semibold text-white">{label}</p>
                {sublabel && <p className="text-xs text-gray-500 mt-0.5">{sublabel}</p>}
            </div>
        </div>
    );
};

export default ScoreCircle;
