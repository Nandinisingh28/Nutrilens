"""
Verification tests for OCR text cleaning and nutrition parser fixes.

Tests:
1. OCR text cleaning (_clean_text) with known error patterns
2. Nutrition parser with edge-case values (< 0.5, Not more than, etc.)
3. Nutrition parser with cleaned OCR text from the bug report

Run: python scripts/test_ocr_fixes.py
"""

import sys
import os
from unittest.mock import MagicMock

# Stub out heavy dependencies before importing any app modules
sys.modules['fastapi'] = MagicMock()
sys.modules['sqlalchemy'] = MagicMock()
sys.modules['sqlalchemy.ext.asyncio'] = MagicMock()
sys.modules['sqlalchemy.orm'] = MagicMock()
sys.modules['app.core.config'] = MagicMock()

# Mock settings with TESSERACT_PATH
mock_settings = MagicMock()
mock_settings.TESSERACT_PATH = None
sys.modules['app.core.config'].settings = mock_settings

sys.modules['app.core.logging'] = MagicMock()
# Make get_logger return a real-ish logger
import logging
sys.modules['app.core.logging'].get_logger = lambda name: logging.getLogger(name)

sys.modules['app.db'] = MagicMock()
sys.modules['app.core.exceptions'] = MagicMock()
sys.modules['app.main'] = MagicMock()
sys.modules['pytesseract'] = MagicMock()

# Need to mock cv2 and numpy are real, PIL is real
# But image_preprocessor needs cv2 — let's just test the parts that don't need it

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

passed = 0
failed = 0

def test(name, actual, expected):
    global passed, failed
    if actual == expected:
        print(f"  ✅ {name}")
        passed += 1
    else:
        print(f"  ❌ {name}")
        print(f"     Expected: {expected!r}")
        print(f"     Got:      {actual!r}")
        failed += 1

def test_contains(name, text, substring):
    global passed, failed
    if substring.lower() in text.lower():
        print(f"  ✅ {name}")
        passed += 1
    else:
        print(f"  ❌ {name}: '{substring}' not found in text")
        failed += 1

# ═══════════════════════════════════════════════════════════════════
# Test 1: OCR text cleaning
# ═══════════════════════════════════════════════════════════════════
print("\n══ Test 1: OCR Text Cleaning ══")

from app.services.ocr_service import OCRService
ocr = OCRService()

# Unit confusions
test("(9) → (g)", ocr._clean_text("Protein (9)"), "Protein (g)")
test("(G) → (g)", ocr._clean_text("Protein (G)"), "Protein (g)")
test("(o) → (g)", ocr._clean_text("Sugar (o)"), "Sugar (g)")

# Nutrient name corrections
test("Sugers → Sugars", ocr._clean_text("Total Sugers"), "Total Sugars")
test("Carboryoraio → Carbohydrate", ocr._clean_text("Carboryoraio"), "Carbohydrate")
test("Saturatod → Saturated", ocr._clean_text("Saturatod Fat"), "Saturated Fat")
test("a rated → Saturated", ocr._clean_text("a rated Fat"), "Saturated Fat")
test("Sodlum → Sodium", ocr._clean_text("Sodlum"), "Sodium")
test("Proteln → Protein", ocr._clean_text("Proteln"), "Protein")

# Number fixes
test("lOO → 100", ocr._clean_text("per lOOg"), "per 100g")
test("l00 → 100", ocr._clean_text("per l00g"), "per 100g")

# kcal fixes
test("kcaI → kcal", ocr._clean_text("100 kcaI"), "100 kcal")


# ═══════════════════════════════════════════════════════════════════
# Test 2: Nutrition parser - edge-case values
# ═══════════════════════════════════════════════════════════════════
print("\n══ Test 2: Nutrition Parser Edge Cases ══")

from app.services.nutrition_parser import NutritionParser
parser = NutritionParser()

# Test "less than" values
lt_text = """
Nutritional Information Per 100g
Energy (kcal) 141.9
Protein (g) 3.06
Total Sugars (g) < 0.5
Added Sugars (g) 0
Total Fat (g) 3.54
Saturated Fat (g) Not more than 1.72
Trans Fat (g) Not more than 0.1
Sodium (mg) 29.48
"""

