"""
app.py — TechFix Guide FastAPI Application
Async SQLAlchemy + aiomysql for non-blocking DB access.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

import config
from models import Base
from routes import router
from btp_runner import btp_router

# ── Async DB Engine ───────────────────────────────────────────
engine = create_async_engine(
    config.DATABASE_URL,
    echo=config.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# ── FastAPI App ───────────────────────────────────────────────
app = FastAPI(
    title=config.APP_TITLE,
    version=config.APP_VERSION,
    description="TechFix Guide — REST API for laptop & smartphone diagnostics",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# ── CORS ──────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────
app.include_router(router, prefix="/api/v1")
app.include_router(btp_router, prefix="/api/v1")

# ── Serve uploads folder ─────────────────────────────────────
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

# Serve frontend static files (optional — production)
frontend_dir = Path("../frontend")
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")


# ── Events ────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    # Create tables if they don't exist (development convenience)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print(f"✅  TechFix Guide API started — {config.APP_TITLE} v{config.APP_VERSION}")


@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()
    print("🛑  Database engine disposed.")


# ── Health check ─────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "version": config.APP_VERSION}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=config.DEBUG,
        log_level="info",
    )
