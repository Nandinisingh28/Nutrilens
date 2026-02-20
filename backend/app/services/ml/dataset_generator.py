"""
Dataset Generator for Health Score Model
Based on Indian Food Safety and Standards (FSSAI) and WHO guidelines.
Generates synthetic training data for 12 food categories.
"""
import pandas as pd
import numpy as np
from typing import List, Dict
import os


def generate_training_data(output_path: str = None, n_samples: int = 3000) -> pd.DataFrame:
    """
    Generate synthetic training data based on Indian food standards.
    
    FSSAI Guidelines used:
    - High Protein: ≥20% of energy from protein
    - Low Sugar: ≤5g per 100g
    - High Fiber: ≥6g per 100g (for solid foods)
    - Low Fat: ≤3g per 100g
    - Low Calorie: ≤40 kcal per 100g (beverages), ≤100 kcal per serving (foods)
    
    Args:
        output_path: Path to save CSV file
        n_samples: Number of samples to generate
        
    Returns:
        DataFrame with training data
    """
    np.random.seed(42)
    
    categories = [
        'PROTEIN_BAR', 'BREAKFAST_CEREAL', 'BISCUITS_COOKIES', 'SNACKS',
        'CHOCOLATES_CONFECTIONERY', 'BEVERAGES', 'ENERGY_DRINKS',
        'DAIRY_PRODUCTS', 'INSTANT_NOODLES_RTE', 'SAUCES_SPREADS',
        'HEALTH_SUPPLEMENTS', 'FROZEN_FOODS',
    ]
    
    generators = {
        'PROTEIN_BAR': _generate_protein_bar_sample,
        'BREAKFAST_CEREAL': _generate_cereal_sample,
        'BISCUITS_COOKIES': _generate_biscuit_sample,
        'SNACKS': _generate_snack_sample,
        'CHOCOLATES_CONFECTIONERY': _generate_chocolate_sample,
        'BEVERAGES': _generate_beverage_sample,
        'ENERGY_DRINKS': _generate_energy_drink_sample,
        'DAIRY_PRODUCTS': _generate_dairy_sample,
        'INSTANT_NOODLES_RTE': _generate_instant_noodle_sample,
        'SAUCES_SPREADS': _generate_sauce_sample,
        'HEALTH_SUPPLEMENTS': _generate_supplement_sample,
        'FROZEN_FOODS': _generate_frozen_food_sample,
    }
    
    data = []
    for i in range(n_samples):
        category = np.random.choice(categories)
        record = generators[category]()
        record['category'] = category
        data.append(record)
    
    df = pd.DataFrame(data)
    
    # Calculate health score based on rules
    df['health_score'] = df.apply(_calculate_health_score, axis=1)
    
    # Add risk labels
    df['risk_labels'] = df.apply(_generate_risk_labels, axis=1)
    
    if output_path:
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        df.to_csv(output_path, index=False)
    
    return df


# ─── Helper to build a sample dict ─────────────────────────────────────────
def _sample(protein, sugar, fat, fiber, calories, sodium,
            sweetener=0, preservatives=0, trans_fat=0, risk_count=0) -> Dict:
    return {
        'protein_per_100g': round(protein, 1),
        'sugar_per_100g': round(sugar, 1),
        'fat_per_100g': round(fat, 1),
        'fiber_per_100g': round(fiber, 1),
        'calories_per_100g': round(calories, 1),
        'sodium_per_100g': round(sodium, 1),
        'has_artificial_sweetener': int(sweetener),
        'has_preservatives': int(preservatives),
        'has_trans_fat': int(trans_fat),
        'ingredient_risk_count': int(risk_count),
    }


# ─── Per-category generators ───────────────────────────────────────────────

def _generate_protein_bar_sample() -> Dict:
    """Protein bars: high protein, variable sugar/fat"""
    p = np.random.choice(['healthy', 'moderate', 'unhealthy'], p=[0.3, 0.4, 0.3])
    if p == 'healthy':
        return _sample(
            np.random.uniform(20, 35), np.random.uniform(2, 8),
            np.random.uniform(5, 12), np.random.uniform(5, 15),
            np.random.uniform(300, 380), np.random.uniform(100, 400),
            0, np.random.choice([0, 1], p=[0.8, 0.2]), 0,
            np.random.randint(0, 2))
    elif p == 'moderate':
        return _sample(
            np.random.uniform(12, 22), np.random.uniform(8, 18),
            np.random.uniform(10, 18), np.random.uniform(3, 8),
            np.random.uniform(350, 420), np.random.uniform(200, 500),
            np.random.choice([0, 1], p=[0.5, 0.5]),
            np.random.choice([0, 1], p=[0.5, 0.5]),
            np.random.choice([0, 1], p=[0.9, 0.1]),
            np.random.randint(0, 4))
    else:
        return _sample(
            np.random.uniform(5, 15), np.random.uniform(18, 40),
            np.random.uniform(15, 25), np.random.uniform(1, 5),
            np.random.uniform(400, 500), np.random.uniform(300, 700),
            np.random.choice([0, 1], p=[0.4, 0.6]),
            np.random.choice([0, 1], p=[0.3, 0.7]),
            np.random.choice([0, 1], p=[0.7, 0.3]),
            np.random.randint(2, 6))


