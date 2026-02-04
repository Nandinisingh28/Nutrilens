import { useParams, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import {
    ArrowLeft,
    Loader2,
    CheckCircle,
    AlertTriangle,
    XCircle,
    HelpCircle,
    Clock,
    FileText,
    Apple,
    Zap,
    RefreshCw,
    AlertCircle,
    Camera,
    Scale,
    Beaker,
    Candy,
    ShieldAlert,
} from 'lucide-react'
import { scanApi, ClaimResult } from '@/app/api'

const verdictConfig = {
    true: {
        label: 'Verified',
        color: 'text-green-600',
        bg: 'bg-green-50 dark:bg-green-900/20',
        border: 'border-green-200 dark:border-green-800',
        icon: CheckCircle,
    },
    misleading: {
        label: 'Misleading',
        color: 'text-amber-600',
        bg: 'bg-amber-50 dark:bg-amber-900/20',
        border: 'border-amber-200 dark:border-amber-800',
        icon: AlertTriangle,
    },
    false: {
        label: 'False',
        color: 'text-red-600',
        bg: 'bg-red-50 dark:bg-red-900/20',
        border: 'border-red-200 dark:border-red-800',
        icon: XCircle,
    },
    mixed: {
        label: 'Mixed',
        color: 'text-orange-600',
        bg: 'bg-orange-50 dark:bg-orange-900/20',
        border: 'border-orange-200 dark:border-orange-800',
        icon: AlertTriangle,
    },
    unknown: {
        label: 'Unknown',
        color: 'text-gray-600',
        bg: 'bg-gray-50 dark:bg-gray-800',
        border: 'border-gray-200 dark:border-gray-700',
        icon: HelpCircle,
    },
}

function OCRQualityWarning({ confidence, onRetry, isRetrying }: {
    confidence: number
    onRetry: () => void
    isRetrying: boolean
}) {
    if (confidence >= 0.7) return null

    const isLow = confidence < 0.5

    return (
        <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`rounded-xl p-4 mb-6 border ${isLow
                    ? 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
                    : 'bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800'
                }`}
        >
            <div className="flex items-start gap-3">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${isLow ? 'bg-red-100 dark:bg-red-900' : 'bg-amber-100 dark:bg-amber-900'
                    }`}>
                    <AlertCircle className={`w-5 h-5 ${isLow ? 'text-red-600' : 'text-amber-600'}`} />
                </div>
                <div className="flex-1">
                    <h3 className={`font-semibold ${isLow ? 'text-red-700 dark:text-red-400' : 'text-amber-700 dark:text-amber-400'}`}>
                        {isLow ? 'Low Image Quality Detected' : 'Image Quality Could Be Better'}
                    </h3>
                    <p className={`text-sm mt-1 ${isLow ? 'text-red-600/80' : 'text-amber-600/80'}`}>
                        OCR confidence: {Math.round(confidence * 100)}%.
                        {isLow
                            ? ' Results may be inaccurate. Please try again with a clearer image.'
                            : ' Some text may not have been recognized correctly.'
                        }
                    </p>
                    <div className="mt-3 flex items-center gap-4">
                        <button
                            onClick={onRetry}
                            disabled={isRetrying}
                            className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all ${isLow
                                    ? 'bg-red-600 text-white hover:bg-red-700'
                                    : 'bg-amber-600 text-white hover:bg-amber-700'
                                } disabled:opacity-50`}
                        >
                            {isRetrying ? (
                                <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                                <Camera className="w-4 h-4" />
                            )}
                            {isRetrying ? 'Reprocessing...' : 'Try Again with New Image'}
                        </button>
                    </div>
                    <div className="mt-3 text-xs space-y-1 text-muted-foreground">
                        <p>💡 Tips for better results:</p>
                        <ul className="list-disc list-inside ml-2">
                            <li>Ensure good lighting without shadows</li>
                            <li>Hold camera steady and in focus</li>
                            <li>Capture the entire label in frame</li>
                            <li>Avoid glare from packaging</li>
                        </ul>
                    </div>
                </div>
            </div>
        </motion.div>
    )
}

