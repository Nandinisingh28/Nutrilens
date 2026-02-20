"""
Database Seeder – populates category_nutrition_rules, claim_rules, and ingredient_risk_master.
Idempotent: only inserts if the tables are empty.
Force-refreshes claim_rules when the expected count changes (schema evolution).
"""
import logging
from sqlalchemy.orm import Session

from app.models.rules import CategoryNutritionRule, ClaimRule, IngredientRiskMaster, RiskLevel

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 1. Category Nutrition Rules  (per 100 g / 100 ml)
#    NOTE: sodium_max here is the HEALTH evaluation threshold, NOT the claim threshold.
#    Claim threshold for "Low Sodium" is 120mg (FSSAI standard) – defined in claim rules.
#    Health evaluation: ≤400mg = good, >600mg = high risk
# ---------------------------------------------------------------------------
CATEGORY_NUTRITION_RULES = [
    # category, protein_min, sugar_max, fat_max, fiber_min, sodium_max(health), calories_max
    ("PROTEIN_BAR",              15,  15, 15,  3,  400,  400),
    ("BREAKFAST_CEREAL",          5,  15, 10,  4,  500,  400),
    ("BISCUITS_COOKIES",          3,  20, 20,  2,  500,  480),
    ("SNACKS",                    3,  10, 15,  2,  600,  500),
    ("CHOCOLATES_CONFECTIONERY",  3,  40, 30,  1,  200,  550),
    ("BEVERAGES",                 0,   5,  0,  0,  200,   50),
    ("ENERGY_DRINKS",             0,   8,  0,  0,  300,   60),
    ("DAIRY_PRODUCTS",            3,  10, 10,  0,  400,  150),
    ("INSTANT_NOODLES_RTE",       5,   5, 15,  2,  800,  450),
    ("SAUCES_SPREADS",            1,  15, 20,  0,  800,  350),
    ("HEALTH_SUPPLEMENTS",       20,  10, 10,  3,  400,  400),
    ("FROZEN_FOODS",              5,  10, 15,  2,  600,  350),
]

# ---------------------------------------------------------------------------
# 2. Claim Rules
# ---------------------------------------------------------------------------
ALL_CATEGORIES = [r[0] for r in CATEGORY_NUTRITION_RULES]

CLAIM_RULES_DATA: dict = {}

def _add_claim(claim_type: str, category_thresholds: dict, ingredient_check_type: str | None, description: str):
    """Register a claim with per-category nutrition conditions."""
    CLAIM_RULES_DATA[claim_type] = {
        "categories": category_thresholds,
        "ingredient_check_type": ingredient_check_type,
        "description": description,
    }

# HIGH_PROTEIN
_add_claim("HIGH_PROTEIN", {
    "PROTEIN_BAR": [("protein_per_100g", "gte", 20)],
    "BREAKFAST_CEREAL": [("protein_per_100g", "gte", 10)],
    "BISCUITS_COOKIES": [("protein_per_100g", "gte", 10)],
    "SNACKS": [("protein_per_100g", "gte", 10)],
    "CHOCOLATES_CONFECTIONERY": [("protein_per_100g", "gte", 8)],
    "BEVERAGES": [("protein_per_100g", "gte", 5)],
    "ENERGY_DRINKS": [("protein_per_100g", "gte", 5)],
    "DAIRY_PRODUCTS": [("protein_per_100g", "gte", 8)],
    "INSTANT_NOODLES_RTE": [("protein_per_100g", "gte", 10)],
    "SAUCES_SPREADS": [("protein_per_100g", "gte", 5)],
    "HEALTH_SUPPLEMENTS": [("protein_per_100g", "gte", 25)],
    "FROZEN_FOODS": [("protein_per_100g", "gte", 10)],
}, None, "High protein content")