def _generate_cereal_sample() -> Dict:
    """Breakfast cereals: fiber-centric, variable sugar"""
    p = np.random.choice(['healthy', 'moderate', 'unhealthy'], p=[0.3, 0.4, 0.3])
    if p == 'healthy':
        return _sample(
            np.random.uniform(8, 15), np.random.uniform(5, 12),
            np.random.uniform(2, 8), np.random.uniform(8, 15),
            np.random.uniform(350, 380), np.random.uniform(100, 350),
            0, np.random.choice([0, 1], p=[0.9, 0.1]), 0,
            np.random.randint(0, 1))
    elif p == 'moderate':
        return _sample(
            np.random.uniform(5, 10), np.random.uniform(12, 22),
            np.random.uniform(5, 12), np.random.uniform(4, 10),
            np.random.uniform(370, 410), np.random.uniform(200, 500),
            np.random.choice([0, 1], p=[0.7, 0.3]),
            np.random.choice([0, 1], p=[0.6, 0.4]),
            np.random.choice([0, 1], p=[0.95, 0.05]),
            np.random.randint(0, 3))
    else:
        return _sample(
            np.random.uniform(2, 6), np.random.uniform(25, 40),
            np.random.uniform(8, 15), np.random.uniform(1, 5),
            np.random.uniform(400, 450), np.random.uniform(400, 700),
            np.random.choice([0, 1], p=[0.5, 0.5]),
            np.random.choice([0, 1], p=[0.4, 0.6]),
            np.random.choice([0, 1], p=[0.8, 0.2]),
            np.random.randint(2, 5))


def _generate_biscuit_sample() -> Dict:
    """Biscuits & cookies: high fat/sugar category"""
    p = np.random.choice(['healthy', 'moderate', 'unhealthy'], p=[0.2, 0.4, 0.4])
    if p == 'healthy':
        return _sample(
            np.random.uniform(5, 10), np.random.uniform(5, 12),
            np.random.uniform(8, 15), np.random.uniform(3, 8),
            np.random.uniform(380, 430), np.random.uniform(200, 400),
            0, 0, 0, np.random.randint(0, 2))
    elif p == 'moderate':
        return _sample(
            np.random.uniform(3, 7), np.random.uniform(15, 25),
            np.random.uniform(15, 22), np.random.uniform(1, 4),
            np.random.uniform(430, 480), np.random.uniform(250, 500),
            np.random.choice([0, 1], p=[0.6, 0.4]),
            np.random.choice([0, 1], p=[0.4, 0.6]),
            np.random.choice([0, 1], p=[0.85, 0.15]),
            np.random.randint(1, 4))
    else:
        return _sample(
            np.random.uniform(2, 5), np.random.uniform(25, 40),
            np.random.uniform(22, 30), np.random.uniform(0, 2),
            np.random.uniform(480, 550), np.random.uniform(300, 600),
            np.random.choice([0, 1], p=[0.4, 0.6]),
            np.random.choice([0, 1], p=[0.2, 0.8]),
            np.random.choice([0, 1], p=[0.6, 0.4]),
            np.random.randint(2, 6))


