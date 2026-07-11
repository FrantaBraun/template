import json

from fastapi import APIRouter, HTTPException

from app.config import BASE_DIR

router = APIRouter()

VERSION_FILE = BASE_DIR / "version.json"


@router.get("/version")
def get_version() -> dict:
    try:
        return json.loads(VERSION_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="version.json not found") from exc
