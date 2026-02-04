"""
NutriLens Backend - Scan Pipeline Service

Main orchestrator for OCR and claim verification.
Supports both single-image and two-image scanning modes.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.logging import get_logger
from app.core.exceptions import OCRQualityError
from app.db.models import Rule, Scan, FileAsset, Category, Product, Ingredient, NutritionFact, Claim, VerificationResult
from app.db.models.scan import OverallVerdict
from app.services.ocr_service import ocr_service
from app.services.ingredient_parser import ingredient_parser
from app.services.nutrition_parser import nutrition_parser
from app.services.claim_engine import claim_engine, ClaimResult, Verdict

logger = get_logger(__name__)


class ScanPipeline:
    """Orchestrates the full scan analysis pipeline."""
    
    def __init__(self):
        self._rules_loaded = False
    
    async def load_rules(self, db: AsyncSession) -> None:
        """Load rules from database."""
        if self._rules_loaded:
            return
        
        result = await db.execute(
            select(Rule).where(Rule.is_active == True)
        )
        rules = result.scalars().all()
        
        # Convert to dicts
        rule_dicts = [
            {
                "rule_type": r.rule_type.value if hasattr(r.rule_type, 'value') else r.rule_type,
                "key": r.key,
                "value": r.value,
            }
            for r in rules
        ]
        
        # Load into parsers
        ingredient_parser.load_rules(rule_dicts)
        claim_engine.load_thresholds(rule_dicts)
        
        self._rules_loaded = True
        logger.info(f"Loaded {len(rules)} rules from database")
    
    def _compute_ocr_quality(self, ocr_result: Dict[str, Any]) -> str:
        """Determine OCR quality based on confidence and word count."""
        confidence = ocr_result.get("confidence", 0)
        word_count = ocr_result.get("word_count", 0)
        
        if confidence >= 0.8 and word_count >= 20:
            return "good"
        elif confidence >= 0.5 and word_count >= 10:
            return "medium"
        else:
            return "low"
    
    async def process_scan(
        self,
        image_bytes: bytes,
        user_claims: Optional[str] = None,
        product_name: Optional[str] = None,
        brand: Optional[str] = None,
        category_id: Optional[int] = None,
        db: Optional[AsyncSession] = None,
        scan_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Run the full analysis pipeline on a single image.
        
        Args:
            image_bytes: Raw image bytes
            user_claims: User-entered claims to verify
            product_name: Optional product name
            brand: Optional brand name
            category_id: Optional category ID
            db: Database session for loading rules
            
        Returns:
            Complete analysis results
        """
        start_time = datetime.utcnow()
        
        # Load rules if database provided
        if db:
            await self.load_rules(db)
        
        # Step 1: OCR
        logger.info("Starting OCR extraction...")
        ocr_result = ocr_service.extract_text(image_bytes)
        ocr_text = ocr_result.get("cleaned_text", "")
        confidence = ocr_result.get("confidence", 0)
        
        # Validation: check for empty text or low confidence
        if not ocr_text or len(ocr_text) < 20:
            raise OCRQualityError(
                message="No readable text found on the label. Please ensure the image is clear and well-lit.",
                details={"confidence": confidence, "word_count": ocr_result.get("word_count", 0)}
            )
        
        if confidence < 0.4:
            raise OCRQualityError(
                message="OCR confidence is too low. The image might be blurry or the text too small.",
                details={"confidence": confidence, "word_count": ocr_result.get("word_count", 0)}
            )
        
        # Step 2: Parse ingredients
        logger.info("Parsing ingredients...")
        ingredients = ingredient_parser.parse(ocr_text)
        
        # Step 3: Parse nutrition
        logger.info("Parsing nutrition facts...")
        nutrition = nutrition_parser.parse(ocr_text)
        
        # Step 4: Detect claims
        logger.info("Detecting claims...")
        detected_claims = claim_engine.detect_claims(ocr_text, user_claims)
        
        # Step 5: Verify claims
        logger.info(f"Verifying {len(detected_claims)} claims...")
        claim_results = claim_engine.verify_claims(
            detected_claims,
            ingredients,
            nutrition,
        )
        
        # Step 6: Compute overall verdict
        overall = claim_engine.compute_overall_verdict(claim_results)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Build result structure
        result = {
            "product": {
                "name": product_name,
                "brand": brand,
                "category_id": category_id,
            },
            "ocr": {
                "raw_text": ocr_result.get("raw_text", ""),
                "cleaned_text": ocr_text,
                "confidence": ocr_result.get("confidence", 0),
                "word_count": ocr_result.get("word_count", 0),
                "quality": self._compute_ocr_quality(ocr_result),
            },
            "ingredients": ingredients,
            "nutrition": nutrition,
            "claims": [r.to_dict() for r in claim_results],
            "overall": overall,
            "metadata": {
                "processing_time_seconds": round(processing_time, 2),
                "timestamp": start_time.isoformat(),
                "claims_detected": len(detected_claims),
                "scan_mode": "single_image",
            },
        }
        
        # NEW: Save to normalized tables if db provided
        if db and scan_id:
            await self._save_normalized_results(db, result, claim_results, scan_id)
        
        logger.info(
            f"Scan complete: {len(detected_claims)} claims, "
            f"verdict={overall['verdict']}, "
            f"time={processing_time:.2f}s"
        )
        
        return result
    
    async def process_scan_two_images(
        self,
        ingredients_bytes: bytes,
        nutrition_bytes: bytes,
        user_claims: Optional[str] = None,
        product_name: Optional[str] = None,
        brand: Optional[str] = None,
        category_id: Optional[int] = None,
        db: Optional[AsyncSession] = None,
        scan_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Run the full analysis pipeline on two separate images.
        
        Args:
            ingredients_bytes: Raw image bytes for ingredients list
            nutrition_bytes: Raw image bytes for nutrition facts
            user_claims: User-entered claims to verify
            product_name: Optional product name
            brand: Optional brand name
            category_id: Optional category ID
            db: Database session for loading rules
            
        Returns:
            Complete analysis results with separate OCR data per image
        """
        start_time = datetime.utcnow()
        
        # Load rules if database provided
        if db:
            await self.load_rules(db)
        
        # Step 1: OCR on ingredients image
        logger.info("Starting OCR extraction on ingredients image...")
        ingredients_ocr = ocr_service.extract_text(ingredients_bytes)
        ingredients_text = ingredients_ocr.get("cleaned_text", "")
        ing_confidence = ingredients_ocr.get("confidence", 0)
        
        if not ingredients_text or len(ingredients_text) < 10:
             raise OCRQualityError(
                message="Ingredients list image is unreadable.",
                details={"confidence": ing_confidence, "source": "ingredients"}
            )

        # Step 2: OCR on nutrition image
        logger.info("Starting OCR extraction on nutrition image...")
        nutrition_ocr = ocr_service.extract_text(nutrition_bytes)
        nutrition_text = nutrition_ocr.get("cleaned_text", "")
        nut_confidence = nutrition_ocr.get("confidence", 0)

        if not nutrition_text or len(nutrition_text) < 10:
             raise OCRQualityError(
                message="Nutrition facts image is unreadable.",
                details={"confidence": nut_confidence, "source": "nutrition"}
            )
            
        # Overall confidence check
        if ing_confidence < 0.35 or nut_confidence < 0.35:
             raise OCRQualityError(
                message="Image quality is too low for precision scanning. Please retake photos with better lighting.",
                details={"ing_confidence": ing_confidence, "nut_confidence": nut_confidence}
            )
        
        # Step 3: Parse ingredients from ONLY ingredients image
        logger.info("Parsing ingredients from dedicated image...")
        ingredients = ingredient_parser.parse(ingredients_text)
        
        # Step 4: Parse nutrition from ONLY nutrition image
        logger.info("Parsing nutrition facts from dedicated image...")
        nutrition = nutrition_parser.parse(nutrition_text)
        
        # Step 5: Detect claims using both texts + user claims
        logger.info("Detecting claims...")
        combined_text = f"{ingredients_text}\n\n{nutrition_text}"
        detected_claims = claim_engine.detect_claims(combined_text, user_claims)
        
        # Step 6: Verify claims
        logger.info(f"Verifying {len(detected_claims)} claims...")
        claim_results = claim_engine.verify_claims(
            detected_claims,
            ingredients,
            nutrition,
        )
        
        # Step 7: Compute overall verdict
        overall = claim_engine.compute_overall_verdict(claim_results)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Build OCR results per image
        ingredients_ocr_result = {
            "raw_text": ingredients_ocr.get("raw_text", ""),
            "cleaned_text": ingredients_text,
            "confidence": ingredients_ocr.get("confidence", 0),
            "word_count": ingredients_ocr.get("word_count", 0),
            "quality": self._compute_ocr_quality(ingredients_ocr),
        }
        
        nutrition_ocr_result = {
            "raw_text": nutrition_ocr.get("raw_text", ""),
            "cleaned_text": nutrition_text,
            "confidence": nutrition_ocr.get("confidence", 0),
            "word_count": nutrition_ocr.get("word_count", 0),
            "quality": self._compute_ocr_quality(nutrition_ocr),
        }
        
        # Build result structure
        result = {
            "product": {
                "name": product_name,
                "brand": brand,
                "category_id": category_id,
            },
            "ocr": {
                "ingredients": ingredients_ocr_result,
                "nutrition": nutrition_ocr_result,
                # Combined raw text for backward compatibility
                "raw_text": f"=== INGREDIENTS ===\n{ingredients_ocr.get('raw_text', '')}\n\n=== NUTRITION ===\n{nutrition_ocr.get('raw_text', '')}",
            },
            "ingredients": ingredients,
            "nutrition": nutrition,
            "claims": [r.to_dict() for r in claim_results],
            "overall": overall,
            "metadata": {
                "processing_time_seconds": round(processing_time, 2),
                "timestamp": start_time.isoformat(),
                "claims_detected": len(detected_claims),
                "scan_mode": "two_image",
            },
        }
        
        # NEW: Save to normalized tables if db provided
        if db and scan_id:
            await self._save_normalized_results(db, result, claim_results, scan_id)
        
        logger.info(
            f"Two-image scan complete: {len(detected_claims)} claims, "
            f"verdict={overall['verdict']}, "
            f"ingredients_quality={ingredients_ocr_result['quality']}, "
            f"nutrition_quality={nutrition_ocr_result['quality']}, "
            f"time={processing_time:.2f}s"
        )
        
        return result
    
    def map_verdict(self, verdict_str: str) -> OverallVerdict:
        """Map string verdict to enum."""
        mapping = {
            "true": OverallVerdict.TRUE,
            "misleading": OverallVerdict.MISLEADING,
            "false": OverallVerdict.FALSE,
            "mixed": OverallVerdict.MIXED,
            "unknown": OverallVerdict.UNKNOWN,
        }
        return mapping.get(verdict_str, OverallVerdict.UNKNOWN)
    
    async def reprocess_scan(
        self,
        scan: Scan,
        db: AsyncSession,
    ) -> Dict[str, Any]:
        """
        Reprocess an existing scan.
        
        Args:
            scan: Existing scan record
            db: Database session
            
        Returns:
            Updated analysis results
        """
        import aiofiles
        
        # Determine scan mode based on available images
        has_two_images = scan.ingredients_image_file_id and scan.nutrition_image_file_id
        has_legacy_image = scan.label_image_file_id
        
        if has_two_images:
            # Two-image reprocess
            ingredients_asset = await db.get(FileAsset, scan.ingredients_image_file_id)
            nutrition_asset = await db.get(FileAsset, scan.nutrition_image_file_id)
            
            if not ingredients_asset or not nutrition_asset:
                raise ValueError("Image files not found")
            
            async with aiofiles.open(ingredients_asset.storage_path, 'rb') as f:
                ingredients_bytes = await f.read()
            async with aiofiles.open(nutrition_asset.storage_path, 'rb') as f:
                nutrition_bytes = await f.read()
            
            results = await self.process_scan_two_images(
                ingredients_bytes=ingredients_bytes,
                nutrition_bytes=nutrition_bytes,
                user_claims=scan.claim_text,
                product_name=scan.product_name,
                brand=scan.brand,
                category_id=scan.category_id,
                db=db,
            )
            
            # Update scan record with two-image data
            scan.ocr_raw_ingredients_text = results["ocr"]["ingredients"]["raw_text"]
            scan.ocr_raw_nutrition_text = results["ocr"]["nutrition"]["raw_text"]
            scan.ocr_raw_text = results["ocr"]["raw_text"]
            
        elif has_legacy_image:
            # Legacy single-image reprocess
            result = await db.execute(
                select(FileAsset).where(FileAsset.id == scan.label_image_file_id)
            )
            file_asset = result.scalar_one_or_none()
            
            if not file_asset:
                raise ValueError("Image file not found")
            
            async with aiofiles.open(file_asset.storage_path, 'rb') as f:
                image_bytes = await f.read()
            
            results = await self.process_scan(
                image_bytes=image_bytes,
                user_claims=scan.claim_text,
                product_name=scan.product_name,
                brand=scan.brand,
                category_id=scan.category_id,
                db=db,
            )
            
            scan.ocr_raw_text = results["ocr"]["raw_text"]
        else:
            raise ValueError("Scan has no associated images")
        
        # Update common fields
        # Note: We don't remove existing Product/Claims/etc. for now, 
        # but we do update the raw_results for future sync.
        scan.raw_results = results
        scan.overall_verdict = self.map_verdict(results["overall"]["verdict"])
        
        # Sync to normalized tables
        await self._save_normalized_results(db, results, claim_results if 'claim_results' in locals() else [], scan.id)
        
        await db.commit()
        
        return results


    async def _save_normalized_results(
        self,
        db: AsyncSession,
        result: Dict[str, Any],
        claim_results: List[ClaimResult],
        scan_id: int
    ) -> None:
        """Save analysis results to normalized database tables."""
        product_data = result.get("product", {})
        if not product_data.get("name") or not product_data.get("category_id"):
            logger.warning("Skipping normalized save: missing product name or category_id")
            return

        # 1. Create/Find Product
        # For simplicity, we create a new Product entry.
        # In a real app, we'd search by name/brand first.
        prod_name = product_data.get("name", "") or "Unknown Product"
        if len(prod_name) > 250:
            prod_name = prod_name[:250]
            
        prod_brand = product_data.get("brand")
        if prod_brand and len(prod_brand) > 250:
            prod_brand = prod_brand[:250]

        product = Product(
            name=prod_name,
            brand=prod_brand,
            category_id=product_data["category_id"]
        )
        db.add(product)
        await db.flush()
        logger.info(f"DEBUG: Product created with ID {product.id}")

        # 2. Ingredients
        ingredients_data = result.get("ingredients", {}).get("list", [])
        logger.info(f"DEBUG: Saving {len(ingredients_data)} ingredients")
        for i, ing_item in enumerate(ingredients_data):
            try:
                name = ing_item.get("name", "")
                if len(name) > 250:
                    logger.warning(f"Truncating ingredient name from {len(name)} to 250 chars: {name[:50]}...")
                    name = name[:250]
                
                ingredient = Ingredient(
                    product_id=product.id,
                    name=name,
                    position=i,
                    is_sugar_alias=ing_item.get("is_sugar_alias", False),
                    is_additive=ing_item.get("is_additive", False),
                    is_preservative=ing_item.get("is_preservative", False)
                )
                db.add(ingredient)
            except Exception as e:
                logger.error(f"Failed to save ingredient {i}: {e}")

        # 3. Nutrition Facts
        normalized_nutrition = result.get("nutrition", {}).get("normalized_per_100g", {})
        raw_nutrition = result.get("nutrition", {}).get("raw_values", {})
        
        logger.info(f"DEBUG: Saving {len(normalized_nutrition)} nutrition facts")
        for key, value in normalized_nutrition.items():
            try:
                # Truncate key if too long to prevent DB error
                if len(key) > 250:
                    logger.warning(f"Truncating nutrition key '{key}' to 250 chars")
                    key = key[:250]
                
                unit = raw_nutrition.get(key, {}).get("unit", "g")
                db.add(NutritionFact(
                    product_id=product.id,
                    name=key,
                    value=float(value) if value is not None else 0.0,
                    unit=unit
                ))
            except Exception as e:
                logger.error(f"Failed to save nutrition fact {key}: {e}")

        # 4. Update Scan with product_id
        scan = await db.get(Scan, scan_id)
        if scan:
            scan.product_id = product.id

        # 5. Claims and Verification Results
        for claim_res in claim_results:
            claim_text = claim_res.claim
            if len(claim_text) > 250:
                 claim_text = claim_text[:250]

            claim_obj = Claim(
                scan_id=scan_id,
                text=claim_text
            )
            db.add(claim_obj)
            await db.flush() # Get claim_obj.id

            db.add(VerificationResult(
                scan_id=scan_id,
                claim_id=claim_obj.id,
                verdict=self.map_verdict(claim_res.verdict.value),
                confidence=claim_res.confidence,
                explanation=claim_res.explanation,
                evidence={"data": claim_res.evidence}
            ))

# Singleton instance
scan_pipeline = ScanPipeline()
