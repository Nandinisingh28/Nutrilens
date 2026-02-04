"""
Simple test for scan API.
"""
import requests
import io
import json
from PIL import Image, ImageDraw

# Create a test nutrition label image
def create_test_label():
    img = Image.new('RGB', (400, 600), color='white')
    draw = ImageDraw.Draw(img)
    text = """NUTRITION FACTS
Per 100g
Protein: 25g
Sugars: 8g
HIGH PROTEIN
LOW SUGAR
INGREDIENTS:
wheat, whey protein,
glucose syrup, salt"""
    draw.text((20, 20), text, fill='black')
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    buffer.seek(0)
    return buffer

# Login
resp = requests.post(
    "http://localhost:8000/api/auth/login",
    json={"email": "test2@example.com", "password": "TestPass123"}
)
token = resp.json()["data"]["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get category
resp = requests.get("http://localhost:8000/api/categories", headers=headers)
categories = resp.json()["data"]
if not categories:
    print("No categories!")
    exit(1)
cat_id = categories[0]["id"]

# Submit scan
img = create_test_label()
resp = requests.post(
    "http://localhost:8000/api/scans",
    headers=headers,
    files={"image": ("test.jpg", img, "image/jpeg")},
    data={
        "category_id": cat_id,
        "claim_text": "high protein, low sugar",
        "product_name": "Test Bar",
    }
)

result = resp.json()
print(json.dumps(result, indent=2))
