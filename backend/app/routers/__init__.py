"""
API Routers Package
"""
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.scans import router as scans_router

__all__ = ["auth_router", "users_router", "scans_router"]
