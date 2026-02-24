import React from 'react';
import { CheckCircle2, AlertCircle, AlertTriangle, XCircle, HelpCircle } from 'lucide-react';

const VERDICT_CONFIG = {
    TRUE: {
        label: 'True',
        color: 'text-green-400',
        bg: 'bg-green-500/15',
        border: 'border-green-500/40',
        glow: 'shadow-green-500/20',
        icon: CheckCircle2,
    },
    PARTIALLY_TRUE: {
        label: 'Partially True',
        color: 'text-yellow-400',
        bg: 'bg-yellow-500/15',
        border: 'border-yellow-500/40',
        glow: 'shadow-yellow-500/20',
        icon: AlertCircle,
    },
    MISLEADING: {
        label: 'Misleading',
        color: 'text-orange-400',
        bg: 'bg-orange-500/15',
        border: 'border-orange-500/40',
        glow: 'shadow-orange-500/20',
        icon: AlertTriangle,
    },
    FALSE: {
        label: 'False',
        color: 'text-red-400',
        bg: 'bg-red-500/15',
        border: 'border-red-500/40',
        glow: 'shadow-red-500/20',
        icon: XCircle,
    },
    UNVERIFIABLE: {
        label: 'Unverifiable',
        color: 'text-gray-400',
        bg: 'bg-gray-500/15',
        border: 'border-gray-500/40',
        glow: 'shadow-gray-500/20',
        icon: HelpCircle,
    },
};

export const getVerdictConfig = (verdict) =>
    VERDICT_CONFIG[verdict] || VERDICT_CONFIG.UNVERIFIABLE;

const VerdictBadge = ({ verdict, size = 'md' }) => {
    const cfg = getVerdictConfig(verdict);
    const Icon = cfg.icon;

    const sizes = {
        sm: 'text-xs px-3 py-1 gap-1.5',
        md: 'text-sm px-4 py-2 gap-2',
        lg: 'text-base px-5 py-2.5 gap-2.5',
    };

    const iconSizes = { sm: 'w-3.5 h-3.5', md: 'w-4 h-4', lg: 'w-5 h-5' };

    return (
        <span className={`inline-flex items-center rounded-full border font-semibold shadow-lg ${cfg.bg} ${cfg.border} ${cfg.color} ${cfg.glow} ${sizes[size]}`}>
            <Icon className={iconSizes[size]} />
            {cfg.label}
        </span>
    );
};

export default VerdictBadge;