# GOOD_SOURCE_OF_PROTEIN
_add_claim("GOOD_SOURCE_OF_PROTEIN", {
    "PROTEIN_BAR": [("protein_per_100g", "gte", 10)],
    "BREAKFAST_CEREAL": [("protein_per_100g", "gte", 6)],
    "BISCUITS_COOKIES": [("protein_per_100g", "gte", 5)],
    "SNACKS": [("protein_per_100g", "gte", 5)],
    "CHOCOLATES_CONFECTIONERY": [("protein_per_100g", "gte", 5)],
    "BEVERAGES": [("protein_per_100g", "gte", 3)],
    "ENERGY_DRINKS": [("protein_per_100g", "gte", 3)],
    "DAIRY_PRODUCTS": [("protein_per_100g", "gte", 5)],
    "INSTANT_NOODLES_RTE": [("protein_per_100g", "gte", 5)],
    "SAUCES_SPREADS": [("protein_per_100g", "gte", 3)],
    "HEALTH_SUPPLEMENTS": [("protein_per_100g", "gte", 15)],
    "FROZEN_FOODS": [("protein_per_100g", "gte", 5)],
}, None, "Good source of protein")

# LOW_SUGAR – category-specific (NOT blanket 5g)
_add_claim("LOW_SUGAR", {
    "PROTEIN_BAR": [("sugar_per_100g", "lte", 5)],
    "BREAKFAST_CEREAL": [("sugar_per_100g", "lte", 10)],
    "BISCUITS_COOKIES": [("sugar_per_100g", "lte", 10)],
    "SNACKS": [("sugar_per_100g", "lte", 5)],
    "CHOCOLATES_CONFECTIONERY": [("sugar_per_100g", "lte", 15)],
    "BEVERAGES": [("sugar_per_100g", "lte", 5)],
    "ENERGY_DRINKS": [("sugar_per_100g", "lte", 5)],
    "DAIRY_PRODUCTS": [("sugar_per_100g", "lte", 8)],
    "INSTANT_NOODLES_RTE": [("sugar_per_100g", "lte", 5)],
    "SAUCES_SPREADS": [("sugar_per_100g", "lte", 8)],
    "HEALTH_SUPPLEMENTS": [("sugar_per_100g", "lte", 5)],
    "FROZEN_FOODS": [("sugar_per_100g", "lte", 5)],
}, None, "Low sugar content")

# NO_SUGAR
_add_claim("NO_SUGAR", {cat: [("sugar_per_100g", "lte", 0.5)] for cat in ALL_CATEGORIES},
           "no_sugar", "Sugar free (< 0.5g per 100g)")

# NO_ADDED_SUGAR
_add_claim("NO_ADDED_SUGAR", {cat: [("sugar_per_100g", "lte", 5)] for cat in ALL_CATEGORIES},
           "no_added_sugar", "No added sugars")

# HIGH_FIBER
_add_claim("HIGH_FIBER", {
    "PROTEIN_BAR": [("fiber_per_100g", "gte", 6)],
    "BREAKFAST_CEREAL": [("fiber_per_100g", "gte", 6)],
    "BISCUITS_COOKIES": [("fiber_per_100g", "gte", 6)],
    "SNACKS": [("fiber_per_100g", "gte", 6)],
    "CHOCOLATES_CONFECTIONERY": [("fiber_per_100g", "gte", 4)],
    "BEVERAGES": [("fiber_per_100g", "gte", 2)],
    "ENERGY_DRINKS": [("fiber_per_100g", "gte", 2)],
    "DAIRY_PRODUCTS": [("fiber_per_100g", "gte", 3)],
    "INSTANT_NOODLES_RTE": [("fiber_per_100g", "gte", 4)],
    "SAUCES_SPREADS": [("fiber_per_100g", "gte", 3)],
    "HEALTH_SUPPLEMENTS": [("fiber_per_100g", "gte", 6)],
    "FROZEN_FOODS": [("fiber_per_100g", "gte", 4)],
}, None, "High fiber content")

