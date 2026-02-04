import { motion } from 'framer-motion'
import { CheckCircle, AlertTriangle, XCircle, HelpCircle } from 'lucide-react'
import { getVerdictStyles } from '@/app/theme'
import { cn } from '@/lib/utils'

interface ResultCardsProps {
    verdict: string
    score: number | null
    warnings: string[]
    recommendations: string[]
    nutrition?: Record<string, number | null>
}

export function ResultCards({
    verdict,
    score,
    warnings,
    recommendations,
    nutrition,
}: ResultCardsProps) {
    const verdictStyles = getVerdictStyles(verdict)

    const VerdictIcon = {
        healthy: CheckCircle,
        moderate: AlertTriangle,
        unhealthy: XCircle,
        unknown: HelpCircle,
    }[verdict] || HelpCircle

    return (
        <div className="space-y-6">
            {/* Verdict Card */}
            <motion.div
                className={cn(
                    'rounded-2xl p-6 border-2',
                    verdictStyles.bg,
                    verdictStyles.border
                )}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
            >
                <div className="flex items-center space-x-4">
                    <div className={cn('p-3 rounded-xl', verdictStyles.bg)}>
                        <VerdictIcon className={cn('w-8 h-8', verdictStyles.text)} />
                    </div>
                    <div>
                        <h3 className={cn('text-2xl font-bold capitalize', verdictStyles.text)}>
                            {verdict}
                        </h3>
                        {score !== null && (
                            <p className="text-muted-foreground">
                                Health Score: <span className="font-semibold">{score}/100</span>
                            </p>
                        )}
                    </div>
                </div>
            </motion.div>

            {/* Nutrition Grid */}
            {nutrition && Object.keys(nutrition).length > 0 && (
                <motion.div
                    className="glass-card p-6"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                >
                    <h4 className="font-semibold text-lg mb-4">Nutrition Facts</h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                        {Object.entries(nutrition).map(([key, value]) => {
                            if (value === null) return null
                            return (
                                <NutritionItem
                                    key={key}
                                    label={formatLabel(key)}
                                    value={value}
                                    unit={getUnit(key)}
                                />
                            )
                        })}
                    </div>
                </motion.div>
            )}

            {/* Warnings */}
            {warnings.length > 0 && (
                <motion.div
                    className="glass-card p-6"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                >
                    <h4 className="font-semibold text-lg mb-4 flex items-center">
                        <AlertTriangle className="w-5 h-5 text-yellow-500 mr-2" />
                        Warnings
                    </h4>
                    <ul className="space-y-2">
                        {warnings.map((warning, index) => (
                            <li key={index} className="flex items-start space-x-2">
                                <span className="w-1.5 h-1.5 rounded-full bg-yellow-500 mt-2" />
                                <span className="text-muted-foreground">{warning}</span>
                            </li>
                        ))}
                    </ul>
                </motion.div>
            )}

            {/* Recommendations */}
            {recommendations.length > 0 && (
                <motion.div
                    className="glass-card p-6"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 }}
                >
                    <h4 className="font-semibold text-lg mb-4 flex items-center">
                        <CheckCircle className="w-5 h-5 text-primary mr-2" />
                        Recommendations
                    </h4>
                    <ul className="space-y-2">
                        {recommendations.map((rec, index) => (
                            <li key={index} className="flex items-start space-x-2">
                                <span className="w-1.5 h-1.5 rounded-full bg-primary mt-2" />
                                <span className="text-muted-foreground">{rec}</span>
                            </li>
                        ))}
                    </ul>
                </motion.div>
            )}
        </div>
    )
}

function NutritionItem({
    label,
    value,
    unit,
}: {
    label: string
    value: number
    unit: string
}) {
    return (
        <div className="p-3 rounded-lg bg-gray-50 border border-gray-100">
            <p className="text-sm text-muted-foreground">{label}</p>
            <p className="text-lg font-semibold">
                {value}
                <span className="text-sm text-muted-foreground ml-1">{unit}</span>
            </p>
        </div>
    )
}

function formatLabel(key: string): string {
    return key
        .replace(/_/g, ' ')
        .replace(/\b\w/g, (l) => l.toUpperCase())
}

function getUnit(key: string): string {
    if (key.includes('sodium') || key.includes('cholesterol')) return 'mg'
    if (key === 'calories') return ''
    return 'g'
}