function QuantitySatisfactionCard({ nutrition, servingSize }: {
    nutrition: { values: Record<string, number>; normalized_per_100g: Record<string, number> }
    servingSize?: { value: number; unit: string }
}) {
    const dailyValues: Record<string, { max: number; unit: string; label: string }> = {
        energy: { max: 2000, unit: 'kcal', label: 'Energy' },
        protein: { max: 50, unit: 'g', label: 'Protein' },
        carbohydrates: { max: 300, unit: 'g', label: 'Carbs' },
        sugar: { max: 25, unit: 'g', label: 'Sugar' },
        fat: { max: 65, unit: 'g', label: 'Fat' },
        saturated_fat: { max: 20, unit: 'g', label: 'Sat. Fat' },
        fiber: { max: 30, unit: 'g', label: 'Fiber' },
        sodium: { max: 2300, unit: 'mg', label: 'Sodium' },
    }

    const values = nutrition.normalized_per_100g || nutrition.values

    return (
        <div className="glass-card p-5">
            <h3 className="font-semibold mb-3 flex items-center gap-2">
                <Scale className="w-4 h-4 text-primary" />
                Daily Value Context
            </h3>
            {servingSize && (
                <p className="text-xs text-muted-foreground mb-3">
                    Based on {servingSize.value}{servingSize.unit} serving
                </p>
            )}
            <div className="space-y-3">
                {Object.entries(dailyValues).map(([key, dv]) => {
                    const value = values[key]
                    if (value === undefined) return null

                    const percentage = Math.min((value / dv.max) * 100, 100)
                    const isHigh = percentage > 50
                    const isVeryHigh = percentage > 75

                    return (
                        <div key={key} className="text-sm">
                            <div className="flex justify-between mb-1">
                                <span className="text-muted-foreground">{dv.label}</span>
                                <span className={`font-medium ${isVeryHigh ? 'text-red-600' : isHigh ? 'text-amber-600' : 'text-green-600'
                                    }`}>
                                    {Math.round(percentage)}% DV
                                </span>
                            </div>
                            <div className="h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                                <motion.div
                                    initial={{ width: 0 }}
                                    animate={{ width: `${percentage}%` }}
                                    transition={{ duration: 0.5, delay: 0.1 }}
                                    className={`h-full rounded-full ${isVeryHigh
                                            ? 'bg-red-500'
                                            : isHigh
                                                ? 'bg-amber-500'
                                                : 'bg-green-500'
                                        }`}
                                />
                            </div>
                        </div>
                    )
                })}
            </div>
            <p className="text-xs text-muted-foreground mt-3 pt-3 border-t">
                % Daily Value based on a 2,000 calorie diet. Your needs may vary.
            </p>
        </div>
    )
}

