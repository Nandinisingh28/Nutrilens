"""
NutriLens Backend - Main Application

FastAPI application entry point.
"""

import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import setup_exception_handlers
from app.api.routes import api_router
from app.db import init_db, async_session_maker

logger = get_logger(__name__)


async def ensure_seed_data():
    """Ensure essential seed data exists (categories, rules)."""
    async with async_session_maker() as session:
        # Check categories
        result = await session.execute(text("SELECT COUNT(*) FROM categories"))
        cat_count = result.scalar()
        
        if cat_count == 0:
            logger.info("Seeding categories...")
            await session.execute(text("""
                INSERT INTO categories (slug, title, description) VALUES
                ('protein-bars', 'Protein Bars', 'High protein snack bars'),
                ('breakfast-cereals', 'Breakfast Cereals', 'Cereals and breakfast foods'),
                ('beverages', 'Beverages', 'Drinks and liquid refreshments'),
                ('snacks', 'Snacks', 'Packaged snack foods'),
                ('dairy', 'Dairy', 'Milk, cheese, and dairy products'),
                ('supplements', 'Supplements', 'Health supplements and vitamins')
            """))
            await session.commit()
            logger.info("Categories seeded successfully")
        
        # Check rules
        result = await session.execute(text("SELECT COUNT(*) FROM rules WHERE rule_type = 'sugar_alias'"))
        rule_count = result.scalar()
        
        if rule_count == 0:
            logger.info("Seeding sugar aliases...")
            sugar_aliases = [
                'glucose syrup', 'maltodextrin', 'dextrose', 'fructose', 'sucrose',
                'invert sugar', 'corn syrup', 'high fructose corn syrup', 'hfcs',
                'jaggery', 'honey', 'agave', 'maple syrup', 'molasses', 'brown sugar',
                'cane sugar', 'coconut sugar', 'date syrup', 'rice syrup', 'barley malt'
            ]
            for alias in sugar_aliases:
                await session.execute(text("""
                    INSERT INTO rules (category_id, rule_type, `key`, value, is_active)
                    VALUES (NULL, 'sugar_alias', :key, :value, 1)
                """), {"key": alias, "value": f'{{"alias": "{alias}", "is_sugar": true}}'})
            await session.commit()
            logger.info(f"Seeded {len(sugar_aliases)} sugar aliases")


def ensure_storage_directories():
    """Ensure storage directories exist."""
    dirs = [
        Path(settings.UPLOAD_DIR),
        Path(settings.UPLOAD_DIR) / "scans",
        Path(settings.UPLOAD_DIR) / "avatars",
    ]
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directory exists: {dir_path}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Ensure storage directories
    ensure_storage_directories()
    logger.info("Storage directories ready")
    
    # Initialize database
    await init_db()
    logger.info("Database tables ready")
    
    # Seed essential data
    try:
        await ensure_seed_data()
        logger.info("Seed data verified")
    except Exception as e:
        logger.warning(f"Seed check skipped (tables may not exist yet): {e}")
    
    logger.info("Startup complete!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Nutrition Label Scanning API with OCR and NLP",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Setup CORS
# Note: allow_origins cannot be ["*"] when allow_credentials=True
allowed_origins = [str(origin).rstrip("/") for origin in settings.BACKEND_CORS_ORIGINS]
# Add some extra common local variants just in case
extra_origins = ["http://localhost:5173", "http://127.0.0.1:5173", "http://0.0.0.0:5173"]
for origin in extra_origins:
    if origin not in allowed_origins:
        allowed_origins.append(origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup exception handlers
setup_exception_handlers(app)

# Include routes with global /api prefix
app.include_router(api_router, prefix="/api")
