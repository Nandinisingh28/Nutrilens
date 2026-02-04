"""API routes package."""

from fastapi import APIRouter

from app.api.routes import health, auth, users, categories, scans, files

# Main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(categories.router)
api_router.include_router(scans.router)
api_router.include_router(files.router)
