import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
    ArrowLeft, AlertTriangle, CheckCircle, XCircle, HelpCircle,
    AlertCircle, Shield, Info, ChevronDown, ChevronUp, Lightbulb, Star,
    Search, BarChart3, FlaskConical, ClipboardList
} from 'lucide-react';
import VerdictBadge from '../components/VerdictBadge';
import ScoreCircle from '../components/ScoreCircle';
import { scansAPI } from '../api/client';
import {
    getCategoryLabel, getCategoryIcon, NUTRITION_ICONS,
    getHealthRating, HEALTH_FACTORS, ProhibitedIcon, SwitchToIcon
} from '../utils/icons';

/* ──────────────────── helpers ──────────────────── */


/* Ingredient alternative suggestions */
const INGREDIENT_ALTERNATIVES = {
    /* ── Artificial Sweeteners ── */
    'aspartame': { why: 'Controversial artificial sweetener linked to headaches in some people.', alt: 'Stevia, Monk Fruit, or Erythritol' },
    'sucralose': { why: 'Artificial sweetener that may alter gut bacteria.', alt: 'Stevia or Monk Fruit extract' },
    'saccharin': { why: 'Oldest artificial sweetener; some studies raise concerns.', alt: 'Stevia, Date Sugar, or Coconut Sugar' },
    'acesulfame': { why: 'Often used with other sweeteners; limited long-term human data.', alt: 'Stevia or Erythritol' },
    'ins 950': { why: 'Acesulfame Potassium — artificial sweetener with limited long-term data.', alt: 'Stevia (INS 960) or Jaggery' },
    'ins 951': { why: 'Aspartame — controversial artificial sweetener.', alt: 'Stevia (INS 960) or Raw Honey' },
    'ins 955': { why: 'Sucralose — artificial sweetener that may affect gut microbiome.', alt: 'Stevia or Coconut Sugar' },
    'ins 954': { why: 'Saccharin — one of the oldest artificial sweeteners with mixed safety data.', alt: 'Stevia or Date Palm Sugar (Khajoor)' },

    /* ── Processed Sugars ── */
    'high fructose corn syrup': { why: 'Rapidly metabolised fructose linked to insulin resistance.', alt: 'Raw Honey, Maple Syrup, or Coconut Sugar' },
    'corn syrup': { why: 'Highly processed added sugar with no nutritional value.', alt: 'Medjool Date Paste or Brown Rice Syrup' },
    'maltodextrin': { why: 'High glycemic index carbohydrate that spikes blood sugar.', alt: 'Tapioca Starch or Arrowroot Powder' },
    'invert sugar': { why: 'Processed sugar syrup; essentially liquid sugar with no nutrients.', alt: 'Jaggery (Gur), Honey, or Coconut Sugar' },
    'liquid glucose': { why: 'Refined simple sugar with extremely high glycemic index.', alt: 'Date Syrup or Rice Malt Syrup' },
    'dextrose': { why: 'Pure glucose derived from corn; spikes blood sugar rapidly.', alt: 'Coconut Sugar or Jaggery' },

    /* ── Preservatives ── */
    'sodium benzoate': { why: 'Preservative that can form benzene (a carcinogen) with Vitamin C.', alt: 'Rosemary Extract (natural preservative)' },
    'potassium sorbate': { why: 'Preservative that may cause allergic reactions in sensitive individuals.', alt: 'Vitamin E (natural antioxidant)' },
    'bha': { why: 'Possible carcinogen at high doses; banned in some countries.', alt: 'Mixed Tocopherols (Vitamin E)' },
    'bht': { why: 'Synthetic antioxidant preservative, potential endocrine disruptor.', alt: 'Rosemary Extract or Ascorbic Acid' },
    'ins 211': { why: 'Sodium Benzoate — can form benzene with Vitamin C (INS 300).', alt: 'Rosemary Extract or Citric Acid' },
    'ins 202': { why: 'Potassium Sorbate — may cause skin/allergic reactions in sensitive people.', alt: 'Vitamin E (Tocopherol) or Neem Extract' },
    'ins 320': { why: 'BHA — synthetic antioxidant; possible carcinogen.', alt: 'Mixed Tocopherols (Vitamin E)' },
    'ins 321': { why: 'BHT — synthetic antioxidant; potential endocrine disruptor.', alt: 'Rosemary Extract or Ascorbic Acid' },
    'ins 223': { why: 'Sodium Metabisulphite — can trigger asthma and allergic reactions.', alt: 'Ascorbic Acid (Vitamin C)' },
    'ins 220': { why: 'Sulphur Dioxide — irritant; can trigger asthma in sensitive individuals.', alt: 'Citric Acid or Ascorbic Acid' },
    'sodium nitrite': { why: 'Used in processed meats; can form carcinogenic nitrosamines.', alt: 'Celery Powder or Sea Salt' },
    'tbhq': { why: 'Synthetic preservative; may cause nausea and vision issues at high doses.', alt: 'Rosemary Extract or Vitamin E' },

    /* ── Artificial Colors / Dyes ── */
    'red 40': { why: 'Artificial dye linked to hyperactivity in children.', alt: 'Beet Juice or Lycopene (natural red)' },
    'yellow 5': { why: 'Artificial dye (Tartrazine) linked to hyperactivity; banned in some EU products.', alt: 'Turmeric Extract or Beta-Carotene' },
    'tartrazine': { why: 'Artificial dye linked to hyperactivity; banned/restricted in several countries.', alt: 'Turmeric or Annatto Extract' },
    'ins 102': { why: 'Tartrazine (Yellow 5) — linked to hyperactivity and allergic reactions.', alt: 'Turmeric Extract or Saffron' },
    'ins 110': { why: 'Sunset Yellow — artificial dye linked to hyperactivity in children.', alt: 'Carrot or Pumpkin Extract' },
    'ins 129': { why: 'Allura Red — artificial dye; may cause allergic reactions.', alt: 'Beetroot Powder or Pomegranate Extract' },
    'ins 133': { why: 'Brilliant Blue — synthetic dye; rarely used in natural foods.', alt: 'Spirulina Extract or Butterfly Pea Flower' },
    'ins 127': { why: 'Erythrosine (Red 3) — restricted in some countries for thyroid concerns.', alt: 'Beetroot or Hibiscus Extract' },
    'ins 150': { why: 'Caramel Color — some variants (Class III/IV) may contain carcinogenic 4-MEI.', alt: 'Molasses or Date Syrup for natural color' },
    'caramel color': { why: 'Some manufacturing processes create potentially carcinogenic 4-MEI compound.', alt: 'Molasses, Cocoa Powder, or Date Syrup' },

    /* ── Unhealthy Fats & Oils (Indian-specific) ── */
    'partially hydrogenated': { why: 'Source of trans fats, strongly linked to heart disease.', alt: 'Cold-pressed Coconut Oil or Olive Oil' },
    'palm oil': { why: 'High saturated fat; environmental concerns around palm deforestation.', alt: 'Sunflower Oil or Cold-pressed Coconut Oil' },
    'palmolein oil': { why: 'High saturated fat; environmental concerns around palm deforestation.', alt: 'Sunflower Oil, Rice Bran Oil, or Olive Oil' },
    'vanaspati': { why: 'Hydrogenated vegetable fat (Indian dalda); major source of trans fats.', alt: 'Desi Ghee, Coconut Oil, or Mustard Oil' },
    'dalda': { why: 'Hydrogenated fat (vanaspati); contains harmful trans fats linked to heart disease.', alt: 'Pure Desi Ghee or Cold-pressed Groundnut Oil' },
    'hydrogenated vegetable oil': { why: 'Contains trans fats created during hydrogenation; raises LDL cholesterol.', alt: 'Desi Ghee, Olive Oil, or Rice Bran Oil' },
    'interesterified fat': { why: 'Chemically modified fat; emerging concerns about metabolic effects.', alt: 'Cold-pressed Coconut Oil or Desi Ghee' },
    'shortening': { why: 'Usually made from hydrogenated oils; source of trans fats.', alt: 'Butter, Desi Ghee, or Coconut Oil' },

    /* ── Refined Flour ── */
    'maida': { why: 'Refined white flour stripped of fiber and nutrients; high glycemic index.', alt: 'Whole Wheat Atta, Ragi Flour, or Jowar Flour' },
    'refined wheat flour': { why: 'Bleached and stripped of bran/germ; spikes blood sugar.', alt: 'Whole Wheat Flour, Multigrain Atta, or Besan' },

    /* ── Flavor Enhancers ── */
    'monosodium glutamate': { why: 'Flavour enhancer that can cause sensitivity in some people.', alt: 'Nutritional Yeast or Mushroom Powder' },
    'msg': { why: 'Flavour enhancer; some people report headaches or flushing.', alt: 'Nutritional Yeast or Natural Umami (e.g., Tomato Powder)' },
    'ajinomoto': { why: 'Brand name for MSG; can cause "Chinese restaurant syndrome" in sensitive people.', alt: 'Mushroom Powder, Nutritional Yeast, or Dried Tomato' },
    'ins 621': { why: 'Monosodium Glutamate (MSG) — flavour enhancer causing sensitivity in some.', alt: 'Nutritional Yeast, Mushroom Powder, or Kasuri Methi' },
    'ins 627': { why: 'Disodium Guanylate — often used with MSG; amplifies umami flavour.', alt: 'Sun-dried Tomato Powder or Mushroom Extract' },
    'ins 631': { why: 'Disodium Inosinate — MSG booster; usually derived from animal sources.', alt: 'Seaweed Flakes (Nori) or Nutritional Yeast' },
    'ins 635': { why: 'Disodium 5-Ribonucleotides — synthetic flavour enhancer blend.', alt: 'Natural Umami: Soy Sauce, Miso, or Mushroom Powder' },

    /* ── Emulsifiers & Thickeners ── */
    'ins 322': { why: 'Soy Lecithin — usually from GMO soy; allergen risk for soy-sensitive people.', alt: 'Sunflower Lecithin' },
    'ins 407': { why: 'Carrageenan — linked to intestinal inflammation in animal studies.', alt: 'Guar Gum (INS 412) or Agar-Agar' },
    'carrageenan': { why: 'Seaweed-derived thickener linked to gut inflammation in studies.', alt: 'Agar-Agar, Guar Gum, or Xanthan Gum' },
    'polysorbate 80': { why: 'Synthetic emulsifier; may disrupt gut barrier in some studies.', alt: 'Sunflower Lecithin or Gum Arabic' },
    'ins 433': { why: 'Polysorbate 80 — synthetic emulsifier with emerging gut health concerns.', alt: 'Sunflower Lecithin or Acacia Gum' },

    /* ── Other Additives ── */
    'sodium caseinate': { why: 'Processed milk protein; hidden dairy allergen in "non-dairy" products.', alt: 'Pea Protein or Almond Protein' },
    'titanium dioxide': { why: 'White colorant (INS 171); banned in EU since 2022 due to genotoxicity concerns.', alt: 'Rice Starch or Calcium Carbonate for whitening' },
    'ins 171': { why: 'Titanium Dioxide — banned in EU foods since 2022 over safety concerns.', alt: 'Rice Flour or Calcium Carbonate' },
    'potassium bromate': { why: 'Flour improver classified as possibly carcinogenic; banned in many countries.', alt: 'Ascorbic Acid (Vitamin C) as dough improver' },
};

