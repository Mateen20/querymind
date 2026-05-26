from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["query"])


@router.post("/query")
def query() -> dict:
    """Placeholder — NL→SQL engine arrives Day 2."""
    return {"message": "Query engine coming Day 2", "status": "placeholder"}


@router.get("/demo")
def demo() -> dict:
    """Placeholder — demo mode arrives Day 7."""
    return {"message": "Demo mode coming Day 7", "status": "placeholder"}


@router.get("/health")
def health() -> dict:
    """Health check endpoint."""
    return {"status": "ok", "service": "QueryMind Backend"}
