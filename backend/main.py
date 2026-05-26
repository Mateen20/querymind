from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import connect, query

app = FastAPI(
    title="QueryMind API",
    description="Natural Language to SQL backend",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(connect.router, prefix="/api")
app.include_router(query.router, prefix="/api")


@app.get("/")
def root() -> dict:
    return {
        "message": "QueryMind API is running",
        "version": "1.0.0",
        "status": "ok",
    }
