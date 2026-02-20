"""
Scan Router - Food Label Analysis Endpoints
"""
import os
import uuid
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.scan import (
    Scan, ScanImage, ExtractedNutrition, ExtractedIngredients, ClaimResult,
    ProductCategory, ScanMode, ImageType, Verdict as ModelVerdict
)
from app.schemas.scan import (
    ScanResponse, ScanHistoryItem, NutritionData, ClaimResultResponse,
    ProductCategory as SchemaCategory, Verdict
)
from app.services.auth import get_current_user
from app.services.ocr import OCRExtractor, NutritionParser, IngredientsParser
from app.services.verification import ClaimVerificationEngine
from app.config import get_settings

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter(prefix="/scans", tags=["Scans"])

settings = get_settings()

# Allowed image types
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'bmp'}


def allowed_file(filename: str) -> bool:
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


async def save_upload(file: UploadFile) -> str:
    """Save uploaded file and return path"""
    if not file.filename or not allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Generate unique filename
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4()}.{ext}"
    
    # Ensure upload directory exists
    os.makedirs(settings.upload_dir, exist_ok=True)
    
    filepath = os.path.join(settings.upload_dir, filename)
    
    # Save file
    content = await file.read()
    
    if len(content) > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.max_file_size // (1024*1024)}MB"
        )
    
    with open(filepath, 'wb') as f:
        f.write(content)
    
    return filepath