const verdictMeta = {
    TRUE: { bg: 'rgba(34,197,94,.10)', border: 'rgba(34,197,94,.35)', accent: '#22c55e', icon: CheckCircle, heading: 'Claim Verified', message: 'The claim on this product is supported by the nutrition facts and ingredient data we extracted.' },
    PARTIALLY_TRUE: { bg: 'rgba(234,179,8,.10)', border: 'rgba(234,179,8,.35)', accent: '#eab308', icon: AlertCircle, heading: 'Partially True', message: 'Some parts of the claim check out, but not everything. See the breakdown below.' },
    MISLEADING: { bg: 'rgba(249,115,22,.10)', border: 'rgba(249,115,22,.35)', accent: '#f97316', icon: AlertTriangle, heading: 'Potentially Misleading', message: 'The claim appears misleading based on the available data. Exercise caution.' },
    FALSE: { bg: 'rgba(239,68,68,.10)', border: 'rgba(239,68,68,.35)', accent: '#ef4444', icon: XCircle, heading: 'Claim Is False', message: 'The data directly contradicts this claim. The product does NOT meet the criteria.' },
    UNVERIFIABLE: { bg: 'rgba(148,163,184,.10)', border: 'rgba(148,163,184,.30)', accent: '#94a3b8', icon: HelpCircle, heading: 'Cannot Verify', message: 'Insufficient data was extracted to verify or deny this claim. Try a clearer photo.' },
};

