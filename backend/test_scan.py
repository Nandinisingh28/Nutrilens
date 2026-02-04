"""
Test script for the scan pipeline.
"""

import requests
import io
from PIL import Image, ImageDraw, ImageFont

# Create a test nutrition label image
def create_test_label():
    """Create a simple test nutrition label image."""
    img = Image.new('RGB', (400, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Add text
    text = """
    NUTRITION FACTS
    Serving Size: 50g
    
    Per 100g
    Energy: 450 kcal
    Protein: 25g
    Total Carbohydrates: 35g
    of which Sugars: 8g
    Total Fat: 15g
    Saturated Fat: 5g
    Fiber: 6g
    Sodium: 200mg
    
    INGREDIENTS:
    Whole wheat flour, whey protein,
    glucose syrup, cocoa, palm oil,
    natural flavors, salt
    
    HIGH PROTEIN
    LOW SUGAR
    """
    
    draw.text((20, 20), text, fill='black')
    
    # Save to bytes
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    buffer.seek(0)
    return buffer

def test_scan_pipeline():
    """Test the full scan pipeline."""
    base_url = "http://localhost:8000"
    
    # 1. Login
    print("1. Logging in...")
    response = requests.post(
        f"{base_url}/api/auth/login",
        json={"email": "test2@example.com", "password": "TestPass123"}
    )
    
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
    
    token = response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"   Token: {token[:50]}...")
    
    # 2. Get categories
    print("\n2. Getting categories...")
    response = requests.get(f"{base_url}/api/categories", headers=headers)
    categories = response.json()["data"]
    print(f"   Categories: {[c['title'] for c in categories]}")
    
    if not categories:
        print("   No categories found!")
        return
    
    category_id = categories[0]["id"]
    
    # 3. Create test image
    print("\n3. Creating test label image...")
    image_buffer = create_test_label()
    
    # 4. Submit scan
    print("\n4. Submitting scan...")
    response = requests.post(
        f"{base_url}/api/scans",
        headers=headers,
        files={"image": ("test_label.jpg", image_buffer, "image/jpeg")},
        data={
            "category_id": category_id,
            "claim_text": "high protein, low sugar",
            "product_name": "Test Protein Bar",
            "brand": "TestBrand",
        }
    )
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   Error: {response.text}")
        return
    
    result = response.json()
    print(f"   Success: {result['success']}")
    print(f"   Message: {result['message']}")
    
    if result.get("data"):
        data = result["data"]
        print(f"\n   Scan ID: {data.get('id')}")
        print(f"   Overall Verdict: {data.get('overall_verdict')}")
        
        if data.get("results"):
            results = data["results"]
            
            # OCR
            if results.get("ocr"):
                print(f"\n   OCR Confidence: {results['ocr'].get('confidence')}")
                print(f"   Word Count: {results['ocr'].get('word_count')}")
            
            # Claims
            if results.get("claims"):
                print(f"\n   Claims Verified: {len(results['claims'])}")
                for claim in results["claims"]:
                    print(f"     - {claim['claim']}: {claim['verdict']} ({claim['confidence']})")
            
            # Overall
            if results.get("overall"):
                overall = results["overall"]
                print(f"\n   Overall: {overall.get('verdict')} (confidence: {overall.get('confidence')})")
                print(f"   Summary: {overall.get('summary')}")

if __name__ == "__main__":
    test_scan_pipeline()
