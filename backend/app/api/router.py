from fastapi import APIRouter

from app.api.public import version as public_version

api_router = APIRouter(prefix="/api")
api_router.include_router(public_version.router, prefix="/public", tags=["public"])