# LOW_FAT (FSSAI: ≤ 3g per 100g)
_add_claim("LOW_FAT", {cat: [("fat_per_100g", "lte", 3)] for cat in ALL_CATEGORIES},
           None, "Low fat (≤ 3g per 100g)")

# NO_TRANS_FAT (ingredient-only)
_add_claim("NO_TRANS_FAT", {cat: [] for cat in ALL_CATEGORIES},
           "no_trans_fat", "No trans fats (no partially hydrogenated oils)")

# LOW_CALORIES – category-specific per-100g thresholds (CODEX-aligned)
_add_claim("LOW_CALORIES", {
    "PROTEIN_BAR": [("calories_per_100g", "lte", 250)],
    "BREAKFAST_CEREAL": [("calories_per_100g", "lte", 350)],
    "BISCUITS_COOKIES": [("calories_per_100g", "lte", 400)],
    "SNACKS": [("calories_per_100g", "lte", 450)],
    "CHOCOLATES_CONFECTIONERY": [("calories_per_100g", "lte", 400)],
    "BEVERAGES": [("calories_per_100g", "lte", 20)],
    "ENERGY_DRINKS": [("calories_per_100g", "lte", 25)],
    "DAIRY_PRODUCTS": [("calories_per_100g", "lte", 100)],
    "INSTANT_NOODLES_RTE": [("calories_per_100g", "lte", 350)],
    "SAUCES_SPREADS": [("calories_per_100g", "lte", 200)],
    "HEALTH_SUPPLEMENTS": [("calories_per_100g", "lte", 300)],
    "FROZEN_FOODS": [("calories_per_100g", "lte", 250)],
}, None, "Low calorie content")

# LOW_SODIUM (FSSAI claim threshold: ≤ 120mg per 100g)
# Distinct from health evaluation threshold (≤400mg good, >600mg high)
_add_claim("LOW_SODIUM", {cat: [("sodium_per_100g", "lte", 120)] for cat in ALL_CATEGORIES},
           None, "Low sodium (≤ 120mg per 100g per FSSAI)")

# HIGH_CALCIUM (ingredient-only, partially verifiable)
_add_claim("HIGH_CALCIUM", {cat: [] for cat in ALL_CATEGORIES},
           "high_calcium", "High calcium (partially verifiable from ingredients)")

# HEALTHY (multi-condition)
_add_claim("HEALTHY", {
    "PROTEIN_BAR":   [("sugar_per_100g", "lte", 15), ("fat_per_100g", "lte", 15), ("fiber_per_100g", "gte", 3)],
    "BREAKFAST_CEREAL": [("sugar_per_100g", "lte", 15), ("fiber_per_100g", "gte", 4)],
    "BISCUITS_COOKIES": [("sugar_per_100g", "lte", 18), ("fat_per_100g", "lte", 18), ("fiber_per_100g", "gte", 2)],
    "SNACKS":        [("sugar_per_100g", "lte", 8),  ("fat_per_100g", "lte", 12), ("sodium_per_100g", "lte", 500)],
    "CHOCOLATES_CONFECTIONERY": [("sugar_per_100g", "lte", 35), ("fat_per_100g", "lte", 25)],
    "BEVERAGES":     [("sugar_per_100g", "lte", 5),  ("calories_per_100g", "lte", 40)],
    "ENERGY_DRINKS": [("sugar_per_100g", "lte", 5),  ("calories_per_100g", "lte", 50)],
    "DAIRY_PRODUCTS":[("sugar_per_100g", "lte", 8),  ("fat_per_100g", "lte", 8),  ("protein_per_100g", "gte", 3)],
    "INSTANT_NOODLES_RTE": [("sugar_per_100g", "lte", 5), ("fat_per_100g", "lte", 12), ("sodium_per_100g", "lte", 700)],
    "SAUCES_SPREADS":[("sugar_per_100g", "lte", 12), ("sodium_per_100g", "lte", 800)],
    "HEALTH_SUPPLEMENTS": [("sugar_per_100g", "lte", 10), ("protein_per_100g", "gte", 15)],
    "FROZEN_FOODS":  [("sugar_per_100g", "lte", 8),  ("fat_per_100g", "lte", 12), ("sodium_per_100g", "lte", 600)],
}, "no_trans_fat", "Balanced nutritional profile")

