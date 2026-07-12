# Part of the With FBraun project template.
# Author: František Braun <frantisek.braun95@gmail.com>
# Freely available as a template for building custom applications.

import json

from fastapi import APIRouter, HTTPException

from app.config import BASE_DIR

router = APIRouter()

VERSION_FILE = BASE_DIR / "version.json"


@router.get("/version")
def get_version() -> dict:
    """Returns backend/version.json verbatim - this is the health-check
    endpoint scripts/upgrade.sh polls after a restart, and the source the
    frontend's /version page compares against its own version.json to detect
    a major.minor drift between the two independently-versioned components."""
    try:
        return json.loads(VERSION_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="version.json not found") from exc
