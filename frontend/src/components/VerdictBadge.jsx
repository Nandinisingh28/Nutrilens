import { CheckCircle, AlertCircle, XCircle, HelpCircle, AlertTriangle, ShieldCheck, ShieldX, ShieldAlert, ShieldQuestion } from 'lucide-react';

function VerdictBadge({ verdict, size = 'default' }) {
    const getVerdictConfig = (v) => {
        const configs = {
            TRUE: {
                label: '✅ VERIFIED TRUE',
                className: 'true',
                Icon: CheckCircle,
            },
            PARTIALLY_TRUE: {
                label: '⚠️ PARTIALLY TRUE',
                className: 'partially-true',
                Icon: AlertCircle,
            },
            MISLEADING: {
                label: '⚠️ MISLEADING',
                className: 'misleading',
                Icon: AlertTriangle,
            },
            FALSE: {
                label: '❌ FALSE CLAIM',
                className: 'false',
                Icon: XCircle,
            },
            UNVERIFIABLE: {
                label: '❓ CANNOT VERIFY',
                className: 'unverifiable',
                Icon: HelpCircle,
            },
        };

        return configs[v] || configs.UNVERIFIABLE;
    };

    const config = getVerdictConfig(verdict);
    const sizeClass = size === 'large' ? 'verdict-large' : '';

    return (
        <span className={`verdict-badge ${config.className} ${sizeClass}`}>
            <config.Icon size={size === 'large' ? 24 : 16} />
            {config.label}
        </span>
    );
}

export default VerdictBadge;