function EnhancedIngredientsCard({ ingredients }: {
    ingredients: {
        count: number
        list?: Array<{
            name: string
            is_sugar_alias: boolean
            is_additive: boolean
            is_preservative: boolean
        }>
        sugar_aliases_found: string[]
        has_sugar_alias: boolean
        has_preservatives: boolean
    }
}) {
    const flaggedItems = ingredients.list?.filter(
        i => i.is_sugar_alias || i.is_additive || i.is_preservative
    ) || []

    return (
        <div className="glass-card p-5">
            <h3 className="font-semibold mb-3 flex items-center gap-2">
                <Beaker className="w-4 h-4 text-primary" />
                Ingredients Analysis
            </h3>

            <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                    <span className="text-muted-foreground">Total ingredients</span>
                    <span className="font-medium">{ingredients.count}</span>
                </div>

                {ingredients.has_sugar_alias && (
                    <div className="pt-2 border-t">
                        <div className="flex items-center gap-2 mb-2">
                            <Candy className="w-4 h-4 text-amber-600" />
                            <span className="text-amber-600 font-medium text-xs">Sugar Aliases Found</span>
                        </div>
                        <div className="flex flex-wrap gap-1">
                            {ingredients.sugar_aliases_found.map((alias, i) => (
                                <span
                                    key={i}
                                    className="px-2 py-0.5 bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400 rounded text-xs"
                                >
                                    {alias}
                                </span>
                            ))}
                        </div>
                        <p className="text-xs text-muted-foreground mt-2">
                            These ingredients are hidden forms of sugar. Products may claim "no added sugar" while containing these.
                        </p>
                    </div>
                )}

                {ingredients.has_preservatives && (
                    <div className="pt-2 border-t">
                        <div className="flex items-center gap-2">
                            <ShieldAlert className="w-4 h-4 text-orange-600" />
                            <span className="text-orange-600 font-medium text-xs">Contains Preservatives</span>
                        </div>
                    </div>
                )}

                {flaggedItems.length > 0 && (
                    <div className="pt-2 border-t">
                        <p className="text-xs text-muted-foreground mb-2">Flagged Ingredients:</p>
                        <div className="space-y-1">
                            {flaggedItems.slice(0, 5).map((item, i) => (
                                <div key={i} className="flex items-center gap-2 text-xs">
                                    <span className={`px-1.5 py-0.5 rounded ${item.is_sugar_alias
                                            ? 'bg-amber-100 text-amber-700'
                                            : item.is_preservative
                                                ? 'bg-orange-100 text-orange-700'
                                                : 'bg-purple-100 text-purple-700'
                                        }`}>
                                        {item.is_sugar_alias ? 'Sugar' : item.is_preservative ? 'Preserv.' : 'Additive'}
                                    </span>
                                    <span>{item.name}</span>
                                </div>
                            ))}
                            {flaggedItems.length > 5 && (
                                <p className="text-muted-foreground">+{flaggedItems.length - 5} more</p>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}

export default function Results() {
    const { id } = useParams<{ id: string }>()
    const navigate = useNavigate()
    const queryClient = useQueryClient()

    const { data, isLoading, error } = useQuery({
        queryKey: ['scan', id],
        queryFn: async () => {
            const response = await scanApi.getById(Number(id))
            return response.data.data
        },
        enabled: !!id,
    })

    const reprocessMutation = useMutation({
        mutationFn: () => scanApi.reprocess(Number(id)),
        onSuccess: () => {
            toast.success('Scan reprocessed!')
            queryClient.invalidateQueries({ queryKey: ['scan', id] })
        },
        onError: () => {
            toast.error('Failed to reprocess scan')
        },
    })

    if (isLoading) {
        return (
            <div className="flex flex-col items-center justify-center py-20">
                <Loader2 className="w-10 h-10 animate-spin text-primary mb-4" />
                <p className="text-muted-foreground">Loading results...</p>
            </div>
        )
    }

    if (error || !data) {
        return (
            <div className="text-center py-20">
                <XCircle className="w-12 h-12 text-destructive mx-auto mb-4" />
                <h2 className="text-xl font-semibold mb-2">Failed to load results</h2>
                <p className="text-muted-foreground mb-4">The scan could not be found.</p>
                <button
                    onClick={() => navigate('/app')}
                    className="px-4 py-2 rounded-lg bg-primary text-primary-foreground"
                >
                    Back to Home
                </button>
            </div>
        )
    }

    const scan = data
    const results = scan.results
    const verdict = scan.overall_verdict || 'unknown'
    const config = verdictConfig[verdict]
    const VerdictIcon = config.icon
    const ocrConfidence = results?.ocr?.confidence ?? 1

    return (
        <div className="max-w-4xl mx-auto">
            {/* Header */}
            <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="mb-6"
            >
                <button
                    onClick={() => navigate('/app')}
                    className="inline-flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors mb-4"
                >
                    <ArrowLeft className="w-4 h-4" />
                    New Scan
                </button>
            </motion.div>

            {/* OCR Quality Warning */}
            <OCRQualityWarning
                confidence={ocrConfidence}
                onRetry={() => navigate('/app')}
                isRetrying={reprocessMutation.isPending}
            />

            {/* Overall Verdict Banner */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className={`rounded-2xl p-6 mb-8 ${config.bg} border-2 ${config.border}`}
            >
                <div className="flex items-start gap-4">
                    <div className={`w-14 h-14 rounded-xl ${config.bg} flex items-center justify-center ${config.color}`}>
                        <VerdictIcon className="w-8 h-8" />
                    </div>
                    <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                            <h1 className="text-2xl font-bold">
                                {scan.product_name || 'Scanned Product'}
                            </h1>
                            <span className={`px-3 py-1 rounded-full text-sm font-medium ${config.bg} ${config.color} ${config.border} border`}>
                                {config.label}
                            </span>
                        </div>
                        {scan.brand && (
                            <p className="text-muted-foreground">{scan.brand}</p>
                        )}
                        {results?.overall?.summary && (
                            <p className={`mt-2 ${config.color} font-medium`}>
                                {results.overall.summary}
                            </p>
                        )}
                    </div>
                </div>

                {/* Metadata */}
                {results?.metadata && (
                    <div className="flex items-center gap-4 mt-4 pt-4 border-t border-current/10 text-sm text-muted-foreground">
                        <div className="flex items-center gap-1">
                            <Clock className="w-4 h-4" />
                            {results.metadata.processing_time_seconds}s processing
                        </div>
                        <div className="flex items-center gap-1">
                            <FileText className="w-4 h-4" />
                            {results.ocr?.word_count || 0} words detected
                        </div>
                        {ocrConfidence < 0.7 && (
                            <div className="flex items-center gap-1 text-amber-600">
                                <AlertCircle className="w-4 h-4" />
                                Low OCR quality
                            </div>
                        )}
                    </div>
                )}
            </motion.div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Claims */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="lg:col-span-2 space-y-4"
                >
                    <h2 className="text-lg font-semibold flex items-center gap-2">
                        <Zap className="w-5 h-5 text-primary" />
                        Claim Verification
                    </h2>

                    {results?.claims && results.claims.length > 0 ? (
                        <div className="space-y-3">
                            {results.claims.map((claim, index) => (
                                <ClaimCard key={index} claim={claim} />
                            ))}
                        </div>
                    ) : (
                        <div className="glass-card p-6 text-center text-muted-foreground">
                            <HelpCircle className="w-8 h-8 mx-auto mb-2 opacity-50" />
                            <p>No claims were detected or verified</p>
                        </div>
                    )}
                </motion.div>

                {/* Sidebar */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="space-y-6"
                >
                    {/* Nutrition Facts */}
                    {results?.nutrition?.has_values && (
                        <div className="glass-card p-5">
                            <h3 className="font-semibold mb-3 flex items-center gap-2">
                                <Apple className="w-4 h-4 text-primary" />
                                Nutrition (per 100g)
                            </h3>
                            <NutritionTable values={results.nutrition.normalized_per_100g} />
                        </div>
                    )}

                    {/* Quantity Satisfaction */}
                    {results?.nutrition?.has_values && (
                        <QuantitySatisfactionCard
                            nutrition={results.nutrition}
                            servingSize={results.nutrition.serving_size}
                        />
                    )}

                    {/* Enhanced Ingredients */}
                    {results?.ingredients && (
                        <EnhancedIngredientsCard ingredients={results.ingredients} />
                    )}

                    {/* Actions */}
                    <div className="glass-card p-5 space-y-3">
                        <button
                            onClick={() => navigate('/app')}
                            className="w-full py-2.5 px-4 rounded-xl bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-all flex items-center justify-center gap-2"
                        >
                            <RefreshCw className="w-4 h-4" />
                            Scan Another
                        </button>
                        <button
                            onClick={() => navigate('/app/history')}
                            className="w-full py-2.5 px-4 rounded-xl border border-input hover:bg-accent transition-all"
                        >
                            View History
                        </button>
                    </div>
                </motion.div>
            </div>
        </div>
    )
}

function ClaimCard({ claim }: { claim: ClaimResult }) {
    const config = verdictConfig[claim.verdict]
    const Icon = config.icon

    return (
        <div className={`glass-card p-5 border-l-4 ${config.border}`}>
            <div className="flex items-start gap-3">
                <div className={`w-10 h-10 rounded-lg ${config.bg} flex items-center justify-center ${config.color} flex-shrink-0`}>
                    <Icon className="w-5 h-5" />
                </div>
                <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-semibold capitalize">{claim.claim}</h4>
                        <span className={`text-xs px-2 py-0.5 rounded-full ${config.bg} ${config.color}`}>
                            {Math.round(claim.confidence * 100)}%
                        </span>
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">
                        {claim.explanation}
                    </p>

                    {claim.evidence.length > 0 && (
                        <div className="text-xs space-y-1">
                            {claim.evidence.slice(0, 3).map((ev, i) => (
                                <p key={i} className="text-muted-foreground bg-gray-50 dark:bg-gray-800 px-2 py-1 rounded">
                                    {ev}
                                </p>
                            ))}
                        </div>
                    )}

                    {claim.suggestions.length > 0 && (
                        <div className="mt-2 pt-2 border-t text-xs text-amber-600">
                            💡 {claim.suggestions[0]}
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}

function NutritionTable({ values }: { values: Record<string, number> }) {
    const nutrients = [
        { key: 'energy', label: 'Energy', unit: 'kcal' },
        { key: 'protein', label: 'Protein', unit: 'g' },
        { key: 'carbohydrates', label: 'Carbs', unit: 'g' },
        { key: 'sugar', label: 'Sugar', unit: 'g' },
        { key: 'fat', label: 'Fat', unit: 'g' },
        { key: 'saturated_fat', label: 'Sat. Fat', unit: 'g' },
        { key: 'fiber', label: 'Fiber', unit: 'g' },
        { key: 'sodium', label: 'Sodium', unit: 'mg' },
    ]

    return (
        <div className="space-y-2">
            {nutrients.map(({ key, label, unit }) => {
                const value = values[key]
                if (value === undefined) return null

                return (
                    <div key={key} className="flex justify-between text-sm">
                        <span className="text-muted-foreground">{label}</span>
                        <span className="font-medium">
                            {typeof value === 'number' ? value.toFixed(1) : value}{unit}
                        </span>
                    </div>
                )
            })}
        </div>
    )
}