const subVerdictStyle = {
    TRUE: { bg: 'rgba(34,197,94,.06)', border: '#22c55e' },
    PARTIALLY_TRUE: { bg: 'rgba(234,179,8,.06)', border: '#eab308' },
    MISLEADING: { bg: 'rgba(249,115,22,.06)', border: '#f97316' },
    FALSE: { bg: 'rgba(239,68,68,.06)', border: '#ef4444' },
    UNVERIFIABLE: { bg: 'rgba(148,163,184,.05)', border: '#94a3b8' },
};

const getVerdictInfo = (v) => verdictMeta[v] || verdictMeta.UNVERIFIABLE;

/* ──────────── Nutrition Row (table-style) ──────────────── */
function NutritionRow({ label, value, unit, maxValue, icon, highlight }) {
    if (value === null || value === undefined) return null;
    const pct = Math.min((value / maxValue) * 100, 100);
    const displayVal = typeof value === 'number' ? value.toFixed(1) : value;
    const valColor = pct > 80 ? '#ef4444' : pct > 60 ? '#f97316' : pct > 35 ? '#eab308' : '#22c55e';

    return (
        <div style={{
            display: 'grid', gridTemplateColumns: '1fr auto 1fr',
            alignItems: 'center', padding: '10px 0',
            borderBottom: '1px solid rgba(255,255,255,.04)',
        }}>
            <span style={{ fontSize: 13, color: highlight ? 'var(--color-neutral-100)' : 'var(--color-neutral-300)', display: 'flex', alignItems: 'center', gap: 8, fontWeight: highlight ? 600 : 400 }}>
                <span style={{ width: 22, textAlign: 'center', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    {typeof icon === 'function' || typeof icon === 'object' ? (() => { const I = icon; return <I size={15} />; })() : <span style={{ fontSize: 15 }}>{icon}</span>}
                </span>
                {label}
            </span>
            <span style={{
                fontSize: 14, fontWeight: 700, color: 'var(--color-neutral-50)',
                background: `${valColor}18`, border: `1px solid ${valColor}40`,
                padding: '3px 12px', borderRadius: 8, minWidth: 70, textAlign: 'center',
            }}>
                {displayVal}<span style={{ fontSize: 10, fontWeight: 400, color: 'var(--color-neutral-400)', marginLeft: 2 }}>{unit}</span>
            </span>
            <div style={{ paddingLeft: 16 }}>
                <div style={{ height: 6, borderRadius: 3, background: 'rgba(255,255,255,.06)', overflow: 'hidden' }}>
                    <div style={{ height: '100%', borderRadius: 3, width: `${pct}%`, background: `linear-gradient(90deg, ${valColor}99, ${valColor})`, transition: 'width 0.8s cubic-bezier(.4,0,.2,1)' }} />
                </div>
            </div>
        </div>
    );
}

/* ──── Nutrition Section Divider ────── */
function NutritionDivider({ label }) {
    return (
        <div style={{ paddingTop: 14, paddingBottom: 6 }}>
            <span style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1.5, color: 'var(--color-neutral-500)' }}>{label}</span>
        </div>
    );
}

