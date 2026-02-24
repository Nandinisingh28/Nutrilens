import React from 'react';
import { motion } from 'framer-motion';

const STATUS_COLORS = {
    good: { bar: 'from-green-400 to-emerald-500', text: 'text-green-400', bg: 'bg-green-500/10' },
    warn: { bar: 'from-yellow-400 to-amber-500', text: 'text-yellow-400', bg: 'bg-yellow-500/10' },
    bad:  { bar: 'from-red-400 to-rose-500', text: 'text-red-400', bg: 'bg-red-500/10' },
};

const NutritionBar = ({ name, value, unit, threshold, status, delay = 0 }) => {
    const cfg = STATUS_COLORS[status] || STATUS_COLORS.warn;
    // Bar fill = min(value / (threshold * 2), 1) * 100 to allow overflow visual
    const fillPct = Math.min((value / (threshold * 2)) * 100, 100);

    return (
        <div className="flex items-center gap-4">
            <div className="w-28 flex-shrink-0">
                <p className="text-sm font-medium text-gray-300">{name}</p>
                <p className={`text-xs font-bold ${cfg.text}`}>{value}{unit}</p>
            </div>
            <div className="flex-1 relative">
                <div className="h-2.5 rounded-full bg-white/5 overflow-hidden">
                    <motion.div
                        className={`h-full rounded-full bg-gradient-to-r ${cfg.bar}`}
                        initial={{ width: 0 }}
                        animate={{ width: `${fillPct}%` }}
                        transition={{ duration: 0.9, ease: 'easeOut', delay: 0.2 + delay }}
                    />
                </div>
                {/* Threshold marker */}
                <div
                    className="absolute top-0 h-2.5 w-0.5 bg-white/30 rounded-full"
                    style={{ left: `50%` }}
                    title={`Threshold: ${threshold}${unit}`}
                />
            </div>
            <div className={`flex-shrink-0 text-xs px-2 py-0.5 rounded-full ${cfg.bg} ${cfg.text} font-medium`}>
                {status === 'good' ? 'OK' : status === 'warn' ? 'High' : 'Excess'}
            </div>
        </div>
    );
};

export default NutritionBar;