def _generate_snack_sample() -> Dict:
    """Snacks (chips, namkeen, etc.): high sodium/fat"""
    p = np.random.choice(['healthy', 'moderate', 'unhealthy'], p=[0.2, 0.4, 0.4])
    if p == 'healthy':
        return _sample(
            np.random.uniform(5, 12), np.random.uniform(2, 6),
            np.random.uniform(8, 14), np.random.uniform(3, 8),
            np.random.uniform(380, 440), np.random.uniform(200, 450),
            0, np.random.choice([0, 1], p=[0.7, 0.3]), 0,
            np.random.randint(0, 2))
    elif p == 'moderate':
        return _sample(
            np.random.uniform(3, 8), np.random.uniform(3, 10),
            np.random.uniform(14, 22), np.random.uniform(1, 4),
            np.random.uniform(440, 500), np.random.uniform(450, 700),
            np.random.choice([0, 1], p=[0.7, 0.3]),
            np.random.choice([0, 1], p=[0.4, 0.6]),
            np.random.choice([0, 1], p=[0.8, 0.2]),
            np.random.randint(1, 4))
    else:
        return _sample(
            np.random.uniform(2, 5), np.random.uniform(5, 15),
            np.random.uniform(22, 35), np.random.uniform(0, 2),
            np.random.uniform(500, 580), np.random.uniform(700, 1200),
            np.random.choice([0, 1], p=[0.5, 0.5]),
            np.random.choice([0, 1], p=[0.2, 0.8]),
            np.random.choice([0, 1], p=[0.6, 0.4]),
            np.random.randint(3, 7))


def _generate_chocolate_sample() -> Dict:
    """Chocolates & confectionery: very high sugar/fat"""
    p = np.random.choice(['healthy', 'moderate', 'unhealthy'], p=[0.15, 0.35, 0.5])
    if p == 'healthy':
        return _sample(
            np.random.uniform(6, 12), np.random.uniform(15, 25),
            np.random.uniform(15, 25), np.random.uniform(2, 6),
            np.random.uniform(420, 480), np.random.uniform(30, 100),
            0, 0, 0, np.random.randint(0, 2))
    elif p == 'moderate':
        return _sample(
            np.random.uniform(3, 8), np.random.uniform(30, 45),
            np.random.uniform(25, 35), np.random.uniform(1, 3),
            np.random.uniform(480, 530), np.random.uniform(50, 150),
            np.random.choice([0, 1], p=[0.6, 0.4]),
            np.random.choice([0, 1], p=[0.5, 0.5]), 0,
            np.random.randint(1, 3))
    else:
        return _sample(
            np.random.uniform(2, 5), np.random.uniform(45, 65),
            np.random.uniform(30, 40), np.random.uniform(0, 2),
            np.random.uniform(520, 580), np.random.uniform(50, 200),
            np.random.choice([0, 1], p=[0.4, 0.6]),
            np.random.choice([0, 1], p=[0.3, 0.7]),
            np.random.choice([0, 1], p=[0.7, 0.3]),
            np.random.randint(2, 5))


def _generate_beverage_sample() -> Dict:
    """Beverages (juice, soda, etc.): per 100 ml"""
    p = np.random.choice(['healthy', 'moderate', 'unhealthy'], p=[0.35, 0.35, 0.3])
    if p == 'healthy':
        return _sample(
            np.random.uniform(0, 2), np.random.uniform(0, 3),
            np.random.uniform(0, 0.5), np.random.uniform(0, 1),
            np.random.uniform(5, 25), np.random.uniform(5, 100),
            0, 0, 0, 0)
    elif p == 'moderate':
        return _sample(
            np.random.uniform(0, 1), np.random.uniform(5, 10),
            np.random.uniform(0, 1), np.random.uniform(0, 0.5),
            np.random.uniform(25, 45), np.random.uniform(50, 200),
            np.random.choice([0, 1], p=[0.6, 0.4]),
            np.random.choice([0, 1], p=[0.6, 0.4]), 0,
            np.random.randint(0, 3))
    else:
        return _sample(
            np.random.uniform(0, 0.5), np.random.uniform(10, 16),
            np.random.uniform(0, 0.5), np.random.uniform(0, 0),
            np.random.uniform(40, 65), np.random.uniform(50, 250),
            np.random.choice([0, 1], p=[0.4, 0.6]),
            np.random.choice([0, 1], p=[0.3, 0.7]), 0,
            np.random.randint(2, 5))


def _generate_energy_drink_sample() -> Dict:
    """Energy drinks: typically high sugar, caffeine (per 100 ml)"""
    p = np.random.choice(['healthy', 'moderate', 'unhealthy'], p=[0.25, 0.35, 0.4])
    if p == 'healthy':
        return _sample(
            np.random.uniform(0, 1), np.random.uniform(0, 3),
            0, 0, np.random.uniform(5, 20),
            np.random.uniform(50, 200), 0, 0, 0, np.random.randint(0, 2))
    elif p == 'moderate':
        return _sample(
            np.random.uniform(0, 1), np.random.uniform(5, 10),
            0, 0, np.random.uniform(25, 50),
            np.random.uniform(100, 300),
            np.random.choice([0, 1], p=[0.5, 0.5]),
            np.random.choice([0, 1], p=[0.5, 0.5]), 0,
            np.random.randint(1, 3))
    else:
        return _sample(
            np.random.uniform(0, 0.5), np.random.uniform(10, 15),
            0, 0, np.random.uniform(45, 70),
            np.random.uniform(200, 400),
            np.random.choice([0, 1], p=[0.3, 0.7]),
            np.random.choice([0, 1], p=[0.2, 0.8]), 0,
            np.random.randint(2, 5))