/* ──────────── Health Score Breakdown ──────────────── */
function HealthScoreBreakdown({ score, verdict }) {
    const [open, setOpen] = useState(false);

    const isUnverifiable = verdict === 'UNVERIFIABLE';
    const rating = isUnverifiable
        ? { label: 'Insufficient Data', color: '#6b7280', Icon: HelpCircle }
        : getHealthRating(score);
    const RatingIcon = rating.Icon;

    return (
        <div style={{ marginTop: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6 }}>
                <span style={{ fontSize: 13, color: 'var(--color-neutral-400)', whiteSpace: 'nowrap' }}>Nutritional Quality Rating:</span>
                <span style={{ fontSize: 15, fontWeight: 700, color: rating.color, display: 'inline-flex', alignItems: 'center', gap: 4, whiteSpace: 'nowrap' }}><RatingIcon size={16} /> {rating.label}</span>
                <button onClick={() => setOpen(!open)} style={{
                    background: 'rgba(255,255,255,.06)', border: '1px solid rgba(255,255,255,.10)',
                    borderRadius: 8, padding: '6px 14px', cursor: 'pointer',
                    color: 'var(--color-neutral-300)', fontSize: 12,
                    display: 'inline-flex', alignItems: 'center', gap: 6,
                    marginLeft: 8, whiteSpace: 'nowrap'
                }}>
                    {open ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                    How is this calculated?
                </button>
            </div>

            {open && (
                <div style={{ marginTop: 14, padding: '16px 18px', background: 'rgba(255,255,255,.03)', borderRadius: 10, border: '1px solid rgba(255,255,255,.08)' }}>
                    <p style={{ fontSize: 12, color: 'var(--color-neutral-400)', marginBottom: 12 }}>
                        The Health Score starts at <strong style={{ color: 'var(--color-neutral-200)' }}>50 (neutral)</strong> and adjusts up or down based on the following factors:
                    </p>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 8 }}>
                        {HEALTH_FACTORS.map((f, i) => {
                            const FIcon = f.Icon;
                            return (
                                <div key={i} style={{ display: 'flex', gap: 10, alignItems: 'flex-start', padding: '8px 12px', background: 'rgba(255,255,255,.03)', borderRadius: 8 }}>
                                    <span style={{ marginTop: 2 }}><FIcon size={16} /></span>
                                    <div>
                                        <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--color-neutral-200)' }}>{f.label}</div>
                                        <div style={{ fontSize: 11, color: 'var(--color-neutral-500)', marginTop: 2 }}>{f.effect}</div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                    <p style={{ fontSize: 11, color: 'var(--color-neutral-600)', marginTop: 12 }}>
                        * Score is further adjusted based on the product category. E.g., chocolates are benchmarked differently than protein bars.
                    </p>
                </div>
            )}
        </div>
    );
}

/* ──────────── Ingredient Alternative Card ──────────────── */
function IngredientAlternatives({ warnings }) {
    if (!warnings || warnings.length === 0) return null;

    // Match warnings against alternatives database
    const alts = [];
    for (const w of warnings) {
        const wLower = w.toLowerCase();
        for (const [key, data] of Object.entries(INGREDIENT_ALTERNATIVES)) {
            if (wLower.includes(key) && !alts.find(a => a.key === key)) {
                alts.push({ key, name: key.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' '), ...data });
            }
        }
    }

    if (alts.length === 0) return null;

    return (
        <div className="results-section" style={{ marginBottom: 24, padding: '28px 32px' }}>
            <h3 style={{ fontSize: 16, fontWeight: 700, color: '#fbbf24', marginBottom: 6, display: 'flex', alignItems: 'center', gap: 10 }}>
                <Lightbulb size={20} color="#fbbf24" />
                Healthier Alternatives
                <span style={{ fontSize: 11, fontWeight: 500, color: 'var(--color-neutral-500)', background: 'rgba(251,191,36,.10)', padding: '2px 10px', borderRadius: 10 }}>
                    {alts.length} found
                </span>
            </h3>
            <p style={{ fontSize: 12, color: 'var(--color-neutral-500)', marginBottom: 18, lineHeight: 1.5 }}>
                These ingredients have healthier substitutes you can look for when choosing products:
            </p>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: 12 }}>
                {alts.map((alt, idx) => (
                    <div key={idx} style={{
                        background: 'rgba(255,255,255,.02)',
                        border: '1px solid rgba(255,255,255,.06)',
                        borderRadius: 14, padding: 0, overflow: 'hidden',
                    }}>
                        {/* Flagged ingredient */}
                        <div style={{ padding: '14px 18px', borderBottom: '1px solid rgba(251,191,36,.10)', background: 'rgba(251,191,36,.04)' }}>
                            <div style={{ fontSize: 13, fontWeight: 700, color: '#fbbf24', marginBottom: 4, display: 'flex', alignItems: 'center', gap: 6 }}>
                                <span style={{ display: 'inline-flex', alignItems: 'center' }}><ProhibitedIcon size={15} /></span> {alt.name}
                            </div>
                            <div style={{ fontSize: 11.5, color: 'var(--color-neutral-400)', lineHeight: 1.5 }}>
                                {alt.why}
                            </div>
                        </div>
                        {/* Better alternative */}
                        <div style={{ padding: '12px 18px', background: 'rgba(34,197,94,.03)' }}>
                            <div style={{ fontSize: 9, fontWeight: 700, color: '#4ade80', textTransform: 'uppercase', letterSpacing: 1.2, marginBottom: 4 }}>
                                <SwitchToIcon size={12} style={{ display: 'inline', marginRight: 2 }} /> Switch to
                            </div>
                            <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--color-neutral-100)' }}>
                                {alt.alt}
                            </div>
                        </div>
                    </div>
                ))}
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

    if (loading) {
        return (
            <div className="loading-overlay" style={{ position: 'static', minHeight: 400 }}>
                <div className="spinner spinner-lg" />
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

    return (
        <div className="animate-fadeIn" style={{ maxWidth: 960, margin: '0 auto' }}>

            {/* ───── Back ───── */}
            <button className="btn btn-ghost" onClick={() => navigate('/dashboard')} style={{ marginBottom: 24 }}>
                <ArrowLeft size={18} /> Back to Dashboard
            </button>

            {/* ═══ VERDICT HERO ═══ */}
            <div style={{
                background: vi.bg, border: `1.5px solid ${vi.border}`,
                borderRadius: 20, padding: '32px 36px', marginBottom: 24,
                position: 'relative', overflow: 'hidden',
            }}>
                <div style={{ position: 'absolute', top: -60, right: -60, width: 200, height: 200, borderRadius: '50%', background: vi.accent, opacity: 0.05, filter: 'blur(50px)', pointerEvents: 'none' }} />

                <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12, marginBottom: 16 }}>
                    <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--color-neutral-400)', background: 'rgba(255,255,255,.06)', padding: '4px 12px', borderRadius: 20, letterSpacing: '.3px' }}>
                        {getCategoryLabel(scan.category)} &nbsp;•&nbsp; {scan.scan_mode} Scan
                    </span>
                </div>

                <h1 style={{ fontSize: 24, fontWeight: 700, color: 'var(--color-neutral-50)', marginBottom: 16, lineHeight: 1.3 }}>
                    Verified Claim: <span style={{ color: vi.accent }}>"{scan.user_claim}"</span>
                </h1>

                <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 12 }}>
                    <VIcon size={32} color={vi.accent} />
                    <span style={{ fontSize: 22, fontWeight: 800, color: vi.accent }}>{vi.heading}</span>
                </div>

                <p style={{ fontSize: 14, color: 'var(--color-neutral-300)', lineHeight: 1.7, maxWidth: 620 }}>
                    {vi.message}
                </p>
            </div>

            {/* ═══ SCORES ROW ═══ */}
            <div style={{ display: 'grid', gridTemplateColumns: scan.health_score != null ? '1fr 1fr' : '1fr', gap: 20, marginBottom: 24 }}>
                {/* Verification score */}
                <div className="results-section" style={{ textAlign: 'center', padding: '28px 20px' }}>
                    <h3 style={{ fontSize: 13, fontWeight: 600, color: 'var(--color-neutral-400)', marginBottom: 14, textTransform: 'uppercase', letterSpacing: 1 }}>
                        Claim Verification Score
                    </h3>
                    <div style={{ display: 'flex', justifyContent: 'center' }}>
                        <ScoreCircle score={scan.score} size={130} />
                    </div>
                    <p style={{ fontSize: 12, color: 'var(--color-neutral-500)', marginTop: 10 }}>
                        How well the claim matches extracted nutrition data
                    </p>
                </div>

                {/* Health score */}
                {scan.health_score != null && (
                    <div className="results-section" style={{ padding: '28px 20px' }}>
                        <h3 style={{ fontSize: 13, fontWeight: 600, color: 'var(--color-neutral-400)', marginBottom: 14, textTransform: 'uppercase', letterSpacing: 1, textAlign: 'center' }}>
                            Overall Health Score
                        </h3>
                        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 4 }}>
                            <ScoreCircle score={scan.health_score} size={130} color="var(--color-info)" label="Health" />
                        </div>
                        <HealthScoreBreakdown score={scan.health_score} verdict={scan.verdict} />
                    </div>
                )}
            </div>

            {/* ═══ CLAIM BREAKDOWN ═══ */}
            {scan.sub_claims && scan.sub_claims.length > 0 && (
                <div className="results-section" style={{ marginBottom: 24, padding: 28 }}>
                    <h3 style={{ fontSize: 16, fontWeight: 700, color: 'var(--color-neutral-100)', marginBottom: 20, display: 'flex', alignItems: 'center', gap: 10 }}>
                        <Shield size={20} color="var(--color-primary-400)" />
                        FSSAI Claim Verification Breakdown
                    </h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                        {scan.sub_claims.map((sc, idx) => {
                            const svs = subVerdictStyle[sc.verdict] || subVerdictStyle.UNVERIFIABLE;
                            const SubIcon = verdictMeta[sc.verdict]?.icon || HelpCircle;
                            return (
                                <div key={idx} style={{ background: svs.bg, borderLeft: `4px solid ${svs.border}`, borderRadius: 10, padding: '16px 20px' }}>
                                    <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
                                        <SubIcon size={20} color={svs.border} style={{ marginTop: 2, flexShrink: 0 }} />
                                        <div style={{ flex: 1 }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap', marginBottom: 6 }}>
                                                <span style={{ fontSize: 15, fontWeight: 700, color: 'var(--color-neutral-100)' }}>
                                                    {sc.sub_claim || sc.claim_type?.replace(/_/g, ' ')}
                                                </span>
                                                <VerdictBadge verdict={sc.verdict} />
                                            </div>
                                            <p style={{ fontSize: 13, lineHeight: 1.6, color: 'var(--color-neutral-300)', margin: 0 }}>
                                                {sc.reason}
                                            </p>
                                            {sc.actual_value && (
                                                <div style={{ marginTop: 10, display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                                                    <span style={{ fontSize: 12, color: 'var(--color-neutral-400)', background: 'rgba(255,255,255,.04)', padding: '4px 10px', borderRadius: 6 }}>
                                                        <strong style={{ color: 'var(--color-neutral-200)' }}>Actual: </strong>{sc.actual_value}
                                                    </span>
                                                    {sc.threshold_value && (
                                                        <span style={{ fontSize: 12, color: 'var(--color-neutral-400)', background: 'rgba(255,255,255,.04)', padding: '4px 10px', borderRadius: 6 }}>
                                                            <strong style={{ color: 'var(--color-neutral-200)' }}>FSSAI Threshold: </strong>{sc.threshold_value}
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

            {/* ═══ NUTRITION OVERVIEW ═══ */}
            {scan.nutrition && (
                <div className="results-section" style={{ marginBottom: 24, padding: '28px 32px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20, flexWrap: 'wrap', gap: 10 }}>
                        <h3 style={{ fontSize: 16, fontWeight: 700, color: 'var(--color-neutral-100)', display: 'flex', alignItems: 'center', gap: 10, margin: 0 }}>
                            Nutrition Facts
                        </h3>
                        {n.serving_size && (
                            <span style={{ fontSize: 12, color: 'var(--color-neutral-400)', background: 'rgba(255,255,255,.06)', padding: '4px 14px', borderRadius: 20 }}>
                                Serving: {n.serving_size}
                            </span>
                        )}
                        <span style={{ fontSize: 11, color: 'var(--color-neutral-500)', background: 'rgba(255,255,255,.04)', padding: '3px 10px', borderRadius: 12 }}>
                            Values per 100g
                        </span>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(380px, 1fr))', gap: '0 40px' }}>
                        {/* ── Left column: Energy & Macros ── */}
                        <div>
                            <NutritionDivider label="Energy & Macronutrients" />
                            <NutritionRow label="Calories" value={n.calories} unit="kcal" maxValue={550} icon={NUTRITION_ICONS.calories} highlight />
                            <NutritionRow label="Protein" value={n.protein} unit="g" maxValue={30} icon={NUTRITION_ICONS.protein} highlight />
                            <NutritionRow label="Total Carbohydrates" value={n.carbohydrates} unit="g" maxValue={80} icon={NUTRITION_ICONS.carbohydrates} />
                            <NutritionRow label="Sugar" value={n.sugar} unit="g" maxValue={40} icon={NUTRITION_ICONS.sugar} />
                            <NutritionRow label="Dietary Fiber" value={n.fiber} unit="g" maxValue={15} icon={NUTRITION_ICONS.fiber} />
                        </div>

                        {/* ── Right column: Fats & Other ── */}
                        <div>
                            <NutritionDivider label="Fats" />
                            <NutritionRow label="Total Fat" value={n.fat} unit="g" maxValue={30} icon={NUTRITION_ICONS.fat} highlight />
                            <NutritionRow label="Saturated Fat" value={n.saturated_fat} unit="g" maxValue={15} icon={NUTRITION_ICONS.saturated_fat} />
                            <NutritionRow label="Trans Fat" value={n.trans_fat} unit="g" maxValue={2} icon={NUTRITION_ICONS.trans_fat} />

                            <NutritionDivider label="Other" />
                            <NutritionRow label="Cholesterol" value={n.cholesterol} unit="mg" maxValue={300} icon={NUTRITION_ICONS.cholesterol} />
                            <NutritionRow label="Sodium" value={n.sodium} unit="mg" maxValue={800} icon={NUTRITION_ICONS.sodium} />
                        </div>
                    </div>

                    {/* FSSAI Reference Badges */}
                    <div style={{ marginTop: 22, padding: '14px 18px', background: 'rgba(59,130,246,.05)', border: '1px solid rgba(59,130,246,.12)', borderRadius: 12 }}>
                        <div style={{ fontSize: 11, fontWeight: 600, color: '#60a5fa', marginBottom: 10, display: 'flex', alignItems: 'center', gap: 6 }}>
                            <ClipboardList size={14} /> FSSAI Claim Thresholds
                        </div>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                            {[
                                { label: 'High Protein', rule: 'Protein ≥ 20% kcal' },
                                { label: 'Sugar Free', rule: 'Sugar ≤ 0.5g' },
                                { label: 'Low Fat', rule: 'Fat ≤ 3g' },
                                { label: 'Trans Fat Free', rule: 'Trans Fat ≤ 0.2g' },
                                { label: 'High Fiber', rule: 'Fiber ≥ 6g' },
                                { label: 'Low Sodium', rule: 'Sodium ≤ 120mg' },
                            ].map((t, i) => (
                                <span key={i} style={{
                                    fontSize: 10, padding: '4px 10px', borderRadius: 6,
                                    background: 'rgba(255,255,255,.04)', border: '1px solid rgba(255,255,255,.08)',
                                    color: 'var(--color-neutral-400)', whiteSpace: 'nowrap',
                                }}>
                                    <strong style={{ color: 'var(--color-neutral-200)' }}>{t.label}:</strong> {t.rule}
                                </span>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {/* ═══ INGREDIENT WARNINGS ═══ */}
            {scan.ingredient_warnings && scan.ingredient_warnings.length > 0 && (
                <div className="results-section" style={{ marginBottom: 24, padding: '28px 32px' }}>
                    <h3 style={{ fontSize: 16, fontWeight: 700, color: '#f97316', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 10 }}>
                        <AlertTriangle size={20} />
                        Ingredient Warnings
                        <span style={{ fontSize: 11, fontWeight: 500, color: 'var(--color-neutral-400)', background: 'rgba(249,115,22,.12)', padding: '2px 10px', borderRadius: 10 }}>
                            {scan.ingredient_warnings.length}
                        </span>
                    </h3>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 8 }}>
                        {scan.ingredient_warnings.map((w, idx) => (
                            <div key={idx} style={{
                                padding: '12px 16px', background: 'rgba(249,115,22,.05)',
                                borderLeft: '3px solid #f97316', borderRadius: 8,
                                fontSize: 13, color: 'var(--color-neutral-300)', lineHeight: 1.5,
                                display: 'flex', alignItems: 'flex-start', gap: 10,
                            }}>
                                <AlertTriangle size={14} color="#f97316" style={{ marginTop: 1, flexShrink: 0 }} />
                                <span>{w}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* ═══ ALLERGEN WARNINGS ═══ */}
            {scan.allergens_detected && scan.allergens_detected.length > 0 && (
                <div className="results-section" style={{ marginBottom: 24, padding: '28px 32px' }}>
                    <h3 style={{ fontSize: 16, fontWeight: 700, color: '#ef4444', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 10 }}>
                        <AlertCircle size={20} />
                        Allergens Detected
                        <span style={{ fontSize: 11, fontWeight: 500, color: 'var(--color-neutral-400)', background: 'rgba(239,68,68,.12)', padding: '2px 10px', borderRadius: 10 }}>
                            {scan.allergens_detected.length}
                        </span>
                    </h3>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10 }}>
                        {scan.allergens_detected.map((allergen, idx) => (
                            <div key={idx} style={{
                                padding: '8px 16px', background: 'rgba(239,68,68,.08)',
                                border: '1px solid rgba(239,68,68,.2)', borderRadius: 20,
                                fontSize: 14, fontWeight: 600, color: '#ef4444',
                                display: 'flex', alignItems: 'center', gap: 8, textTransform: 'capitalize'
                            }}>
                                <AlertCircle size={14} />
                                {allergen}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* ═══ HEALTHIER ALTERNATIVES ═══ */}
            <IngredientAlternatives warnings={scan.ingredient_warnings} />

            {/* ═══ WHAT THIS MEANS ═══ */}
            <div className="results-section" style={{ marginBottom: 24, padding: 28, background: 'rgba(59,130,246,.05)', border: '1px solid rgba(59,130,246,.15)' }}>
                <h3 style={{ fontSize: 16, fontWeight: 700, color: 'var(--color-info)', marginBottom: 14, display: 'flex', alignItems: 'center', gap: 10 }}>
                    <Info size={20} /> What This Means For You
                </h3>
                <p style={{ fontSize: 14, lineHeight: 1.8, color: 'var(--color-neutral-300)', margin: 0 }}>
                    {scan.verdict === 'TRUE' && 'Great news! The claim on this product is backed by its nutrition facts and ingredients list. You can trust this claim based on the data extracted from the label.'}
                    {scan.verdict === 'PARTIALLY_TRUE' && "This product partially meets the criteria. While some aspects check out, others don't fully align. Review the specific breakdown above to understand which parts of the claim hold true."}
                    {scan.verdict === 'MISLEADING' && 'The data suggests this claim is misleading. The product may use technically correct language but the overall impression created may not match reality. Review the breakdown above.'}
                    {scan.verdict === 'FALSE' && 'The extracted data directly contradicts this claim. The product does NOT meet the required FSSAI criteria. This could be an exaggerated or false marketing claim.'}
                    {scan.verdict === 'UNVERIFIABLE' && 'We could not extract enough data from the label to verify this claim. This may be due to image quality or OCR limitations. Try uploading a clearer, closer photo of the label.'}
                </p>
            </div>

            {/* ═══ DETAILED EXPLANATION ═══ */}
            {scan.explanation && (
                <div className="results-section" style={{ marginBottom: 24, padding: 28 }}>
                    <h3 style={{ fontSize: 16, fontWeight: 700, color: 'var(--color-neutral-100)', marginBottom: 20, display: 'flex', alignItems: 'center', gap: 10 }}>
                        Detailed Analysis
                    </h3>
                    <div style={{ color: 'var(--color-neutral-300)', fontSize: 13, lineHeight: 1.8 }}>
                        {scan.explanation.split('\n').map((line, idx) => {
                            const parsedLine = line.replace(/\*\*([^*]+)\*\*/g, '<strong style="color:var(--color-neutral-100);font-weight:600">$1</strong>');

                            // Handle empty lines
                            if (line.trim() === '') return <div key={idx} style={{ height: 8 }} />;

                            // Format lines starting with emojis (sub-claims or breakdown items) as list items
                            if (line.match(/^[✅❌⚠️❓🟡]/) || line.trim().startsWith('•') || line.trim().startsWith('-')) {
                                return (
                                    <div key={idx} style={{ paddingLeft: 16, marginBottom: 4, display: 'flex', alignItems: 'flex-start', gap: 6 }}>
                                        <div dangerouslySetInnerHTML={{ __html: parsedLine }} />
                                    </div>
                                );
                            }

                            // Format standard text lines
                            return <div key={idx} style={{ marginBottom: 6 }} dangerouslySetInnerHTML={{ __html: parsedLine }} />;
                        })}
                    </div>
                </div>
            )}

            {/* ═══ OCR DEBUG (collapsible) ═══ */}
            {(scan.ocr_nutrition_text || scan.ocr_ingredients_text) && (
                <div className="results-section" style={{ marginBottom: 24, padding: 0, overflow: 'hidden' }}>
                    <button onClick={() => setShowOcr(!showOcr)} style={{
                        width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                        padding: '18px 28px', background: 'transparent', border: 'none',
                        cursor: 'pointer', color: 'var(--color-neutral-500)', fontSize: 13, fontWeight: 500
                    }}>
                        <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}><Search size={14} /> Raw OCR Text (for debugging)</span>
                        {showOcr ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                    </button>
                    {showOcr && (
                        <div style={{ padding: '0 28px 24px' }}>
                            {scan.ocr_nutrition_text && (
                                <div style={{ marginBottom: 16 }}>
                                    <h4 style={{ color: 'var(--color-primary-400)', marginBottom: 8, fontSize: 13, display: 'flex', alignItems: 'center', gap: 6 }}><BarChart3 size={14} /> Nutrition Label Text:</h4>
                                    <textarea readOnly value={scan.ocr_nutrition_text} style={{ width: '100%', minHeight: 120, padding: 12, background: 'var(--color-neutral-900)', border: '1px solid var(--color-neutral-700)', borderRadius: 8, color: 'var(--color-neutral-200)', fontSize: 12, fontFamily: 'monospace', resize: 'vertical' }} />
                                </div>
                            )}
                            {scan.ocr_ingredients_text && (
                                <div>
                                    <h4 style={{ color: 'var(--color-secondary-400)', marginBottom: 8, fontSize: 13, display: 'flex', alignItems: 'center', gap: 6 }}><FlaskConical size={14} /> Ingredients Text:</h4>
                                    <textarea readOnly value={scan.ocr_ingredients_text} style={{ width: '100%', minHeight: 120, padding: 12, background: 'var(--color-neutral-900)', border: '1px solid var(--color-neutral-700)', borderRadius: 8, color: 'var(--color-neutral-200)', fontSize: 12, fontFamily: 'monospace', resize: 'vertical' }} />
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}

            {/* ═══ ACTIONS ═══ */}
            <div style={{ display: 'flex', justifyContent: 'center', gap: 16, marginTop: 12, marginBottom: 40, flexWrap: 'wrap' }}>
                <button className="btn btn-primary" onClick={() => navigate('/dashboard')}>Scan Another Product</button>
                <button className="btn btn-secondary" onClick={() => navigate('/history')}>View History</button>
            </div>
        </div>
    );
}

export default Results;
