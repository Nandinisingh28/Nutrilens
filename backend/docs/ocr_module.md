# OCR Module – NutriLens

## Objective
The OCR module in NutriLens is responsible for accurately extracting **ingredients, nutrition facts, and claim-related text** from food product label images. This extracted text forms the foundation for all downstream claim verification logic.

---

## Why OCR is Critical in NutriLens
Food claim verification cannot be performed reliably without structured textual data. Since most food labels are images, OCR acts as the **entry gate** to the entire pipeline.

If OCR fails or returns incomplete text:
- Ingredient parsing becomes unreliable
- Claim analysis is halted
- False positives are avoided intentionally

Therefore, NutriLens prioritizes **OCR correctness over speed**.

---

## OCR Pipeline Design

### Step 1: Image Upload & Validation
- **Formats**: `.jpg`, `.jpeg`, `.png`, `.webp`
- **Validation**: System checks for file size (max 10MB) and presence of image data.

### Step 2: Quality Guard & Validation (Reliability Layer)
To ensure high-fidelity analysis, the system performs an immediate quality check on the extracted text:
- **Confidence Threshold**: Any scan with an average OCR confidence below **40%** is rejected as "too blurry."
- **Content Minimums**: A minimum of **20 characters** must be extracted to prevent empty or invalid scans from proceeding.
- **Fail-Fast**: If validation fails, downstream parsing (ingredients/claims) is **not triggered**, and the user is provided with a "retake photo" option.

### Step 3: Dual-Image (Precision) Mode
For labels where text is curved or split, the system supports a separate pipeline:
- **Segments**: Ingredients and Nutrition facts are scanned independently.
- **Independence**: Each image undergoes its own confidence validation.

---

## Technical Stack
- **Engine**: Tesseract OCR (`pytesseract`)
- **Preprocessing**: OpenCV & PIL (noise reduction, thresholding, grayscale)
- **Error Codes**: `OCR_QUALITY_LOW` (422 Unprocessable Entity)