def _generate_dairy_sample() -> Dict:
    """Dairy products (yogurt, flavored milk, cheese, etc.)"""
    p = np.random.choice(['healthy', 'moderate', 'unhealthy'], p=[0.35, 0.4, 0.25])
    if p == 'healthy':
        return _sample(
            np.random.uniform(5, 12), np.random.uniform(3, 6),
            np.random.uniform(1, 5), np.random.uniform(0, 2),
            np.random.uniform(50, 100), np.random.uniform(50, 250),
            0, 0, 0, np.random.randint(0, 1))
    elif p == 'moderate':
        return _sample(
            np.random.uniform(3, 7), np.random.uniform(8, 14),
            np.random.uniform(5, 10), np.random.uniform(0, 1),
            np.random.uniform(90, 150), np.random.uniform(150, 400),
            np.random.choice([0, 1], p=[0.6, 0.4]),
            np.random.choice([0, 1], p=[0.6, 0.4]), 0,
            np.random.randint(0, 3))
    else:
        return _sample(
            np.random.uniform(2, 5), np.random.uniform(15, 25),
            np.random.uniform(10, 18), np.random.uniform(0, 0.5),
            np.random.uniform(140, 220), np.random.uniform(300, 600),
            np.random.choice([0, 1], p=[0.4, 0.6]),
            np.random.choice([0, 1], p=[0.3, 0.7]),
            np.random.choice([0, 1], p=[0.85, 0.15]),
            np.random.randint(2, 5))


def _generate_instant_noodle_sample() -> Dict:
    """Instant noodles & ready-to-eat: high sodium"""
    p = np.random.choice(['healthy', 'moderate', 'unhealthy'], p=[0.15, 0.35, 0.5])
    if p == 'healthy':
        return _sample(
            np.random.uniform(8, 14), np.random.uniform(1, 4),
            np.random.uniform(5, 10), np.random.uniform(3, 7),
            np.random.uniform(300, 380), np.random.uniform(400, 600),
            0, np.random.choice([0, 1], p=[0.7, 0.3]), 0,
            np.random.randint(0, 2))
    elif p == 'moderate':
        return _sample(
            np.random.uniform(5, 9), np.random.uniform(2, 6),
            np.random.uniform(12, 18), np.random.uniform(1, 4),
            np.random.uniform(370, 440), np.random.uniform(700, 1000),
            np.random.choice([0, 1], p=[0.7, 0.3]),
            np.random.choice([0, 1], p=[0.3, 0.7]),
            np.random.choice([0, 1], p=[0.8, 0.2]),
            np.random.randint(1, 4))
    else:
        return _sample(
            np.random.uniform(3, 6), np.random.uniform(3, 8),
            np.random.uniform(18, 25), np.random.uniform(0, 2),
            np.random.uniform(430, 500), np.random.uniform(1000, 1800),
            np.random.choice([0, 1], p=[0.5, 0.5]),
            np.random.choice([0, 1], p=[0.2, 0.8]),
            np.random.choice([0, 1], p=[0.6, 0.4]),
            np.random.randint(3, 6))


def _generate_sauce_sample() -> Dict:
    """Sauces, condiments & spreads: high sodium and/or sugar"""
    p = np.random.choice(['healthy', 'moderate', 'unhealthy'], p=[0.25, 0.4, 0.35])
    if p == 'healthy':
        return _sample(
            np.random.uniform(1, 5), np.random.uniform(2, 8),
            np.random.uniform(2, 8), np.random.uniform(0, 2),
            np.random.uniform(50, 200), np.random.uniform(200, 500),
            0, np.random.choice([0, 1], p=[0.7, 0.3]), 0,
            np.random.randint(0, 2))
    elif p == 'moderate':
        return _sample(
            np.random.uniform(1, 3), np.random.uniform(10, 20),
            np.random.uniform(8, 18), np.random.uniform(0, 1),
            np.random.uniform(180, 300), np.random.uniform(500, 900),
            np.random.choice([0, 1], p=[0.6, 0.4]),
            np.random.choice([0, 1], p=[0.4, 0.6]), 0,
            np.random.randint(1, 3))
    else:
        return _sample(
            np.random.uniform(0, 2), np.random.uniform(20, 35),
            np.random.uniform(18, 30), np.random.uniform(0, 0.5),
            np.random.uniform(280, 400), np.random.uniform(800, 1500),
            np.random.choice([0, 1], p=[0.4, 0.6]),
            np.random.choice([0, 1], p=[0.2, 0.8]),
            np.random.choice([0, 1], p=[0.7, 0.3]),
            np.random.randint(2, 5))