result = parser.parse(lt_text)
vals = result["values"]

test("Energy parsed", vals.get("energy"), 141.9)
test("Protein parsed", vals.get("protein"), 3.06)
test("Sugar < 0.5 parsed", vals.get("sugar"), 0.5)
test("Added sugar parsed", vals.get("added_sugar"), 0.0)
test("Fat parsed", vals.get("fat"), 3.54)
test("Saturated fat parsed", vals.get("saturated_fat"), 1.72)
test("Trans fat parsed", vals.get("trans_fat"), 0.1)
test("Sodium parsed", vals.get("sodium"), 29.48)


# ═══════════════════════════════════════════════════════════════════
# Test 3: Nutrition parser with cleaned OCR text (simulated)
# ═══════════════════════════════════════════════════════════════════
print("\n══ Test 3: Parser with Cleaned OCR Text ══")

# Simulate what _clean_text would produce from the bug report's OCR output
raw_ocr = """Nutritional Information 750 g Pack contains about 7.5 serves
(Frozen Product) Serving Size 100 g

Per Serve %
Per 100 g contribution to RDA
Energy (kcal) 141.9 7.1
Protein (g) 3.06 -
Carbohydrate (g) 24.45 -
Total Sugars (g) < 0.5 -
Added Sugars (g) 0 0
Total Fat (g) 3.54 5.3
Saturated Fat (g) Not more than 1.72 7.8
Trans Fat (g) Not more than 0.1 < 5
Sodium (mg) 29.48 1.5
"""

result2 = parser.parse(raw_ocr)
vals2 = result2["values"]

print(f"  Reference detected: {result2['reference']}")
print(f"  Nutrients found: {list(vals2.keys())}")

test("Energy from label", vals2.get("energy"), 141.9)
test("Protein from label", vals2.get("protein"), 3.06)
test("Carbs from label", vals2.get("carbohydrates"), 24.45)
test("Fat from label", vals2.get("fat"), 3.54)
test("Sodium from label", vals2.get("sodium"), 29.48)

# These use "less than" / "not more than" patterns
sugar_val = vals2.get("sugar")
if sugar_val is not None:
    test("Sugar < 0.5 from label", sugar_val, 0.5)
else:
    test("Sugar detected at all", sugar_val is not None, True)

sat_fat_val = vals2.get("saturated_fat")
if sat_fat_val is not None:
    test("Saturated fat from label", sat_fat_val, 1.72)
else:
    test("Saturated fat detected at all", sat_fat_val is not None, True)


# ═══════════════════════════════════════════════════════════════════
# Test 4: _clean_text full pipeline on bug report text
# ═══════════════════════════════════════════════════════════════════
print("\n══ Test 4: Full Clean Pipeline ══")

# The actual OCR garbage from the bug report
ocr_garbage = """Nutritional Information 750 g Pack contains about 7.5 serves
(Frozen Product) Serving Size 100 g

Per Serve %
Per 100 g contribution to RDA
Energy (kcal) 4190 A
fs Protein (9) EX ee
Carboryoraio(G) aus

Total Sugers(o) /05[-
Added Sugars (9) a [
Total Fat (g) 3.54

a rated Fat (g) in more than } 79"""

cleaned = ocr._clean_text(ocr_garbage)
print(f"  Cleaned text preview:\n{cleaned[:500]}\n")

test_contains("Protein (g) present", cleaned, "Protein (g)")
test_contains("Carbohydrate present", cleaned, "Carbohydrate")
test_contains("Sugars present", cleaned, "Sugars")
test_contains("Saturated present", cleaned, "Saturated")


# ═══════════════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════════════
print(f"\n{'═' * 50}")
print(f"Results: {passed} passed, {failed} failed out of {passed + failed} tests")
if failed == 0:
    print("🎉 All tests passed!")
else:
    print(f"⚠️  {failed} test(s) failed")
    sys.exit(1)
