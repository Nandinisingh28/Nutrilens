"""
NutriLens Backend - Scans Routes

Scan CRUD endpoints with OCR pipeline integration.
Supports two-image scanning (ingredients + nutrition) with legacy single-image fallback.
"""

import os
import uuid
import aiofiles
from io import BytesIO
from PIL import Image
from typing import Annotated, Optional, List

from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from sqlalchemy.orm import joinedload

from app.db import get_db
from app.db.models import User, Scan, Category, FileAsset, Product, Claim
from app.db.models.file_asset import FileKind
from app.db.models.scan import OverallVerdict
from app.api.deps import get_current_user
from app.core.config import settings
from app.core.exceptions import NotFoundError, ForbiddenError, AppException
from app.core.logging import get_logger
from app.schemas import (
    ScanResponse,
    ScanSummary,
    PaginationMeta,
    success_response,
)
from app.schemas.scan import OCRResult, OCRResults
from app.services import scan_pipeline

logger = get_logger(__name__)

router = APIRouter(prefix="/scans", tags=["Scans"])


async def save_image_file(
    image: UploadFile,
    image_bytes: bytes,
    user_id: int,
    kind: FileKind,
    db: AsyncSession,
) -> FileAsset:
    """Helper to save an image file and create FileAsset record."""
    file_ext = os.path.splitext(image.filename or "image.jpg")[1] or ".jpg"
    file_name = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, "labels", str(user_id), file_name)
    
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(image_bytes)
    
    file_asset = FileAsset(
        owner_user_id=user_id,
        kind=kind,
        storage_path=file_path,
        mime_type=image.content_type,
        size_bytes=len(image_bytes),
        original_filename=image.filename,
    )
    db.add(file_asset)
    await db.flush()
    
    return file_asset