def _generate_supplement_sample() -> Dict:
    """Health supplements & protein powders"""
    p = np.random.choice(['healthy', 'moderate', 'unhealthy'], p=[0.45, 0.35, 0.2])
    if p == 'healthy':
        return _sample(
            np.random.uniform(60, 85), np.random.uniform(1, 5),
            np.random.uniform(2, 8), np.random.uniform(2, 8),
            np.random.uniform(300, 380), np.random.uniform(100, 300),
            0, 0, 0, np.random.randint(0, 1))
    elif p == 'moderate':
        return _sample(
            np.random.uniform(30, 60), np.random.uniform(5, 12),
            np.random.uniform(5, 12), np.random.uniform(1, 5),
            np.random.uniform(350, 420), np.random.uniform(200, 500),
            np.random.choice([0, 1], p=[0.5, 0.5]),
            np.random.choice([0, 1], p=[0.6, 0.4]), 0,
            np.random.randint(0, 3))
    else:
        return _sample(
            np.random.uniform(15, 30), np.random.uniform(12, 25),
            np.random.uniform(10, 18), np.random.uniform(0, 3),
            np.random.uniform(400, 480), np.random.uniform(300, 600),
            np.random.choice([0, 1], p=[0.3, 0.7]),
            np.random.choice([0, 1], p=[0.3, 0.7]),
            np.random.choice([0, 1], p=[0.8, 0.2]),
            np.random.randint(2, 5))


def _generate_frozen_food_sample() -> Dict:
    """Frozen foods (pizzas, ready meals, etc.)"""
    p = np.random.choice(['healthy', 'moderate', 'unhealthy'], p=[0.2, 0.4, 0.4])
    if p == 'healthy':
        return _sample(
            np.random.uniform(8, 15), np.random.uniform(2, 5),
            np.random.uniform(5, 10), np.random.uniform(3, 7),
            np.random.uniform(150, 250), np.random.uniform(250, 500),
            0, np.random.choice([0, 1], p=[0.6, 0.4]), 0,
            np.random.randint(0, 2))
    elif p == 'moderate':
        return _sample(
            np.random.uniform(5, 10), np.random.uniform(4, 8),
            np.random.uniform(10, 18), np.random.uniform(1, 4),
            np.random.uniform(230, 320), np.random.uniform(500, 800),
            np.random.choice([0, 1], p=[0.7, 0.3]),
            np.random.choice([0, 1], p=[0.3, 0.7]),
            np.random.choice([0, 1], p=[0.8, 0.2]),
            np.random.randint(1, 4))
    else:
        return _sample(
            np.random.uniform(3, 7), np.random.uniform(6, 14),
            np.random.uniform(18, 28), np.random.uniform(0, 2),
            np.random.uniform(300, 400), np.random.uniform(800, 1200),
            np.random.choice([0, 1], p=[0.5, 0.5]),
            np.random.choice([0, 1], p=[0.2, 0.8]),
            np.random.choice([0, 1], p=[0.6, 0.4]),
            np.random.randint(3, 6))


# ─── Scoring ────────────────────────────────────────────────────────────────

