import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import {
    ArrowLeft, CheckCircle2, XCircle, AlertTriangle, BarChart2,
    ShieldAlert, Calendar, Tag, Target, Zap, Share2, RotateCcw,
} from 'lucide-react';
import VerdictBadge, { getVerdictConfig } from '../components/VerdictBadge';
import ScoreCircle from '../components/ScoreCircle';
import NutritionBar from '../components/NutritionBar';
import * as api from '../utils/api';

const pageVariants = {
    initial: { opacity: 0, y: 16 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -16 },
};

const RISK_COLORS = {
    low: 'bg-green-500/10 text-green-400 border-green-500/30',
    medium: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30',
    high: 'bg-red-500/10 text-red-400 border-red-500/30',
};

const VERDICT_BG = {
    TRUE: 'from-green-500/10 to-transparent border-green-500/20',
    PARTIALLY_TRUE: 'from-yellow-500/10 to-transparent border-yellow-500/20',
    MISLEADING: 'from-orange-500/10 to-transparent border-orange-500/20',
    FALSE: 'from-red-500/10 to-transparent border-red-500/20',
    UNVERIFIABLE: 'from-gray-500/10 to-transparent border-gray-500/20',
};

const SCORE_COLORS = {
    TRUE: '#22c55e',
    PARTIALLY_TRUE: '#eab308',
    MISLEADING: '#f97316',
    FALSE: '#ef4444',
    UNVERIFIABLE: '#6b7280',
};

/**
 * Build a nutrition overview array from the backend NutritionData object.
 * Values are per 100g; we display them as a percentage of a max reference value.
 */
function buildNutritionOverview(nutrition) {
    if (!nutrition) return [];
    const items = [
        { name: 'Protein', value: nutrition.protein, unit: 'g', max: 40, color: '#22c55e' },
        { name: 'Sugar', value: nutrition.sugar, unit: 'g', max: 100, color: '#eab308' },
        { name: 'Fat', value: nutrition.fat, unit: 'g', max: 70, color: '#f97316' },
        { name: 'Fiber', value: nutrition.fiber, unit: 'g', max: 30, color: '#3b82f6' },
        { name: 'Calories', value: nutrition.calories, unit: 'kcal', max: 500, color: '#a855f7' },
        { name: 'Sodium', value: nutrition.sodium, unit: 'mg', max: 2000, color: '#ec4899' },
    ];
    return items
        .filter((i) => i.value != null)
        .map((i) => ({
            ...i,
            percentage: Math.min(Math.round((i.value / i.max) * 100), 100),
        }));
}

/**
 * Parse ingredient_warnings strings into structured objects.
 * Backend sends ["Ingredient Name: concern text", ...]
 */
function parseIngredientWarnings(warnings) {
    if (!warnings || warnings.length === 0) return [];
    return warnings.map((w) => {
        const colonIdx = w.indexOf(':');
        if (colonIdx > -1) {
            return { name: w.slice(0, colonIdx).trim(), note: w.slice(colonIdx + 1).trim(), risk: 'medium' };
        }
        return { name: w, note: '', risk: 'medium' };
    });
}

