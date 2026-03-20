/**
 * Centralised SVG icon mappings — replaces all emoji usage with lucide-react icons.
 * Every component imports from here so the project has a consistent, professional look.
 *
 * lucide-react ≥ 0.309 compatible — only well-established icon names used.
 */
import {
    Nut, Cookie, Candy, Coffee,
    Zap, Milk, UtensilsCrossed, FlaskConical, Pill, Snowflake,
    Flame, Beef, Wheat, Sandwich,
    Ban, Leaf, Egg, TreePine, Palette,
    Dumbbell, Droplets, Search, BarChart3,
    Star, CheckCircle, AlertTriangle, XCircle, Circle,
    Lightbulb, ClipboardList, TestTubes, Heart, Salad,
    ShieldOff, ShieldCheck, BatteryLow, Sparkles,
    FlaskRound, Hand, HeartPulse, Activity, Scale, Smile
} from 'lucide-react';

/* ─────────── Product‑category icons ─────────── */

export const CATEGORY_ICONS = {
    PROTEIN_BAR: Nut,
    BREAKFAST_CEREAL: UtensilsCrossed,
    BISCUITS_COOKIES: Cookie,
    SNACKS: Sandwich,
    CHOCOLATES_CONFECTIONERY: Candy,
    BEVERAGES: Coffee,
    ENERGY_DRINKS: Zap,
    INSTANT_NOODLES_RTE: UtensilsCrossed,
    SAUCES_SPREADS: FlaskConical,
    HEALTH_SUPPLEMENTS: Pill,
    FROZEN_FOODS: Snowflake,
};

const CATEGORY_LABELS = {
    PROTEIN_BAR: 'Protein Bar',
    BREAKFAST_CEREAL: 'Breakfast Cereal',
    BISCUITS_COOKIES: 'Biscuits & Cookies',
    SNACKS: 'Snacks',
    CHOCOLATES_CONFECTIONERY: 'Chocolate & Confectionery',
    BEVERAGES: 'Beverages',
    ENERGY_DRINKS: 'Energy Drinks',
    INSTANT_NOODLES_RTE: 'Instant Noodles / RTE',
    SAUCES_SPREADS: 'Sauces & Spreads',
    HEALTH_SUPPLEMENTS: 'Health Supplements',
    FROZEN_FOODS: 'Frozen Foods',
};

const CATEGORY_LABELS_SHORT = {
    PROTEIN_BAR: 'Protein Bar',
    BREAKFAST_CEREAL: 'Cereal',
    BISCUITS_COOKIES: 'Biscuits',
    SNACKS: 'Snacks',
    CHOCOLATES_CONFECTIONERY: 'Chocolate',
    BEVERAGES: 'Beverages',
    ENERGY_DRINKS: 'Energy Drinks',
    INSTANT_NOODLES_RTE: 'Noodles/RTE',
    SAUCES_SPREADS: 'Sauces',
    HEALTH_SUPPLEMENTS: 'Supplements',
    FROZEN_FOODS: 'Frozen',
};

/** Return the Lucide icon component for a category key. */
export function getCategoryIcon(key) {
    return CATEGORY_ICONS[key] || Circle;
}

/** Return human-friendly label for a category key. */
export function getCategoryLabel(category, short = false) {
    return (short ? CATEGORY_LABELS_SHORT : CATEGORY_LABELS)[category] || category;
}

/** Array of category objects ready for grids / selectors. */
export const CATEGORIES = Object.keys(CATEGORY_ICONS).map((key) => ({
    key,
    Icon: CATEGORY_ICONS[key],
    label: CATEGORY_LABELS_SHORT[key],
    labelFull: CATEGORY_LABELS[key],
}));

/* ─────────── Nutrition‑row icon components ─────────── */

export const NUTRITION_ICONS = {
    calories: Flame,
    protein: Beef,
    carbohydrates: Sandwich,
    sugar: Candy,
    fiber: Wheat,
    fat: Droplets,
    saturated_fat: Droplets,
    trans_fat: AlertTriangle,
    cholesterol: Heart,
    sodium: FlaskConical,
};

/* ─────────── Health‑score rating ─────────── */

export function getHealthRating(score) {
    if (score >= 80) return { label: 'Excellent', color: '#22c55e', Icon: Star };
    if (score >= 65) return { label: 'Good', color: '#86efac', Icon: CheckCircle };
    if (score >= 50) return { label: 'Average', color: '#eab308', Icon: AlertTriangle };
    if (score >= 35) return { label: 'Poor', color: '#f97316', Icon: Circle };
    return { label: 'Unhealthy', color: '#ef4444', Icon: XCircle };
}

/* ─────────── Health‑score factor icons ─────────── */

export const HEALTH_FACTORS = [
    { Icon: Beef, label: 'Protein content', effect: 'Adds up to +15 pts for high protein foods' },
    { Icon: Candy, label: 'Sugar content', effect: 'Penalty of up to -15 pts for excess sugar' },
    { Icon: Wheat, label: 'Dietary fiber', effect: 'Up to +12 pts for high fiber' },
    { Icon: Droplets, label: 'Total fat', effect: 'Penalty up to -10 pts for very high fat' },
    { Icon: FlaskConical, label: 'Sodium', effect: 'Penalty up to -10 pts for excess sodium' },
    { Icon: Flame, label: 'Calories', effect: 'Penalty of -5 pts if >450 kcal / 100g' },
    { Icon: FlaskRound, label: 'Artificial sweeteners', effect: '-8 pts if detected in ingredients' },
    { Icon: TestTubes, label: 'Preservatives', effect: '-5 pts per preservative found' },
    { Icon: AlertTriangle, label: 'Trans fats', effect: '-15 pts if trans fat source detected' },
];

/* ─────────── Claim‑tag icons ─────────── */

export const CLAIM_ICONS = {
    // Nutrition-based Claims
    'High Protein': Dumbbell,
    'Good Source of Protein': Beef,
    'Low Sugar': Candy,
    'No Sugar': Ban,
    'No Added Sugar': Ban,
    'High Fiber': Wheat,
    'Low Fat': Droplets,
    'Low Calories': BatteryLow,
    'Low Sodium': FlaskConical,

    // Ingredient-based Claims
    'No Trans Fat': ShieldOff,
    'Clean Ingredients': Sparkles,
    'No Preservatives': TestTubes,
    'No Artificial Colors': Palette,
    'No Artificial Flavors': FlaskRound,
    'Whole Grain': Wheat,

    // Compound / Profile-based Claims
    'Healthy': HeartPulse,
    'Diabetic Friendly': Activity,
    'Weight Loss Friendly': Scale,
    'Child Friendly': Smile,
    'Heart Healthy': Heart,
};

/** Return the Lucide icon component for a claim label. */
export function getClaimIcon(label) {
    return CLAIM_ICONS[label] || CheckCircle;
}

/* ─────────── Re‑exports for misc inline usage ─────────── */

export {
    Lightbulb as TipIcon,
    Hand as WaveIcon,
    Search as SearchIcon,
    BarChart3 as ChartIcon,
    ClipboardList as ClipboardIcon,
    Ban as ProhibitedIcon,
    ShieldCheck as SwitchToIcon,
};