def _calculate_health_score(row: pd.Series) -> float:
    """
    Calculate health score (0-100) based on nutritional values.
    Uses FSSAI and WHO guidelines.  Category-aware scoring.
    """
    score = 50  # Start neutral
    cat = row['category']

    # ── Protein scoring ────────────────────────────────────────────
    prot = row['protein_per_100g']
    if cat in ('PROTEIN_BAR', 'HEALTH_SUPPLEMENTS'):
        if prot >= 25: score += 15
        elif prot >= 20: score += 10
        elif prot >= 15: score += 5
        elif prot < 10: score -= 5
    elif cat in ('BEVERAGES', 'ENERGY_DRINKS'):
        if prot >= 5: score += 5
    else:
        if prot >= 12: score += 12
        elif prot >= 8: score += 8
        elif prot >= 5: score += 4

    # ── Sugar scoring (penalty for excess) ────────────────────────
    sug = row['sugar_per_100g']
    if cat == 'CHOCOLATES_CONFECTIONERY':
        # Chocolate inherently high sugar — use looser scale
        if   sug <= 20: score += 10
        elif sug <= 35: score += 3
        elif sug <= 50: score -= 5
        else:           score -= 12
    elif cat in ('BEVERAGES', 'ENERGY_DRINKS'):
        if   sug <= 2: score += 15
        elif sug <= 5: score += 8
        elif sug <= 8: score += 2
        else:          score -= 12
    else:
        if   sug <= 5:  score += 15
        elif sug <= 10: score += 8
        elif sug <= 15: score += 2
        elif sug <= 22: score -= 5
        else:           score -= 15

    # ── Fiber scoring ─────────────────────────────────────────────
    fib = row['fiber_per_100g']
    if cat not in ('BEVERAGES', 'ENERGY_DRINKS', 'DAIRY_PRODUCTS'):
        if   fib >= 10: score += 12
        elif fib >= 6:  score += 8
        elif fib >= 3:  score += 4
        elif fib < 2:   score -= 5

    # ── Fat scoring ───────────────────────────────────────────────
    fat = row['fat_per_100g']
    if cat in ('BEVERAGES', 'ENERGY_DRINKS'):
        pass  # fat not meaningful here
    elif cat == 'CHOCOLATES_CONFECTIONERY':
        if   fat <= 20: score += 4
        elif fat >= 35: score -= 8
    else:
        if   fat <= 5:  score += 8
        elif fat <= 10: score += 4
        elif fat <= 15: pass
        elif fat <= 20: score -= 5
        else:           score -= 10

    # ── Sodium scoring (new) ─────────────────────────────────────
    sod = row.get('sodium_per_100g', 0) or 0
    if cat in ('INSTANT_NOODLES_RTE', 'SAUCES_SPREADS', 'SNACKS'):
        # these categories are inherently high-sodium
        if   sod <= 300: score += 8
        elif sod <= 600: score += 3
        elif sod >= 1000: score -= 10
    else:
        if   sod <= 200: score += 5
        elif sod >= 600: score -= 5

    # ── Calorie scoring ──────────────────────────────────────────
    cal = row['calories_per_100g']
    if cat in ('BEVERAGES', 'ENERGY_DRINKS'):
        if cal <= 20: score += 5
        elif cal >= 50: score -= 5
    else:
        if cal <= 350: score += 5
        elif cal >= 450: score -= 5

    # ── Ingredient-flag penalties ────────────────────────────────
    if row['has_artificial_sweetener']:
        score -= 8
    if row['has_preservatives']:
        score -= 5
    if row['has_trans_fat']:
        score -= 15

    # Ingredient risk count penalty (new)
    risk_count = row.get('ingredient_risk_count', 0) or 0
    score -= risk_count * 2  # 2-pt penalty per risky ingredient

    return max(0, min(100, score))


def _generate_risk_labels(row: pd.Series) -> str:
    """Generate risk labels based on nutritional analysis"""
    risks = []

    if row['sugar_per_100g'] > 20:
        risks.append('HIGH_SUGAR')
    if row['fat_per_100g'] > 18:
        risks.append('HIGH_FAT')
    if row['has_trans_fat']:
        risks.append('TRANS_FAT')
    if row['has_artificial_sweetener']:
        risks.append('ARTIFICIAL_SWEETENER')
    if row['has_preservatives']:
        risks.append('PRESERVATIVES')
    if row['fiber_per_100g'] < 2:
        risks.append('LOW_FIBER')
    if row['calories_per_100g'] > 450:
        risks.append('HIGH_CALORIE')

    sod = row.get('sodium_per_100g', 0) or 0
    if sod > 800:
        risks.append('HIGH_SODIUM')

    risk_count = row.get('ingredient_risk_count', 0) or 0
    if risk_count >= 3:
        risks.append('MANY_RISKY_INGREDIENTS')

    return ','.join(risks) if risks else 'NONE'


if __name__ == '__main__':
    # Generate and save training data
    df = generate_training_data('data/training_data.csv', n_samples=3000)
    print(f"Generated {len(df)} samples")
    print(f"Categories: {df['category'].value_counts().to_dict()}")
    print(df.describe())
