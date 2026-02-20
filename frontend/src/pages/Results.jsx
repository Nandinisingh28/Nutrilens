import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
    ArrowLeft, AlertTriangle, CheckCircle, XCircle, HelpCircle,
    AlertCircle, Shield, Info, Beaker, TrendingUp, TrendingDown,
    Minus, ChevronDown, ChevronUp
} from 'lucide-react';
import VerdictBadge from '../components/VerdictBadge';
import ScoreCircle from '../components/ScoreCircle';
import { scansAPI } from '../api/client';

/* ──────────────────── helpers ──────────────────── */

const getCategoryLabel = (category) => {
    const labels = {
        PROTEIN_BAR: '🥜 Protein Bar',
        BREAKFAST_CEREAL: '🥣 Breakfast Cereal',
        BISCUITS_COOKIES: '🍪 Biscuits & Cookies',
        SNACKS: '🍿 Snacks',
        CHOCOLATES_CONFECTIONERY: '🍫 Chocolate & Confectionery',
        BEVERAGES: '🥤 Beverages',
        ENERGY_DRINKS: '⚡ Energy Drinks',
        DAIRY_PRODUCTS: '🥛 Dairy Products',
        INSTANT_NOODLES_RTE: '🍜 Instant Noodles / RTE',
        SAUCES_SPREADS: '🫙 Sauces & Spreads',
        HEALTH_SUPPLEMENTS: '💊 Health Supplements',
        FROZEN_FOODS: '🧊 Frozen Foods',
    };
    return labels[category] || category;
};

const verdictMeta = {
    TRUE: {
        bg: 'rgba(34,197,94,.12)',
        border: 'rgba(34,197,94,.40)',
        accent: '#22c55e',
        icon: CheckCircle,
        heading: 'Claim Verified ✅',
        message: 'The claim on this product is supported by the extracted nutrition and ingredient data.',
    },
    PARTIALLY_TRUE: {
        bg: 'rgba(234,179,8,.10)',
        border: 'rgba(234,179,8,.35)',
        accent: '#eab308',
        icon: AlertCircle,
        heading: 'Partially True ⚠️',
        message: 'Some aspects of the claim hold up, but not everything checks out.',
    },
    MISLEADING: {
        bg: 'rgba(249,115,22,.10)',
        border: 'rgba(249,115,22,.35)',
        accent: '#f97316',
        icon: AlertTriangle,
        heading: 'Potentially Misleading ⚠️',
        message: 'The claim appears to be misleading based on the available data. Exercise caution.',
    },
    FALSE: {
        bg: 'rgba(239,68,68,.10)',
        border: 'rgba(239,68,68,.35)',
        accent: '#ef4444',
        icon: XCircle,
        heading: 'Claim Is False ❌',
        message: 'The data contradicts this claim. The product does NOT meet the criteria.',
    },
    UNVERIFIABLE: {
        bg: 'rgba(148,163,184,.10)',
        border: 'rgba(148,163,184,.30)',
        accent: '#94a3b8',
        icon: HelpCircle,
        heading: 'Cannot Verify ❓',
        message: 'Insufficient data was extracted to fully verify or deny this claim.',
    },
};

const getVerdictInfo = (v) => verdictMeta[v] || verdictMeta.UNVERIFIABLE;

/* ──────────────  Sub-claim card colors  ────────── */

const subVerdictStyle = {
    TRUE: { bg: 'rgba(34,197,94,.08)', border: '#22c55e' },
    PARTIALLY_TRUE: { bg: 'rgba(234,179,8,.08)', border: '#eab308' },
    MISLEADING: { bg: 'rgba(249,115,22,.08)', border: '#f97316' },
    FALSE: { bg: 'rgba(239,68,68,.08)', border: '#ef4444' },
    UNVERIFIABLE: { bg: 'rgba(148,163,184,.06)', border: '#94a3b8' },
};

/* ──────────────  Nutrition bar  ────────────────── */

