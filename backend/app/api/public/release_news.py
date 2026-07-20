# Part of the With FBraun project template.
# Author: František Braun <frantisek.braun95@gmail.com>
# Freely available as a template for building custom applications.

import json

from fastapi import APIRouter, HTTPException

from app.config import BASE_DIR

router = APIRouter()

RELEASE_NEWS_FILE = BASE_DIR / "release_news.json"


@router.get("/release-news")
def get_release_news() -> dict:
    """Returns backend/release_news.json verbatim - {unreleased, releases}.
    scripts/build.py seals unreleased entries into a dated release at build
    time; the frontend's /release-news page fetches this alongside its own
    release_news.json and groups both by major.minor version."""
    try:
        return json.loads(RELEASE_NEWS_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="release_news.json not found") from exc
