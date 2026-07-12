# Part of the With FBraun project template.
# Author: František Braun <frantisek.braun95@gmail.com>
# Freely available as a template for building custom applications.

from fastapi import APIRouter

from app.api.account import router as account_router
from app.api.auth import router as auth_router
from app.api.public import version as public_version

api_router = APIRouter(prefix="/api")
api_router.include_router(public_version.router, prefix="/public", tags=["public"])
api_router.include_router(auth_router.router, prefix="/auth", tags=["auth"])
api_router.include_router(account_router.router, prefix="/account", tags=["account"])