async def validate_image(image: UploadFile) -> bytes:
    """Validate image and return bytes."""
    if image.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise AppException(
            message=f"Invalid file type. Allowed: {', '.join(settings.ALLOWED_IMAGE_TYPES)}",
            code="INVALID_FILE_TYPE",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    
    image_bytes = await image.read()
    if len(image_bytes) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise AppException(
            message=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE_MB}MB",
            code="FILE_TOO_LARGE",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    
    # Resolution validation
    try:
        with Image.open(BytesIO(image_bytes)) as img:
            width, height = img.size
            if width < settings.MIN_IMAGE_RESOLUTION and height < settings.MIN_IMAGE_RESOLUTION:
                raise AppException(
                    message=f"Image resolution too low ({width}x{height}). Minimum required: {settings.MIN_IMAGE_RESOLUTION}px.",
                    code="LOW_RESOLUTION",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
    except Exception as e:
        if isinstance(e, AppException):
            raise e
        logger.error(f"Failed to validate image resolution: {e}")
        # We don't raise here to avoid blocking valid images if PIL fails, 
        # but the primary check is done.
    
    return image_bytes


def get_image_url(file_asset: Optional[FileAsset]) -> Optional[str]:
    """Build URL for a file asset."""
    if not file_asset:
        return None
    # Return relative URL that can be served by backend
    return f"/api/files/{file_asset.id}"


@router.post("")
async def create_scan(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    category_id: int = Form(..., description="Category ID"),
    claim_text: Optional[str] = Form(None, description="User-entered claims to verify"),
    product_name: Optional[str] = Form(None, description="Product name"),
    brand: Optional[str] = Form(None, description="Brand name"),
    # NEW: Two-image scanning
    ingredients_image: Optional[UploadFile] = File(None, description="Photo of ingredients list"),
    nutrition_image: Optional[UploadFile] = File(None, description="Photo of nutrition facts"),
    # Legacy single image (backward compatible)
    image: Optional[UploadFile] = File(None, description="Legacy: single label image"),
):
    """
    Create a new scan with OCR analysis.
    
    Supports two modes:
    1. Two-image mode: Upload ingredients_image AND nutrition_image
    2. Legacy mode: Upload single 'image' for backward compatibility
    
    Pipeline:
    1. Upload image(s)
    2. Run OCR on each image separately
    3. Parse ingredients and nutrition from respective sources
    4. Verify claims
    5. Return full analysis results
    """
    # Determine scan mode
    is_two_image_mode = ingredients_image is not None and nutrition_image is not None
    is_legacy_mode = image is not None and not is_two_image_mode
    
    if not is_two_image_mode and not is_legacy_mode:
        raise AppException(
            message="Please provide either (ingredients_image + nutrition_image) or a single image",
            code="MISSING_IMAGES",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    
    # Verify category exists
    category = await db.get(Category, category_id)
    if not category:
        raise NotFoundError("Category", category_id)
    
    # Initialize variables
    ingredients_file_asset = None
    nutrition_file_asset = None
    label_file_asset = None
    ingredients_bytes = None
    nutrition_bytes = None
    legacy_bytes = None
    
    if is_two_image_mode:
        # Validate and save both images
        ingredients_bytes = await validate_image(ingredients_image)
        nutrition_bytes = await validate_image(nutrition_image)
        
        ingredients_file_asset = await save_image_file(
            ingredients_image, ingredients_bytes, current_user.id,
            FileKind.INGREDIENTS_IMAGE, db
        )
        nutrition_file_asset = await save_image_file(
            nutrition_image, nutrition_bytes, current_user.id,
            FileKind.NUTRITION_IMAGE, db
        )
    else:
        # Legacy single image mode
        legacy_bytes = await validate_image(image)
        label_file_asset = await save_image_file(
            image, legacy_bytes, current_user.id,
            FileKind.LABEL_IMAGE, db
        )
    
    # Create scan record
    scan = Scan(
        user_id=current_user.id,
        category_id=category_id,
        claim_text=claim_text,
        # Legacy
        label_image_file_id=label_file_asset.id if label_file_asset else None,
        # Two-image
        ingredients_image_file_id=ingredients_file_asset.id if ingredients_file_asset else None,
        nutrition_image_file_id=nutrition_file_asset.id if nutrition_file_asset else None,
        overall_verdict=OverallVerdict.UNKNOWN,
    )
    db.add(scan)
    await db.flush()
    
    # Run OCR pipeline
    logger.info(f"DEBUG: Starting OCR pipeline for scan {scan.id}")
    results = {} 
    try:
        if is_two_image_mode:
            # Process both images separately
            results = await scan_pipeline.process_scan_two_images(
                ingredients_bytes=ingredients_bytes,
                nutrition_bytes=nutrition_bytes,
                user_claims=claim_text,
                product_name=product_name,
                brand=brand,
                category_id=category_id,
                db=db,
                scan_id=scan.id,
            )
            
            # Store separate OCR text
            scan.ocr_raw_ingredients_text = results.get("ocr", {}).get("ingredients", {}).get("raw_text")
            scan.ocr_raw_nutrition_text = results.get("ocr", {}).get("nutrition", {}).get("raw_text")
            # Also combine for legacy compatibility
            combined_text = []
            if scan.ocr_raw_ingredients_text:
                combined_text.append(f"=== INGREDIENTS ===\n{scan.ocr_raw_ingredients_text}")
            if scan.ocr_raw_nutrition_text:
                combined_text.append(f"=== NUTRITION ===\n{scan.ocr_raw_nutrition_text}")
            scan.ocr_raw_text = "\n\n".join(combined_text) if combined_text else None
        else:
            # Legacy single image processing
            results = await scan_pipeline.process_scan(
                image_bytes=legacy_bytes,
                user_claims=claim_text,
                product_name=product_name,
                brand=brand,
                category_id=category_id,
                db=db,
                scan_id=scan.id,
            )
            scan.ocr_raw_text = results.get("ocr", {}).get("raw_text")
        
        # Update scan with results summary
        logger.info("DEBUG: Pipeline finished, updating scan results")
        scan.raw_results = results
        scan.overall_verdict = scan_pipeline.map_verdict(results.get("overall", {}).get("verdict", "unknown"))
        
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        # Rollback the failed transaction (clears the session)
        await db.rollback()
        
        # We need to save the scan failure record.
        # Since we rolled back, the 'scan' object and 'file_assets' are detached/gone from DB.
        # We need to re-add them or create new ones.
        # For simplicity, let's just create a minimal failed scan record.
        try:
            # Re-create scan object for the error log
            failed_scan = Scan(
                user_id=current_user.id,
                category_id=category_id,
                claim_text=claim_text,
                overall_verdict=OverallVerdict.UNKNOWN,
                raw_results={"error": str(e)}
            )
            # Re-attach file assets if we want to keep them (complex due to IDs being lost)
            # For now, just logging the scan failure is better than 500ing.
            
            db.add(failed_scan)
            await db.commit()
            await db.refresh(failed_scan)
            scan = failed_scan # Use this for response
            
        except Exception as inner_e:
            logger.error(f"Failed to save error state: {inner_e}")
            raise AppException(
                message=f"Scan processing failed: {str(e)}",
                code="SCAN_FAILED",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    else:
        # Happy path commit
        await db.commit()
        await db.refresh(scan)
    
    logger.info(f"Scan created: {scan.id} by user {current_user.email}, verdict: {scan.overall_verdict}")
    
    # Safe response building
    try:
        # Build OCR results for response
        ocr_results = None
        if results:
            if is_two_image_mode:
                ocr_data = results.get("ocr", {})
                ocr_results = {
                    "ingredients": ocr_data.get("ingredients"),
                    "nutrition": ocr_data.get("nutrition"),
                }
            else:
                ocr_data = results.get("ocr", {})
                ocr_results = {
                    "combined": {
                        "confidence": ocr_data.get("confidence", 0),
                        "word_count": ocr_data.get("word_count", 0),
                        "raw_text": ocr_data.get("raw_text"),
                        "quality": ocr_data.get("quality", "unknown"),
                    }
                }
        
        # Build response with full results
        response_data = {
            "id": scan.id,
            "product_name": scan.product.name if scan.product else None,
            "brand": scan.product.brand if scan.product else None,
            "category_id": scan.category_id,
            "claim_text": scan.claim_text,
            "overall_verdict": scan.overall_verdict.value if scan.overall_verdict else "unknown",
            "results": scan.raw_results,
            "ocr_results": ocr_results,
            # Image URLs
            "label_image_url": get_image_url(scan.label_image) if scan.label_image_file_id else None,
            "ingredients_image_url": get_image_url(scan.ingredients_image) if scan.ingredients_image_file_id else None,
            "nutrition_image_url": get_image_url(scan.nutrition_image) if scan.nutrition_image_file_id else None,
            "created_at": scan.created_at.isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to build response for scan {scan.id}: {e}", exc_info=True)
        # Verify scan exists/committed
        return {
            "id": scan.id,
            "status": "error",
            "message": "Scan processed but response building failed. See detailed results in history.",
            "error_details": str(e),
            "results": scan.raw_results
        }
    
    return success_response(
        data=response_data,
        message="Scan created and analyzed",
    )


@router.post("/{scan_id}/reprocess")
async def reprocess_scan(
    scan_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Reprocess an existing scan with updated rules.
    
    Useful when rules are updated or for debugging.
    """
    scan = await db.get(Scan, scan_id)
    
    if not scan:
        raise NotFoundError("Scan", scan_id)
    
    if scan.user_id != current_user.id:
        raise ForbiddenError("You do not have access to this scan")
    
    # Check for any image to reprocess
    has_images = scan.label_image_file_id or scan.ingredients_image_file_id or scan.nutrition_image_file_id
    if not has_images:
        raise AppException(
            message="Scan has no associated image to reprocess",
            code="NO_IMAGE",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    
    try:
        results = await scan_pipeline.reprocess_scan(scan, db)
        
        return success_response(
            data={
                "id": scan.id,
                "overall_verdict": scan.overall_verdict.value,
                "results": results,
            },
            message="Scan reprocessed successfully",
        )
        
    except Exception as e:
        logger.error(f"Reprocess failed for scan {scan_id}: {e}")
        raise AppException(
            message=f"Reprocessing failed: {str(e)}",
            code="REPROCESS_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.get("")
async def list_scans(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    verdict: Optional[str] = None,
):
    """List user's scans with pagination."""
    # Build query
    query = select(Scan).where(Scan.user_id == current_user.id)
    count_query = select(func.count()).select_from(Scan).where(Scan.user_id == current_user.id)
    
    if category_id:
        query = query.where(Scan.category_id == category_id)
        count_query = count_query.where(Scan.category_id == category_id)
    
    if verdict:
        try:
            verdict_enum = OverallVerdict(verdict)
            query = query.where(Scan.overall_verdict == verdict_enum)
            count_query = count_query.where(Scan.overall_verdict == verdict_enum)
        except ValueError:
            pass  # Ignore invalid verdict filter
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Get paginated results
    offset = (page - 1) * per_page
    query = query.order_by(Scan.created_at.desc()).offset(offset).limit(per_page)
    
    result = await db.execute(query)
    scans = result.scalars().all()
    
    total_pages = (total + per_page - 1) // per_page
    
    # Build response with image URLs
    scan_data = []
    for s in scans:
        data = {
            "id": s.id,
            "product_name": s.product.name if s.product else None,
            "brand": s.product.brand if s.product else None,
            "category_id": s.category_id,
            "overall_verdict": s.overall_verdict.value if s.overall_verdict else "unknown",
            "created_at": s.created_at.isoformat(),
            "label_image_url": get_image_url(s.label_image) if s.label_image_file_id else None,
            "ingredients_image_url": get_image_url(s.ingredients_image) if s.ingredients_image_file_id else None,
            "nutrition_image_url": get_image_url(s.nutrition_image) if s.nutrition_image_file_id else None,
        }
        scan_data.append(data)
    
    return {
        "success": True,
        "message": "Success",
        "data": scan_data,
        "meta": PaginationMeta(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
        ).model_dump(),
        "error": None,
    }


@router.get("/{scan_id}")
async def get_scan(
    scan_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get scan by ID with full results."""
    # Fetch scan with related normalized data
    stmt = (
        select(Scan)
        .where(Scan.id == scan_id)
        .options(
            joinedload(Scan.product).joinedload(Product.ingredients),
            joinedload(Scan.product).joinedload(Product.nutrition_facts),
            joinedload(Scan.claims).joinedload(Claim.verification_results),
        )
    )
    result = await db.execute(stmt)
    scan = result.unique().scalar_one_or_none()
    
    if not scan:
        raise NotFoundError("Scan", scan_id)
    
    if scan.user_id != current_user.id:
        raise ForbiddenError("You do not have access to this scan")
    
    # Build OCR results
    ocr_results = None
    if scan.ocr_raw_ingredients_text or scan.ocr_raw_nutrition_text:
        # Two-image scan
        ocr_results = {
            "ingredients": {
                "raw_text": scan.ocr_raw_ingredients_text,
                "quality": "good" if scan.ocr_raw_ingredients_text and len(scan.ocr_raw_ingredients_text) > 50 else "medium",
            } if scan.ocr_raw_ingredients_text else None,
            "nutrition": {
                "raw_text": scan.ocr_raw_nutrition_text,
                "quality": "good" if scan.ocr_raw_nutrition_text and len(scan.ocr_raw_nutrition_text) > 50 else "medium",
            } if scan.ocr_raw_nutrition_text else None,
        }
    elif scan.ocr_raw_text:
        # Legacy single image
        ocr_results = {
            "combined": {
                "raw_text": scan.ocr_raw_text,
                "quality": "good" if len(scan.ocr_raw_text) > 100 else "medium",
            }
        }
    
    response_data = {
        "id": scan.id,
        "user_id": scan.user_id,
        "product_name": scan.product.name if scan.product else None,
        "brand": scan.product.brand if scan.product else None,
        "category_id": scan.category_id,
        "claim_text": scan.claim_text,
        "overall_verdict": scan.overall_verdict.value if scan.overall_verdict else "unknown",
        "results": scan.raw_results,
        # Legacy OCR
        "ocr_raw_text": scan.ocr_raw_text,
        # New separate OCR
        "ocr_raw_ingredients_text": scan.ocr_raw_ingredients_text,
        "ocr_raw_nutrition_text": scan.ocr_raw_nutrition_text,
        "ocr_results": ocr_results,
        # Image URLs
        "label_image_file_id": scan.label_image_file_id,
        "label_image_url": get_image_url(scan.label_image) if scan.label_image_file_id else None,
        "ingredients_image_file_id": scan.ingredients_image_file_id,
        "nutrition_image_file_id": scan.nutrition_image_file_id,
        "ingredients_image_url": get_image_url(scan.ingredients_image) if scan.ingredients_image_file_id else None,
        "nutrition_image_url": get_image_url(scan.nutrition_image) if scan.nutrition_image_file_id else None,
        # Timestamps
        "created_at": scan.created_at.isoformat(),
        "updated_at": scan.updated_at.isoformat(),
        # Normalized data
        "product_id": scan.product_id,
        "ingredients": [i.to_dict() for i in scan.product.ingredients] if scan.product else [],
        "nutrition_facts": [n.to_dict() for n in scan.product.nutrition_facts] if scan.product else [],
        "claims": [
            {
                "id": c.id,
                "text": c.text,
                "verification_results": [v.to_dict() for v in c.verification_results]
            } for c in scan.claims
        ],
    }
    
    return success_response(data=response_data)


@router.delete("/{scan_id}")
async def delete_scan(
    scan_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete a scan."""
    scan = await db.get(Scan, scan_id)
    
    if not scan:
        raise NotFoundError("Scan", scan_id)
    
    if scan.user_id != current_user.id:
        raise ForbiddenError("You do not have access to this scan")
    
    # Delete associated files
    for file_id in [scan.label_image_file_id, scan.ingredients_image_file_id, scan.nutrition_image_file_id]:
        if file_id:
            file_asset = await db.get(FileAsset, file_id)
            if file_asset and os.path.exists(file_asset.storage_path):
                try:
                    os.remove(file_asset.storage_path)
                except OSError:
                    pass
            if file_asset:
                await db.delete(file_asset)
    
    await db.delete(scan)
    await db.commit()
    
    logger.info(f"Scan deleted: {scan_id} by user {current_user.email}")
    
    return success_response(message="Scan deleted")


@router.delete("")
async def bulk_delete_scans(
    scan_ids: List[int] = Query(..., description="List of scan IDs to delete"),
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
):
    """Bulk delete scans."""
    # Get scans to delete
    result = await db.execute(
        select(Scan).where(
            Scan.id.in_(scan_ids),
            Scan.user_id == current_user.id,
        )
    )
    scans = result.scalars().all()
    
    # Delete associated files
    for scan in scans:
        for file_id in [scan.label_image_file_id, scan.ingredients_image_file_id, scan.nutrition_image_file_id]:
            if file_id:
                file_asset = await db.get(FileAsset, file_id)
                if file_asset and os.path.exists(file_asset.storage_path):
                    try:
                        os.remove(file_asset.storage_path)
                    except OSError:
                        pass
                if file_asset:
                    await db.delete(file_asset)
    
    # Delete scans
    deleted_ids = [s.id for s in scans]
    for scan in scans:
        await db.delete(scan)
    
    await db.commit()
    
    logger.info(f"Bulk deleted {len(deleted_ids)} scans by user {current_user.email}")
    
    return success_response(
        data={"deleted_count": len(deleted_ids), "deleted_ids": deleted_ids},
        message=f"Deleted {len(deleted_ids)} scans",
    )