# CLEAN_INGREDIENTS (ingredient-only)
_add_claim("CLEAN_INGREDIENTS", {cat: [] for cat in ALL_CATEGORIES},
           "clean", "No artificial additives, preservatives, or sweeteners")

# DIABETIC_FRIENDLY
_add_claim("DIABETIC_FRIENDLY", {
    "PROTEIN_BAR":   [("sugar_per_100g", "lte", 5),  ("fiber_per_100g", "gte", 3)],
    "BREAKFAST_CEREAL": [("sugar_per_100g", "lte", 8), ("fiber_per_100g", "gte", 5)],
    "BISCUITS_COOKIES": [("sugar_per_100g", "lte", 5), ("fiber_per_100g", "gte", 3)],
    "SNACKS":        [("sugar_per_100g", "lte", 3),  ("fiber_per_100g", "gte", 2)],
    "CHOCOLATES_CONFECTIONERY": [("sugar_per_100g", "lte", 8)],
    "BEVERAGES":     [("sugar_per_100g", "lte", 2)],
    "ENERGY_DRINKS": [("sugar_per_100g", "lte", 2)],
    "DAIRY_PRODUCTS":[("sugar_per_100g", "lte", 5)],
    "INSTANT_NOODLES_RTE": [("sugar_per_100g", "lte", 3), ("fiber_per_100g", "gte", 2)],
    "SAUCES_SPREADS":[("sugar_per_100g", "lte", 5)],
    "HEALTH_SUPPLEMENTS": [("sugar_per_100g", "lte", 5), ("fiber_per_100g", "gte", 3)],
    "FROZEN_FOODS":  [("sugar_per_100g", "lte", 5),  ("fiber_per_100g", "gte", 2)],
}, None, "Suitable for diabetics")

# WEIGHT_LOSS_FRIENDLY
_add_claim("WEIGHT_LOSS_FRIENDLY", {
    "PROTEIN_BAR":   [("calories_per_100g", "lte", 350), ("protein_per_100g", "gte", 15), ("fiber_per_100g", "gte", 4)],
    "BREAKFAST_CEREAL": [("calories_per_100g", "lte", 380), ("fiber_per_100g", "gte", 6)],
    "BISCUITS_COOKIES": [("calories_per_100g", "lte", 400), ("fat_per_100g", "lte", 12)],
    "SNACKS":        [("calories_per_100g", "lte", 400), ("fat_per_100g", "lte", 10)],
    "CHOCOLATES_CONFECTIONERY": [("calories_per_100g", "lte", 450)],
    "BEVERAGES":     [("calories_per_100g", "lte", 20)],
    "ENERGY_DRINKS": [("calories_per_100g", "lte", 25)],
    "DAIRY_PRODUCTS":[("calories_per_100g", "lte", 100), ("fat_per_100g", "lte", 5)],
    "INSTANT_NOODLES_RTE": [("calories_per_100g", "lte", 350), ("fat_per_100g", "lte", 10)],
    "SAUCES_SPREADS":[("calories_per_100g", "lte", 200), ("fat_per_100g", "lte", 10)],
    "HEALTH_SUPPLEMENTS": [("calories_per_100g", "lte", 350), ("protein_per_100g", "gte", 20)],
    "FROZEN_FOODS":  [("calories_per_100g", "lte", 250), ("fat_per_100g", "lte", 8)],
}, None, "Suitable for weight management")