function NutritionBar({ label, value, unit, maxValue, color = 'var(--color-primary-500)', icon }) {
    if (value === null || value === undefined) return null;
    const pct = Math.min((value / maxValue) * 100, 100);
    const displayVal = typeof value === 'number' ? value.toFixed(1) : value;

    // Color based on percentage of max
    let barColor = color;
    if (pct > 80) barColor = '#ef4444';
    else if (pct > 60) barColor = '#f97316';
    else if (pct > 40) barColor = '#eab308';
    else barColor = '#22c55e';

    return (
        <div style={{ marginBottom: '14px' }}>
            <div style={{
                display: 'flex', justifyContent: 'space-between',
                alignItems: 'center', marginBottom: '6px'
            }}>
                <span style={{
                    fontSize: '13px', color: 'var(--color-neutral-300)',
                    display: 'flex', alignItems: 'center', gap: '6px',
                    fontWeight: 500
                }}>
                    {icon && <span style={{ fontSize: '14px' }}>{icon}</span>}
                    {label}
                </span>
                <span style={{
                    fontSize: '14px', fontWeight: 700,
                    color: 'var(--color-neutral-100)'
                }}>
                    {displayVal}<span style={{ fontSize: '11px', fontWeight: 400, color: 'var(--color-neutral-400)', marginLeft: '2px' }}>{unit}</span>
                </span>
            </div>
            <div style={{
                height: '8px', borderRadius: '4px',
                background: 'rgba(255,255,255,.06)',
                overflow: 'hidden'
            }}>
                <div style={{
                    height: '100%', borderRadius: '4px',
                    width: `${pct}%`, background: barColor,
                    transition: 'width 0.8s cubic-bezier(.4,0,.2,1)'
                }} />
            </div>
        </div>
    );
}

/* ──────────────────── main  ───────────────────── */