const Results = () => {
    const navigate = useNavigate();
    const { id } = useParams();
    const location = useLocation();

    // If result was passed via navigation state (fresh scan), use it directly.
    // Otherwise fetch it from the backend by ID.
    const [result, setResult] = useState(location.state?.result || null);
    const [loading, setLoading] = useState(!result);
    const [error, setError] = useState('');

    useEffect(() => {
        if (!result && id) {
            api.getScanById(id)
                .then(setResult)
                .catch((err) => setError(err.message || 'Failed to load scan result.'))
                .finally(() => setLoading(false));
        }
    }, [id]);

    const formatDate = (iso) => {
        if (!iso) return '';
        return new Date(iso).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <span className="w-10 h-10 border-2 border-nutri-mint/40 border-t-nutri-mint rounded-full animate-spin" />
            </div>
        );
    }

    if (error || !result) {
        return (
            <div className="min-h-screen flex flex-col items-center justify-center gap-4 px-6">
                <p className="text-nutri-red text-lg">{error || 'Scan not found.'}</p>
                <button
                    onClick={() => navigate('/history')}
                    className="px-6 py-3 rounded-xl bg-nutri-mint text-black font-bold"
                >
                    Back to History
                </button>
            </div>
        );
    }

    const verdict = result.verdict || 'UNVERIFIABLE';
    const verdictBg = VERDICT_BG[verdict] || VERDICT_BG.UNVERIFIABLE;
    const scoreColor = SCORE_COLORS[verdict] || '#6b7280';
    const nutritionOverview = buildNutritionOverview(result.nutrition);
    const ingredientWarnings = parseIngredientWarnings(result.ingredient_warnings);
    const claimBreakdown = (result.sub_claims || []).map((sc) => ({
        claim: sc.sub_claim || sc.claim_type,
        reason: sc.reason,
        passed: sc.verdict === 'TRUE' || sc.verdict === 'PARTIALLY_TRUE',
    }));

    const Section = ({ icon: Icon, title, children }) => (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="bg-white/[0.03] border border-white/10 rounded-2xl p-6"
        >
            <div className="flex items-center gap-3 mb-5">
                <div className="w-9 h-9 rounded-xl bg-nutri-mint/10 flex items-center justify-center">
                    <Icon className="w-5 h-5 text-nutri-mint" />
                </div>
                <h3 className="text-lg font-bold text-white">{title}</h3>
            </div>
            {children}
        </motion.div>
    );

    return (
        <motion.div
            variants={pageVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={{ duration: 0.4 }}
            className="min-h-screen py-10 px-6 relative overflow-hidden"
        >
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[700px] h-[300px] bg-nutri-mint/5 rounded-full blur-[100px] pointer-events-none" />

            <div className="max-w-3xl mx-auto relative z-10">
                {/* Back + actions */}
                <div className="flex items-center justify-between mb-8">
                    <motion.button
                        initial={{ opacity: 0, x: -16 }}
                        animate={{ opacity: 1, x: 0 }}
                        onClick={() => navigate(-1)}
                        className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
                    >
                        <ArrowLeft className="w-4 h-4" /> Back
                    </motion.button>
                    <div className="flex items-center gap-2">
                        <motion.button
                            whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                            onClick={() => navigate('/dashboard')}
                            className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-gray-300 hover:text-white text-sm transition-colors"
                        >
                            <RotateCcw className="w-4 h-4" /> New Scan
                        </motion.button>
                        <motion.button
                            whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                            onClick={() => navigator.clipboard?.writeText(window.location.href)}
                            className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-gray-300 hover:text-white text-sm transition-colors"
                        >
                            <Share2 className="w-4 h-4" /> Share
                        </motion.button>
                    </div>
                </div>

                {/* Verdict Banner */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                    className={`rounded-2xl bg-gradient-to-b ${verdictBg} border p-6 mb-6`}
                >
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-5">
                        <div>
                            <div className="flex flex-wrap items-center gap-3 mb-3">
                                <VerdictBadge verdict={verdict} size="lg" />
                                <span className="flex items-center gap-1.5 text-xs text-gray-500 bg-white/5 border border-white/10 px-3 py-1 rounded-full">
                                    {result.scan_mode === 'PRECISION' ? <Target className="w-3.5 h-3.5" /> : <Zap className="w-3.5 h-3.5" />}
                                    {result.scan_mode === 'PRECISION' ? 'Precision' : 'Quick'} Scan
                                </span>
                            </div>
                            <div className="flex flex-wrap gap-3 text-sm text-gray-400">
                                <span className="flex items-center gap-1.5"><Tag className="w-4 h-4" />{result.category}</span>
                                <span className="flex items-center gap-1.5"><Calendar className="w-4 h-4" />{formatDate(result.created_at)}</span>
                            </div>
                            <p className="mt-3 text-gray-300 text-sm italic">
                                Claim: "<span className="text-white not-italic font-medium">{result.user_claim}</span>"
                            </p>
                            {result.explanation && (
                                <p className="mt-2 text-gray-400 text-sm leading-relaxed">{result.explanation}</p>
                            )}
                        </div>

                        {/* Score circles */}
                        <div className="flex gap-8 justify-center">
                            <ScoreCircle
                                score={result.score ?? 0}
                                label="Verification"
                                sublabel="Accuracy"
                                color={scoreColor}
                            />
                            {result.health_score != null && (
                                <ScoreCircle
                                    score={result.health_score}
                                    label="Health Score"
                                    sublabel="Out of 100"
                                    color={result.health_score >= 70 ? '#22c55e' : result.health_score >= 45 ? '#eab308' : '#ef4444'}
                                />
                            )}
                        </div>
                    </div>
                </motion.div>

                <div className="space-y-5">
                    {/* Nutrition Overview */}
                    {nutritionOverview.length > 0 && (
                        <Section icon={BarChart2} title="Nutrition Overview">
                            <div className="space-y-5">
                                {nutritionOverview.map((item, i) => (
                                    <NutritionBar key={item.name} {...item} delay={i * 0.08} />
                                ))}
                            </div>
                            <p className="text-xs text-gray-600 mt-4">Values per 100g. Marker at 50% represents the recommended threshold.</p>
                        </Section>
                    )}

                    {/* Claim Breakdown */}
                    {claimBreakdown.length > 0 && (
                        <Section icon={CheckCircle2} title="Claim Breakdown">
                            <div className="space-y-3">
                                {claimBreakdown.map((item, i) => (
                                    <div
                                        key={i}
                                        className={`flex items-start gap-3 p-4 rounded-xl border ${item.passed ? 'bg-green-500/5 border-green-500/20' : 'bg-red-500/5 border-red-500/20'}`}
                                    >
                                        {item.passed
                                            ? <CheckCircle2 className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                                            : <XCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                                        }
                                        <div>
                                            <p className={`font-semibold text-sm ${item.passed ? 'text-green-300' : 'text-red-300'}`}>
                                                {item.claim}
                                            </p>
                                            <p className="text-gray-400 text-sm mt-0.5">{item.reason}</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </Section>
                    )}

                    {/* Ingredient Warnings */}
                    <Section icon={ShieldAlert} title="Ingredient Warnings">
                        {ingredientWarnings.length > 0 ? (
                            <div className="space-y-3">
                                {ingredientWarnings.map((item, i) => (
                                    <div
                                        key={i}
                                        className="flex items-start gap-3 p-4 rounded-xl bg-white/[0.02] border border-white/10"
                                    >
                                        <AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
                                        <div className="flex-1">
                                            <div className="flex flex-wrap items-center gap-2 mb-1">
                                                <span className="font-semibold text-white text-sm">{item.name}</span>
                                                <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${RISK_COLORS[item.risk] || RISK_COLORS.medium}`}>
                                                    {item.risk} risk
                                                </span>
                                            </div>
                                            {item.note && <p className="text-gray-400 text-sm">{item.note}</p>}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="flex items-center gap-3 p-4 rounded-xl bg-green-500/5 border border-green-500/20">
                                <CheckCircle2 className="w-5 h-5 text-green-400" />
                                <p className="text-green-300 text-sm font-medium">No flagged ingredients detected.</p>
                            </div>
                        )}
                    </Section>
                </div>

                {/* Disclaimer */}
                <motion.p
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.7 }}
                    className="text-center text-xs text-gray-600 mt-8 px-4"
                >
                    NutriLens results are based on OCR data extraction and may not replace professional nutritional advice. Always consult a registered dietitian for health decisions.
                </motion.p>
            </div>
        </motion.div>
    );
};

export default Results;