# HEART_HEALTHY
_add_claim("HEART_HEALTHY", {
    "PROTEIN_BAR":   [("fat_per_100g", "lte", 12), ("fiber_per_100g", "gte", 3)],
    "BREAKFAST_CEREAL": [("fat_per_100g", "lte", 5), ("fiber_per_100g", "gte", 5)],
    "BISCUITS_COOKIES": [("fat_per_100g", "lte", 8), ("fiber_per_100g", "gte", 3)],
    "SNACKS":        [("fat_per_100g", "lte", 8),  ("sodium_per_100g", "lte", 400)],
    "CHOCOLATES_CONFECTIONERY": [("fat_per_100g", "lte", 15)],
    "BEVERAGES":     [("sugar_per_100g", "lte", 5)],
    "ENERGY_DRINKS": [("sugar_per_100g", "lte", 5), ("sodium_per_100g", "lte", 200)],
    "DAIRY_PRODUCTS":[("fat_per_100g", "lte", 5),  ("sodium_per_100g", "lte", 300)],
    "INSTANT_NOODLES_RTE": [("fat_per_100g", "lte", 8), ("sodium_per_100g", "lte", 500)],
    "SAUCES_SPREADS":[("fat_per_100g", "lte", 10), ("sodium_per_100g", "lte", 600)],
    "HEALTH_SUPPLEMENTS": [("fat_per_100g", "lte", 8), ("fiber_per_100g", "gte", 3)],
    "FROZEN_FOODS":  [("fat_per_100g", "lte", 8),  ("sodium_per_100g", "lte", 500)],
}, "no_trans_fat", "Heart healthy (low fat, no trans fat)")

# NATURAL (ingredient-only, partially verifiable – loosely regulated)
_add_claim("NATURAL", {cat: [] for cat in ALL_CATEGORIES},
           "natural", "No artificial ingredients (partially verifiable)")

# ORGANIC (ingredient-only, partially verifiable – requires certification)
_add_claim("ORGANIC", {cat: [] for cat in ALL_CATEGORIES},
           "organic", "Organic claim (partially verifiable – certification required)")

# NO_PRESERVATIVES (ingredient-only)
_add_claim("NO_PRESERVATIVES", {cat: [] for cat in ALL_CATEGORIES},
           "no_preservatives", "No artificial preservatives")

# NO_ARTIFICIAL_COLORS (ingredient-only)
_add_claim("NO_ARTIFICIAL_COLORS", {cat: [] for cat in ALL_CATEGORIES},
           "no_artificial_colors", "No artificial colors")

# NO_ARTIFICIAL_FLAVORS (ingredient-only)
_add_claim("NO_ARTIFICIAL_FLAVORS", {cat: [] for cat in ALL_CATEGORIES},
           "no_artificial_flavors", "No artificial flavors")

# WHOLE_GRAIN (ingredient-only)
_add_claim("WHOLE_GRAIN", {cat: [] for cat in ALL_CATEGORIES},
           "whole_grain", "Contains whole grains")

# CHILD_FRIENDLY
_add_claim("CHILD_FRIENDLY", {
    "PROTEIN_BAR":   [("sugar_per_100g", "lte", 12), ("protein_per_100g", "gte", 5)],
    "BREAKFAST_CEREAL": [("sugar_per_100g", "lte", 15)],
    "BISCUITS_COOKIES": [("sugar_per_100g", "lte", 15), ("fat_per_100g", "lte", 18)],
    "SNACKS":        [("sugar_per_100g", "lte", 8),  ("sodium_per_100g", "lte", 400)],
    "CHOCOLATES_CONFECTIONERY": [("sugar_per_100g", "lte", 30)],
    "BEVERAGES":     [("sugar_per_100g", "lte", 5)],
    "ENERGY_DRINKS": [("sugar_per_100g", "lte", 5)],
    "DAIRY_PRODUCTS":[("sugar_per_100g", "lte", 10)],
    "INSTANT_NOODLES_RTE": [("sugar_per_100g", "lte", 5), ("sodium_per_100g", "lte", 500)],
    "SAUCES_SPREADS":[("sugar_per_100g", "lte", 10), ("sodium_per_100g", "lte", 600)],
    "HEALTH_SUPPLEMENTS": [("sugar_per_100g", "lte", 8)],
    "FROZEN_FOODS":  [("sugar_per_100g", "lte", 8),  ("sodium_per_100g", "lte", 500)],
}, "no_artificial", "Suitable for children")