function Results() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [scan, setScan] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [showOcr, setShowOcr] = useState(false);
    const [showExplanation, setShowExplanation] = useState(false);

    useEffect(() => {
        (async () => {
            try {
                const response = await scansAPI.getScan(id);
                setScan(response.data);
            } catch {
                setError('Failed to load scan results');
            }
            setLoading(false);
        })();
    }, [id]);

    /* ---------- render guards ---------- */
    if (loading) {
        return (
            <div className="loading-overlay" style={{ position: 'static', minHeight: '400px' }}>
                <div className="spinner spinner-lg"></div>
                <p className="loading-text">Analysing results…</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="empty-state">
                <div className="empty-state-icon"><AlertTriangle size={80} /></div>
                <h3 className="empty-state-title">Error Loading Results</h3>
                <p className="empty-state-text">{error}</p>
                <button className="btn btn-primary" onClick={() => navigate('/dashboard')}>Back to Dashboard</button>
            </div>
        );
    }

    if (!scan) return null;

    const vi = getVerdictInfo(scan.verdict);
    const VIcon = vi.icon;
    const n = scan.nutrition || {};

    /* ──────────────────── JSX ──────────────────── */
    return (
        <div className="animate-fadeIn" style={{ maxWidth: 960, margin: '0 auto' }}>

            {/* ───── Back ───── */}
            <button className="btn btn-ghost" onClick={() => navigate('/dashboard')}
                style={{ marginBottom: '24px' }}>
                <ArrowLeft size={18} /> Back to Dashboard
            </button>

            {/* ═══════════════ VERDICT HERO CARD ═══════════════ */}
            <div style={{
                background: vi.bg,
                border: `1.5px solid ${vi.border}`,
                borderRadius: '16px',
                padding: '32px',
                marginBottom: '28px',
                position: 'relative',
                overflow: 'hidden',
            }}>
                {/* glow */}
                <div style={{
                    position: 'absolute', top: -60, right: -60,
                    width: 180, height: 180, borderRadius: '50%',
                    background: vi.accent, opacity: 0.06, filter: 'blur(40px)', pointerEvents: 'none'
                }} />

                {/* category pill */}
                <span style={{
                    display: 'inline-block',
                    fontSize: '12px', fontWeight: 600,
                    color: 'var(--color-neutral-300)',
                    background: 'rgba(255,255,255,.06)',
                    padding: '4px 12px', borderRadius: '20px',
                    marginBottom: '12px', letterSpacing: '.3px'
                }}>
                    {getCategoryLabel(scan.category)} &nbsp;•&nbsp; {scan.scan_mode} Scan
                </span>

                {/* claim */}
                <h1 style={{
                    fontSize: '26px', fontWeight: 700,
                    color: 'var(--color-neutral-50)',
                    marginBottom: '16px', lineHeight: 1.3,
                }}>
                    Claim: <span style={{ color: vi.accent }}>"{scan.user_claim}"</span>
                </h1>

                {/* verdict row */}
                <div style={{
                    display: 'flex', alignItems: 'center', gap: '14px',
                    marginBottom: '14px', flexWrap: 'wrap'
                }}>
                    <VIcon size={32} color={vi.accent} />
                    <span style={{
                        fontSize: '22px', fontWeight: 800,
                        color: vi.accent, letterSpacing: '.3px',
                    }}>
                        {vi.heading}
                    </span>
                </div>

                <p style={{
                    fontSize: '15px', color: 'var(--color-neutral-300)',
                    lineHeight: 1.7, maxWidth: 600
                }}>
                    {vi.message}
                </p>
            </div>

            {/* ═══════════════ SCORES ROW ═══════════════ */}
            <div style={{
                display: 'grid',
                gridTemplateColumns: scan.health_score != null ? '1fr 1fr' : '1fr',
                gap: '20px',
                marginBottom: '28px'
            }}>
                {/* Verification Score */}
                <div className="results-section" style={{ textAlign: 'center', padding: '28px 20px' }}>
                    <h3 style={{
                        fontSize: '14px', fontWeight: 600,
                        color: 'var(--color-neutral-400)',
                        marginBottom: '16px', textTransform: 'uppercase', letterSpacing: '1px'
                    }}>Verification Score</h3>
                    <div style={{ display: 'flex', justifyContent: 'center' }}>
                        <ScoreCircle score={scan.score} size={140} />
                    </div>
                    <p style={{
                        fontSize: '12px', color: 'var(--color-neutral-500)',
                        marginTop: '10px'
                    }}>
                        How well the claim matches extracted data
                    </p>
                </div>

                {/* Health Score */}
                {scan.health_score != null && (
                    <div className="results-section" style={{ textAlign: 'center', padding: '28px 20px' }}>
                        <h3 style={{
                            fontSize: '14px', fontWeight: 600,
                            color: 'var(--color-neutral-400)',
                            marginBottom: '16px', textTransform: 'uppercase', letterSpacing: '1px'
                        }}>Health Score</h3>
                        <div style={{ display: 'flex', justifyContent: 'center' }}>
                            <ScoreCircle score={scan.health_score} size={140} color="var(--color-info)" label="Health" />
                        </div>
                        <p style={{
                            fontSize: '12px', color: 'var(--color-neutral-500)',
                            marginTop: '10px'
                        }}>
                            Overall nutritional quality (0-100)
                        </p>
                    </div>
                )}
            </div>

            {/* ═══════════════ CLAIM BREAKDOWN ═══════════════ */}
            {scan.sub_claims && scan.sub_claims.length > 0 && (
                <div className="results-section" style={{ marginBottom: '28px', padding: '28px' }}>
                    <h3 style={{
                        fontSize: '16px', fontWeight: 700,
                        color: 'var(--color-neutral-100)',
                        marginBottom: '20px',
                        display: 'flex', alignItems: 'center', gap: '10px'
                    }}>
                        <Shield size={20} color="var(--color-primary-400)" />
                        Claim Breakdown
                    </h3>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                        {scan.sub_claims.map((sc, idx) => {
                            const svs = subVerdictStyle[sc.verdict] || subVerdictStyle.UNVERIFIABLE;
                            const SubIcon = verdictMeta[sc.verdict]?.icon || HelpCircle;
                            return (
                                <div key={idx} style={{
                                    background: svs.bg,
                                    borderLeft: `4px solid ${svs.border}`,
                                    borderRadius: '10px',
                                    padding: '16px 20px',
                                    transition: 'transform .15s ease',
                                }}>
                                    <div style={{
                                        display: 'flex', alignItems: 'flex-start',
                                        gap: '12px'
                                    }}>
                                        <SubIcon size={22} color={svs.border} style={{ marginTop: 2, flexShrink: 0 }} />
                                        <div style={{ flex: 1 }}>
                                            <div style={{
                                                display: 'flex', alignItems: 'center',
                                                gap: '10px', flexWrap: 'wrap', marginBottom: '6px'
                                            }}>
                                                <span style={{
                                                    fontSize: '15px', fontWeight: 700,
                                                    color: 'var(--color-neutral-100)'
                                                }}>
                                                    {sc.sub_claim || sc.claim_type?.replace(/_/g, ' ')}
                                                </span>
                                                <VerdictBadge verdict={sc.verdict} />
                                            </div>
                                            <p style={{
                                                fontSize: '13px', lineHeight: 1.6,
                                                color: 'var(--color-neutral-300)', margin: 0
                                            }}>
                                                {sc.reason}
                                            </p>

                                            {/* Show actual vs threshold if available */}
                                            {sc.actual_value && (
                                                <div style={{
                                                    marginTop: '10px',
                                                    display: 'flex', gap: '16px', flexWrap: 'wrap'
                                                }}>
                                                    <span style={{
                                                        fontSize: '12px', color: 'var(--color-neutral-400)',
                                                        background: 'rgba(255,255,255,.04)',
                                                        padding: '4px 10px', borderRadius: '6px'
                                                    }}>
                                                        <strong style={{ color: 'var(--color-neutral-200)' }}>Actual:</strong> {sc.actual_value}
                                                    </span>
                                                    {sc.threshold_value && (
                                                        <span style={{
                                                            fontSize: '12px', color: 'var(--color-neutral-400)',
                                                            background: 'rgba(255,255,255,.04)',
                                                            padding: '4px 10px', borderRadius: '6px'
                                                        }}>
                                                            <strong style={{ color: 'var(--color-neutral-200)' }}>Threshold:</strong> {sc.threshold_value}
                                                        </span>
                                                    )}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}

            {/* ═══════════════ NUTRITION OVERVIEW ═══════════════ */}
            {scan.nutrition && (
                <div className="results-section" style={{ marginBottom: '28px', padding: '28px' }}>
                    <h3 style={{
                        fontSize: '16px', fontWeight: 700,
                        color: 'var(--color-neutral-100)',
                        marginBottom: '20px',
                        display: 'flex', alignItems: 'center', gap: '10px'
                    }}>
                        📊 Nutrition Overview <span style={{
                            fontSize: '12px', fontWeight: 400,
                            color: 'var(--color-neutral-500)'
                        }}>(per 100g)</span>
                    </h3>
                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                        gap: '24px'
                    }}>
                        <div>
                            <NutritionBar label="Protein" value={n.protein} unit="g" maxValue={30} icon="🥩" />
                            <NutritionBar label="Sugar" value={n.sugar} unit="g" maxValue={40} icon="🍬" />
                            <NutritionBar label="Fat" value={n.fat} unit="g" maxValue={30} icon="🧈" />
                        </div>
                        <div>
                            <NutritionBar label="Fiber" value={n.fiber} unit="g" maxValue={15} icon="🌾" />
                            <NutritionBar label="Calories" value={n.calories} unit="kcal" maxValue={550} icon="🔥" />
                            <NutritionBar label="Sodium" value={n.sodium} unit="mg" maxValue={800} icon="🧂" />
                        </div>
                    </div>
                </div>
            )}

            {/* ═══════════════ INGREDIENT WARNINGS ═══════════════ */}
            {scan.ingredient_warnings && scan.ingredient_warnings.length > 0 && (
                <div className="results-section" style={{ marginBottom: '28px', padding: '28px' }}>
                    <h3 style={{
                        fontSize: '16px', fontWeight: 700,
                        color: 'var(--color-misleading)',
                        marginBottom: '16px',
                        display: 'flex', alignItems: 'center', gap: '10px'
                    }}>
                        <AlertTriangle size={20} />
                        Ingredient Warnings ({scan.ingredient_warnings.length})
                    </h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        {scan.ingredient_warnings.map((w, idx) => (
                            <div key={idx} style={{
                                padding: '12px 16px',
                                background: 'rgba(249,115,22,.08)',
                                borderLeft: '3px solid #f97316',
                                borderRadius: '8px',
                                fontSize: '13px', color: '#fbbf24', lineHeight: 1.5
                            }}>
                                {w}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* ═══════════════ WHAT THIS MEANS ═══════════════ */}
            <div className="results-section" style={{
                marginBottom: '28px', padding: '28px',
                background: 'rgba(59,130,246,.06)',
                border: '1px solid rgba(59,130,246,.15)',
            }}>
                <h3 style={{
                    fontSize: '16px', fontWeight: 700,
                    color: 'var(--color-info)',
                    marginBottom: '14px',
                    display: 'flex', alignItems: 'center', gap: '10px'
                }}>
                    <Info size={20} /> What This Means
                </h3>
                <p style={{
                    fontSize: '14px', lineHeight: 1.8,
                    color: 'var(--color-neutral-300)', margin: 0
                }}>
                    {scan.verdict === 'TRUE' &&
                        'Great news! The claim on this product is backed by its nutrition facts and ingredients list. You can trust this claim based on the data we extracted from the label.'}
                    {scan.verdict === 'PARTIALLY_TRUE' &&
                        'This product partially meets the criteria for the claim. While some aspects check out, others don\'t fully align. Consider looking at the specific breakdown above to understand which parts of the claim hold true.'}
                    {scan.verdict === 'MISLEADING' &&
                        'The data suggests this claim is misleading. The product may use technically correct language but the overall impression it creates may not match reality. Review the claim breakdown above for specifics.'}
                    {scan.verdict === 'FALSE' &&
                        'The extracted data directly contradicts this claim. The product does NOT meet the required criteria. This could be an exaggerated or false marketing claim. Review the detailed breakdown above to see exactly why.'}
                    {scan.verdict === 'UNVERIFIABLE' &&
                        'We could not extract enough data from the label images to verify or deny this claim. This could be due to image quality, OCR limitations, or the claim requiring data not present on the label (like certifications). Try uploading clearer images.'}
                </p>
            </div>

            {/* ═══════════════ DETAILED EXPLANATION ═══════════════ */}
            {scan.explanation && (
                <div className="results-section" style={{ marginBottom: '28px', padding: '28px' }}>
                    <h3 style={{
                        fontSize: '16px', fontWeight: 700,
                        color: 'var(--color-neutral-100)',
                        marginBottom: '20px',
                        display: 'flex', alignItems: 'center', gap: '10px'
                    }}>
                        📝 Detailed Explanation
                    </h3>
                    <div style={{
                        color: 'var(--color-neutral-300)',
                        fontSize: '13px', lineHeight: 1.8
                    }}>
                        {scan.explanation.split('\n').map((line, idx) => {
                            const parsedLine = line.replace(
                                /\*\*([^*]+)\*\*/g,
                                '<strong style="color:var(--color-neutral-100);font-weight:600">$1</strong>'
                            );
                            if (line.trim().startsWith('•') || line.trim().startsWith('-'))
                                return <div key={idx} style={{ paddingLeft: '16px', marginBottom: '4px' }} dangerouslySetInnerHTML={{ __html: parsedLine }} />;
                            if (line.match(/^[✅❌⚠️❓🟡]/))
                                return <div key={idx} style={{ padding: '10px 14px', marginBottom: '8px', background: 'rgba(255,255,255,.03)', borderRadius: '8px', borderLeft: '3px solid var(--color-primary-500)' }} dangerouslySetInnerHTML={{ __html: parsedLine }} />;
                            if (line.trim() === '') return <div key={idx} style={{ height: '12px' }} />;
                            return <div key={idx} style={{ marginBottom: '6px' }} dangerouslySetInnerHTML={{ __html: parsedLine }} />;
                        })}
                    </div>
                </div>
            )}

            {/* ═══════════════ OCR DEBUG (collapsible) ═══════════════ */}
            {(scan.ocr_nutrition_text || scan.ocr_ingredients_text) && (
                <div className="results-section" style={{ marginBottom: '28px', padding: 0, overflow: 'hidden' }}>
                    <button
                        onClick={() => setShowOcr(!showOcr)}
                        style={{
                            width: '100%', display: 'flex', alignItems: 'center',
                            justifyContent: 'space-between',
                            padding: '20px 28px',
                            background: 'transparent', border: 'none',
                            cursor: 'pointer', color: 'var(--color-neutral-400)',
                            fontSize: '14px', fontWeight: 500
                        }}
                    >
                        <span style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                            🔍 OCR Debug — Extracted Text
                        </span>
                        {showOcr ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                    </button>
                    {showOcr && (
                        <div style={{ padding: '0 28px 24px' }}>
                            {scan.ocr_nutrition_text && (
                                <div style={{ marginBottom: '16px' }}>
                                    <h4 style={{ color: 'var(--color-primary-400)', marginBottom: '8px', fontSize: '13px' }}>📊 Nutrition Label Text:</h4>
                                    <textarea readOnly value={scan.ocr_nutrition_text} style={{
                                        width: '100%', minHeight: '120px', padding: '12px',
                                        background: 'var(--color-neutral-900)', border: '1px solid var(--color-neutral-700)',
                                        borderRadius: '8px', color: 'var(--color-neutral-200)',
                                        fontSize: '12px', fontFamily: 'monospace', resize: 'vertical'
                                    }} />
                                </div>
                            )}
                            {scan.ocr_ingredients_text && (
                                <div>
                                    <h4 style={{ color: 'var(--color-secondary-400)', marginBottom: '8px', fontSize: '13px' }}>🧪 Ingredients Text:</h4>
                                    <textarea readOnly value={scan.ocr_ingredients_text} style={{
                                        width: '100%', minHeight: '120px', padding: '12px',
                                        background: 'var(--color-neutral-900)', border: '1px solid var(--color-neutral-700)',
                                        borderRadius: '8px', color: 'var(--color-neutral-200)',
                                        fontSize: '12px', fontFamily: 'monospace', resize: 'vertical'
                                    }} />
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}

            {/* ═══════════════ ACTIONS ═══════════════ */}
            <div style={{
                display: 'flex', justifyContent: 'center',
                gap: '16px', marginTop: '12px', marginBottom: '32px', flexWrap: 'wrap'
            }}>
                <button className="btn btn-primary" onClick={() => navigate('/dashboard')}>
                    Scan Another Product
                </button>
                <button className="btn btn-secondary" onClick={() => navigate('/history')}>
                    View History
                </button>
            </div>
        </div>
    );
}

export default Results;
