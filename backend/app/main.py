"""
NutriLens - Food Claim Verification API
Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import get_settings
from app.database import engine, Base
from app.routers import auth_router, users_router, scans_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    logger.info("Starting NutriLens API...")
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified")
        # Migrate: ensure scans.category is VARCHAR, not the old 2-value ENUM
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE scans MODIFY COLUMN category VARCHAR(50) NOT NULL"))
            conn.commit()
            logger.info("Verified scans.category column type")
    except Exception as e:
        logger.warning(f"Database initialization/migration note: {e}")
    
    # Seed rule tables (idempotent)
    try:
        from app.database import SessionLocal
        from app.services.seed_data import seed_database
        db = SessionLocal()
        try:
            seed_database(db)
            logger.info("Database seeding complete")
        finally:
            db.close()
    except Exception as e:
        logger.warning(f"Database seeding warning: {e}")
    
    # Train ML model if needed
    try:
        from app.services.ml.model import get_health_model
        model = get_health_model()
        logger.info(f"ML model loaded (trained: {model.is_trained})")
    except Exception as e:
        logger.warning(f"ML model initialization warning: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down NutriLens API...")


# Create FastAPI application
app = FastAPI(
    title="NutriLens API",
    description="""
    ## Food Claim Verification Platform (India)
    
    NutriLens helps you verify food packaging claims using OCR and ML.
    
    ### Features:
    - **Precision Scan**: Upload separate nutrition and ingredients images
    - **Quick Scan**: Upload a single image with both sections
    - **Claim Verification**: Verify claims like "High Protein", "Low Sugar", etc.
    - **Scan History**: Track all your past scans
    
    ### Supported Categories:
    - Protein Bars, Breakfast Cereals, Biscuits & Cookies
    - Snacks, Chocolates & Confectionery, Beverages
    - Energy Drinks, Dairy Products, Instant Noodles & RTE
    - Sauces & Spreads, Health Supplements, Frozen Foods
    
    ### Claim Types:
    High Protein, Low Sugar, No Added Sugar, High Fiber, Low Fat, 
    Low Calories, Healthy, Natural, No Preservatives, and more.
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS - Allow all origins for development
origins = settings.cors_origins_list
if not origins or origins == [""]:
    origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(scans_router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API health check"""
    return {
        "name": "NutriLens API",
        "version": "1.0.0",
        "status": "healthy",
        "documentation": "/docs"
    }


@app.get("/health", tags=["Root"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