# ---------------------------------------------------------------------------
# 3.  Ingredient Risk Master
# ---------------------------------------------------------------------------
INGREDIENT_RISKS = [
    # (ingredient_name, category, risk_level, description)
    # Artificial sweeteners
    ("aspartame",        "artificial_sweetener", RiskLevel.MEDIUM, "Controversial artificial sweetener"),
    ("sucralose",        "artificial_sweetener", RiskLevel.LOW,    "Artificial sweetener"),
    ("stevia",           "artificial_sweetener", RiskLevel.LOW,    "Natural zero-calorie sweetener"),
    ("saccharin",        "artificial_sweetener", RiskLevel.MEDIUM, "Artificial sweetener"),
    ("acesulfame",       "artificial_sweetener", RiskLevel.MEDIUM, "Artificial sweetener (Ace-K)"),
    # Added sugars
    ("high fructose corn syrup", "added_sugar", RiskLevel.HIGH, "High fructose corn syrup"),
    ("hfcs",             "added_sugar",          RiskLevel.HIGH,   "High fructose corn syrup"),
    ("corn syrup",       "added_sugar",          RiskLevel.MEDIUM, "Added sugar"),
    ("maltodextrin",     "added_sugar",          RiskLevel.MEDIUM, "High glycemic ingredient"),
    # Preservatives
    ("sodium benzoate",  "preservative",         RiskLevel.MEDIUM, "Common preservative"),
    ("potassium sorbate","preservative",         RiskLevel.LOW,    "Common preservative"),
    ("bha",              "preservative",         RiskLevel.HIGH,   "Controversial preservative (butylated hydroxyanisole)"),
    ("bht",              "preservative",         RiskLevel.HIGH,   "Controversial preservative (butylated hydroxytoluene)"),
    ("sodium nitrite",   "preservative",         RiskLevel.HIGH,   "Preservative linked to health concerns"),
    ("tbhq",             "preservative",         RiskLevel.HIGH,   "Tertiary butylhydroquinone"),
    # Artificial colors
    ("red 40",           "artificial_color",     RiskLevel.MEDIUM, "Artificial color (Allura Red)"),
    ("yellow 5",         "artificial_color",     RiskLevel.MEDIUM, "Artificial color (Tartrazine)"),
    ("tartrazine",       "artificial_color",     RiskLevel.MEDIUM, "Artificial color (E102)"),
    ("yellow 6",         "artificial_color",     RiskLevel.MEDIUM, "Artificial color (Sunset Yellow)"),
    ("blue 1",           "artificial_color",     RiskLevel.LOW,    "Artificial color (Brilliant Blue)"),
    # Trans fats
    ("partially hydrogenated", "trans_fat",      RiskLevel.HIGH,   "Contains trans fats"),
    # Flavor enhancers
    ("monosodium glutamate", "flavor_enhancer",  RiskLevel.LOW,    "Flavor enhancer (MSG)"),
    ("msg",              "flavor_enhancer",      RiskLevel.LOW,    "Flavor enhancer (MSG)"),
    # Emulsifiers of concern
    ("carrageenan",      "emulsifier",           RiskLevel.MEDIUM, "Emulsifier with potential gut health concerns"),
    ("polysorbate 80",   "emulsifier",           RiskLevel.MEDIUM, "Emulsifier linked to gut inflammation"),
]