@router.post("/precision", response_model=ScanResponse)
async def precision_scan(
    nutrition_image: UploadFile = File(..., description="Image of nutrition facts label"),
    ingredients_image: UploadFile = File(..., description="Image of ingredients list"),
    claim: str = Form(..., description="Claim to verify (e.g., 'High Protein and Low Sugar')"),
    category: str = Form(..., description="Product category: PROTEIN_BAR or BREAKFAST_CEREAL"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Precision Scan - Upload separate images for nutrition facts and ingredients.
    
    This mode provides the most accurate results by using dedicated images
    for each section of the food label.
    
    - **nutrition_image**: Clear photo of the nutrition facts table
    - **ingredients_image**: Clear photo of the ingredients list
    - **claim**: The marketing claim to verify
    - **category**: PROTEIN_BAR or BREAKFAST_CEREAL
    """
    
    # Validate category
    category_upper = category.upper()
    try:
        product_category = ProductCategory(category_upper)
    except ValueError:
        valid = ', '.join(c.value for c in ProductCategory)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category. Must be one of: {valid}"
        )
    
    # Save images
    nutrition_path = await save_upload(nutrition_image)
    ingredients_path = await save_upload(ingredients_image)
    
    try:
        # Read image contents
        with open(nutrition_path, 'rb') as f:
            nutrition_bytes = f.read()
        with open(ingredients_path, 'rb') as f:
            ingredients_bytes = f.read()
        
        # Initialize services
        ocr_extractor = OCRExtractor()
        nutrition_parser = NutritionParser()
        ingredients_parser = IngredientsParser(db=db)
        verification_engine = ClaimVerificationEngine(db=db)
        
        # Extract text from images
        nutrition_text = ocr_extractor.extract_nutrition_only(nutrition_bytes)
        ingredients_text = ocr_extractor.extract_ingredients_only(ingredients_bytes)
        
        # Parse extracted text
        nutrition_info = nutrition_parser.parse(nutrition_text, category)
        ingredients_info = ingredients_parser.parse(ingredients_text)
        
        # Verify claim
        verification_result = verification_engine.verify(
            claim=claim,
            category=category,
            nutrition=nutrition_info,
            ingredients=ingredients_info
        )
        
        # Create scan record
        scan = Scan(
            user_id=current_user.id,
            category=product_category,
            scan_mode=ScanMode.PRECISION,
            user_claim=claim,
            final_verdict=ModelVerdict(verification_result.final_verdict.value),
            score=verification_result.score,
            explanation=verification_result.explanation
        )
        db.add(scan)
        db.flush()
        
        # Save image records
        db.add(ScanImage(
            scan_id=scan.id,
            image_type=ImageType.NUTRITION,
            file_path=nutrition_path
        ))
        db.add(ScanImage(
            scan_id=scan.id,
            image_type=ImageType.INGREDIENTS,
            file_path=ingredients_path
        ))
        
        # Save nutrition data
        db.add(ExtractedNutrition(
            scan_id=scan.id,
            serving_size=nutrition_info.serving_size,
            protein_per_100g=nutrition_info.protein_per_100g,
            sugar_per_100g=nutrition_info.sugar_per_100g,
            fat_per_100g=nutrition_info.fat_per_100g,
            fiber_per_100g=nutrition_info.fiber_per_100g,
            calories_per_100g=nutrition_info.calories_per_100g,
            sodium_per_100g=nutrition_info.sodium_per_100g,
            raw_text=nutrition_info.raw_text
        ))
        
        # Save ingredients data
        db.add(ExtractedIngredients(
            scan_id=scan.id,
            ingredients_list=', '.join(ingredients_info.ingredients_list),
            flagged_ingredients=ingredients_info.flagged_ingredients,
            raw_text=ingredients_info.raw_text
        ))
        
        # Save claim results
        for sub_claim in verification_result.sub_claims:
            db.add(ClaimResult(
                scan_id=scan.id,
                claim_type=sub_claim.claim_type,
                sub_claim=sub_claim.display_name,
                verdict=ModelVerdict(sub_claim.verdict.value),
                reason=sub_claim.reason
            ))
        
        db.commit()
        
        # Build response
        return ScanResponse(
            scan_id=scan.id,
            category=SchemaCategory(product_category.value),
            scan_mode=ScanMode.PRECISION,
            user_claim=claim,
            verdict=Verdict(verification_result.final_verdict.value),
            score=verification_result.score,
            explanation=verification_result.explanation,
            nutrition=NutritionData(
                serving_size=nutrition_info.serving_size,
                protein=nutrition_info.protein_per_100g,
                sugar=nutrition_info.sugar_per_100g,
                fat=nutrition_info.fat_per_100g,
                fiber=nutrition_info.fiber_per_100g,
                calories=nutrition_info.calories_per_100g,
                sodium=nutrition_info.sodium_per_100g
            ),
            ingredient_warnings=verification_result.ingredient_warnings,
            sub_claims=[
                ClaimResultResponse(
                    claim_type=sc.claim_type,
                    sub_claim=sc.display_name,
                    verdict=Verdict(sc.verdict.value),
                    reason=sc.reason
                )
                for sc in verification_result.sub_claims
            ],
            created_at=scan.created_at
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing scan: {str(e)}"
        )


@router.post("/quick", response_model=ScanResponse)
async def quick_scan(
    image: UploadFile = File(..., description="Image containing both nutrition facts and ingredients"),
    claim: str = Form(..., description="Claim to verify"),
    category: str = Form(..., description="Product category: PROTEIN_BAR or BREAKFAST_CEREAL"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Quick Scan - Upload a single image containing both nutrition facts and ingredients.
    
    This mode is convenient but may be less accurate than Precision Scan.
    The system will automatically detect and separate the nutrition and
    ingredients sections.
    
    - **image**: Photo containing both nutrition facts and ingredients
    - **claim**: The marketing claim to verify
    - **category**: PROTEIN_BAR or BREAKFAST_CEREAL
    """
    
    # Validate category
    category_upper = category.upper()
    try:
        product_category = ProductCategory(category_upper)
    except ValueError:
        valid = ', '.join(c.value for c in ProductCategory)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category. Must be one of: {valid}"
        )
    
    # Save image
    image_path = await save_upload(image)
    
    try:
        # Read image content
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        
        # Initialize services
        ocr_extractor = OCRExtractor()
        nutrition_parser = NutritionParser()
        ingredients_parser = IngredientsParser(db=db)
        verification_engine = ClaimVerificationEngine(db=db)
        
        # Extract both sections from single image
        extracted = ocr_extractor.extract_from_image(image_bytes)
        
        # Debug logging
        logger.info("=" * 60)
        logger.info("OCR EXTRACTION DEBUG")
        logger.info("=" * 60)
        logger.info(f"Full text extracted ({len(extracted.get('full_text', ''))} chars):")
        logger.info(extracted.get('full_text', '')[:2000])
        logger.info("-" * 40)
        if 'debug_info' in extracted:
            logger.info(f"Best preprocessing mode: {extracted['debug_info'].get('best_mode')}")
            logger.info(f"Anchors found: {extracted['debug_info'].get('anchors_found')}")
        logger.info("=" * 60)
        
        # Parse extracted text
        nutrition_info = nutrition_parser.parse(extracted['nutrition_text'], category)
        ingredients_info = ingredients_parser.parse(extracted['ingredients_text'])
        
        # Log parsed values
        logger.info("PARSED NUTRITION:")
        logger.info(f"  Protein: {nutrition_info.protein_per_100g}")
        logger.info(f"  Sugar: {nutrition_info.sugar_per_100g}")
        logger.info(f"  Fat: {nutrition_info.fat_per_100g}")
        logger.info(f"  Calories: {nutrition_info.calories_per_100g}")
        if hasattr(nutrition_info, 'debug_matches'):
            logger.info(f"  Debug matches: {nutrition_info.debug_matches}")
        logger.info("=" * 60)
        
        # Verify claim
        verification_result = verification_engine.verify(
            claim=claim,
            category=category,
            nutrition=nutrition_info,
            ingredients=ingredients_info
        )
        
        # Create scan record
        scan = Scan(
            user_id=current_user.id,
            category=product_category,
            scan_mode=ScanMode.QUICK,
            user_claim=claim,
            final_verdict=ModelVerdict(verification_result.final_verdict.value),
            score=verification_result.score,
            explanation=verification_result.explanation
        )
        db.add(scan)
        db.flush()
        
        # Save image record
        db.add(ScanImage(
            scan_id=scan.id,
            image_type=ImageType.COMBINED,
            file_path=image_path
        ))
        
        # Save nutrition data
        db.add(ExtractedNutrition(
            scan_id=scan.id,
            serving_size=nutrition_info.serving_size,
            protein_per_100g=nutrition_info.protein_per_100g,
            sugar_per_100g=nutrition_info.sugar_per_100g,
            fat_per_100g=nutrition_info.fat_per_100g,
            fiber_per_100g=nutrition_info.fiber_per_100g,
            calories_per_100g=nutrition_info.calories_per_100g,
            sodium_per_100g=nutrition_info.sodium_per_100g,
            raw_text=nutrition_info.raw_text
        ))
        
        # Save ingredients data
        db.add(ExtractedIngredients(
            scan_id=scan.id,
            ingredients_list=', '.join(ingredients_info.ingredients_list),
            flagged_ingredients=ingredients_info.flagged_ingredients,
            raw_text=ingredients_info.raw_text
        ))
        
        # Save claim results
        for sub_claim in verification_result.sub_claims:
            db.add(ClaimResult(
                scan_id=scan.id,
                claim_type=sub_claim.claim_type,
                sub_claim=sub_claim.display_name,
                verdict=ModelVerdict(sub_claim.verdict.value),
                reason=sub_claim.reason
            ))
        
        db.commit()
        
        # Build response
        return ScanResponse(
            scan_id=scan.id,
            category=SchemaCategory(product_category.value),
            scan_mode=ScanMode.QUICK,
            user_claim=claim,
            verdict=Verdict(verification_result.final_verdict.value),
            score=verification_result.score,
            explanation=verification_result.explanation,
            nutrition=NutritionData(
                serving_size=nutrition_info.serving_size,
                protein=nutrition_info.protein_per_100g,
                sugar=nutrition_info.sugar_per_100g,
                fat=nutrition_info.fat_per_100g,
                fiber=nutrition_info.fiber_per_100g,
                calories=nutrition_info.calories_per_100g,
                sodium=nutrition_info.sodium_per_100g
            ),
            ingredient_warnings=verification_result.ingredient_warnings,
            sub_claims=[
                ClaimResultResponse(
                    claim_type=sc.claim_type,
                    sub_claim=sc.display_name,
                    verdict=Verdict(sc.verdict.value),
                    reason=sc.reason
                )
                for sc in verification_result.sub_claims
            ],
            created_at=scan.created_at
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing scan: {str(e)}"
        )


@router.get("/history", response_model=List[ScanHistoryItem])
async def get_scan_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get scan history for the current user.
    
    Returns a list of all past scans, ordered by creation date (newest first).
    If the user has no scans, returns an empty array.
    """
    scans = db.query(Scan).filter(
        Scan.user_id == current_user.id
    ).order_by(Scan.created_at.desc()).all()
    
    return [
        ScanHistoryItem(
            scan_id=scan.id,
            category=SchemaCategory(scan.category),
            scan_mode=scan.scan_mode,
            user_claim=scan.user_claim,
            final_verdict=Verdict(scan.final_verdict.value) if scan.final_verdict else None,
            score=scan.score,
            created_at=scan.created_at
        )
        for scan in scans
    ]


@router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan_details(
    scan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed results for a specific scan.
    
    - **scan_id**: ID of the scan to retrieve
    
    Returns the full scan result including nutrition data, ingredient warnings,
    and sub-claim breakdowns.
    """
    scan = db.query(Scan).filter(
        Scan.id == scan_id,
        Scan.user_id == current_user.id
    ).first()
    
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    
    # Get related data
    nutrition = scan.nutrition
    claim_results = scan.claim_results
    ingredients = scan.ingredients
    
    # Build nutrition data
    nutrition_data = None
    if nutrition:
        nutrition_data = NutritionData(
            serving_size=nutrition.serving_size,
            protein=nutrition.protein_per_100g,
            sugar=nutrition.sugar_per_100g,
            fat=nutrition.fat_per_100g,
            fiber=nutrition.fiber_per_100g,
            calories=nutrition.calories_per_100g,
            sodium=nutrition.sodium_per_100g
        )
    
    # Build ingredient warnings
    ingredient_warnings = []
    if ingredients and ingredients.flagged_ingredients:
        for flagged in ingredients.flagged_ingredients:
            ingredient_warnings.append(
                f"{flagged.get('ingredient', '').title()}: {flagged.get('concern', '')}"
            )
    
    # Build sub-claims
    sub_claims = [
        ClaimResultResponse(
            claim_type=cr.claim_type,
            sub_claim=cr.sub_claim,
            verdict=Verdict(cr.verdict.value),
            reason=cr.reason
        )
        for cr in claim_results
    ]
    
    # Get raw OCR text for debugging
    ocr_nutrition_text = nutrition.raw_text if nutrition else None
    ocr_ingredients_text = ingredients.raw_text if ingredients else None
    
    # Calculate health score if nutrition data is available
    health_score = 0
    if nutrition_data:
        try:
            from app.services.ml.model import get_health_model
            health_model = get_health_model()
            
            # Prepare nutrition dict
            nut_dict = nutrition.to_dict()
            # Rename keys to match model expectation if needed (model expects _per_100g keys which to_dict provides mapped to simple names? let's check model.py)
            # model.py uses: protein_per_100g, etc.
            # to_dict returns: protein, sugar, etc.
            # let's map them back
            
            model_input = {
                'protein_per_100g': nutrition.protein_per_100g,
                'sugar_per_100g': nutrition.sugar_per_100g,
                'fat_per_100g': nutrition.fat_per_100g,
                'fiber_per_100g': nutrition.fiber_per_100g,
                'calories_per_100g': nutrition.calories_per_100g,
                'sodium_per_100g': nutrition.sodium_per_100g
            }
            
            # Prepare ingredient flags
            flags = {}
            if ingredients and ingredients.flagged_ingredients:
                flagged = ingredients.flagged_ingredients
                # Convert list of dicts to flat flags if needed, or parser helper
                # simpler: check raw flags if stored as JSON
                # Actually, model.py expects basic flags. Let's infer minimal flags.
                # Use IngredientsParser logic if possible, or just defaults.
                pass
            
            # Since we don't have full ingredient flags easily from DB without parser, 
            # we'll do a simpler prediction or skip flags.
            # actually, let's just stick to nutrition-based score for history view
            result = health_model.predict(model_input, flags)
            health_score = result.score
        except Exception as e:
            print(f"Error calculating health score: {e}")

    return ScanResponse(
        scan_id=scan.id,
        category=SchemaCategory(scan.category),
        scan_mode=scan.scan_mode,
        user_claim=scan.user_claim,
        verdict=Verdict(scan.final_verdict.value) if scan.final_verdict else None,
        score=scan.score,
        health_score=health_score,
        explanation=scan.explanation,
        nutrition=nutrition_data,
        ingredient_warnings=ingredient_warnings,
        sub_claims=sub_claims,
        created_at=scan.created_at,
        ocr_nutrition_text=ocr_nutrition_text,
        ocr_ingredients_text=ocr_ingredients_text
    )
