from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.public import version as public_version

api_router = APIRouter(prefix="/api")
api_router.include_router(public_version.router, prefix="/public", tags=["public"])
api_router.include_router(auth_router.router, prefix="/auth", tags=["auth"])
