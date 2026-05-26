from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.db import read_schema, test_connection

router = APIRouter(tags=["connect"])


class ConnectionRequest(BaseModel):
    host: str
    port: int = 3306
    user: str
    password: str
    database: str


@router.post("/connect")
def connect(request: ConnectionRequest) -> dict:
    """Test DB connection then read and return its schema."""
    try:
        result = test_connection(
            host=request.host,
            port=request.port,
            user=request.user,
            password=request.password,
            database=request.database,
        )
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Connection failed"))

        schema = read_schema(
            host=request.host,
            port=request.port,
            user=request.user,
            password=request.password,
            database=request.database,
        )

        if "error" in schema:
            raise HTTPException(status_code=400, detail=schema["error"])

        table_count: int = schema.get("table_count", 0)
        return {
            "success": True,
            "schema": schema,
            "table_count": table_count,
            "message": f"Connected to {request.database} — {table_count} tables found",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