# ---------------------------------------------------------------------------
# Expected counts for force-refresh detection
# ---------------------------------------------------------------------------
def _count_expected_claim_rules() -> int:
    """Count expected number of claim rule rows."""
    count = 0
    for claim_type, meta in CLAIM_RULES_DATA.items():
        for category, conditions in meta["categories"].items():
            if not conditions:
                count += 1
            else:
                count += len(conditions)
    return count


EXPECTED_CLAIM_COUNT = _count_expected_claim_rules()


# ---------------------------------------------------------------------------
# Seeder function
# ---------------------------------------------------------------------------
def seed_database(db: Session) -> None:
    """
    Populate rule tables if they are empty.  Idempotent – safe to call on every startup.
    Force-refreshes claim_rules when the expected count changes (new claims added).
    """
    # --- Category Nutrition Rules ---
    existing_nutrition = db.query(CategoryNutritionRule).count()
    if existing_nutrition == 0:
        for cat, prot, sug, fat, fib, sod, cal in CATEGORY_NUTRITION_RULES:
            db.add(CategoryNutritionRule(
                category=cat,
                protein_min=prot, sugar_max=sug, fat_max=fat,
                fiber_min=fib, sodium_max=sod, calories_max=cal,
            ))
        logger.info(f"Seeded {len(CATEGORY_NUTRITION_RULES)} category nutrition rules")
    elif existing_nutrition != len(CATEGORY_NUTRITION_RULES):
        # Schema changed – clear and re-seed
        db.query(CategoryNutritionRule).delete()
        for cat, prot, sug, fat, fib, sod, cal in CATEGORY_NUTRITION_RULES:
            db.add(CategoryNutritionRule(
                category=cat,
                protein_min=prot, sugar_max=sug, fat_max=fat,
                fiber_min=fib, sodium_max=sod, calories_max=cal,
            ))
        logger.info(f"Re-seeded {len(CATEGORY_NUTRITION_RULES)} category nutrition rules (schema changed)")
    else:
        logger.info("Category nutrition rules already seeded – skipping")

    # --- Claim Rules ---
    existing_claims = db.query(ClaimRule).count()
    if existing_claims != EXPECTED_CLAIM_COUNT:
        # Count mismatch → clear and re-seed (new claims added or removed)
        if existing_claims > 0:
            db.query(ClaimRule).delete()
            logger.info(f"Cleared {existing_claims} stale claim rules (expected {EXPECTED_CLAIM_COUNT})")
        count = 0
        for claim_type, meta in CLAIM_RULES_DATA.items():
            ing_check_type = meta["ingredient_check_type"]
            desc = meta["description"]
            for category, conditions in meta["categories"].items():
                if not conditions:
                    # Ingredient-only claim (no nutrition conditions)
                    db.add(ClaimRule(
                        claim_type=claim_type,
                        category=category,
                        nutrient=None,
                        operator=None,
                        threshold=None,
                        requires_ingredient_check=bool(ing_check_type),
                        ingredient_check_type=ing_check_type,
                        description=desc,
                    ))
                    count += 1
                else:
                    for nutrient, op, value in conditions:
                        db.add(ClaimRule(
                            claim_type=claim_type,
                            category=category,
                            nutrient=nutrient,
                            operator=op,
                            threshold=value,
                            requires_ingredient_check=bool(ing_check_type),
                            ingredient_check_type=ing_check_type,
                            description=desc,
                        ))
                        count += 1
        logger.info(f"Seeded {count} claim rules")
    else:
        logger.info("Claim rules already seeded – skipping")

    # --- Ingredient Risk Master ---
    if db.query(IngredientRiskMaster).count() == 0:
        for name, cat, risk, desc in INGREDIENT_RISKS:
            db.add(IngredientRiskMaster(
                ingredient_name=name,
                category=cat,
                risk_level=risk,
                description=desc,
            ))
        logger.info(f"Seeded {len(INGREDIENT_RISKS)} ingredient risk entries")
    else:
        logger.info("Ingredient risk master already seeded – skipping")

    db.commit()
