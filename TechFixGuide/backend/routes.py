"""
routes.py — All API endpoints for TechFix Guide
"""

import os
import shutil
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import Device, OperatingSystem, ErrorCategory, Error, Script, Guide, ErrorScript
from ocr_reader import analyze_error_image

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# ─────────────────────────────────────────────────────────────
# Dependency: DB session injected per request
# ─────────────────────────────────────────────────────────────
async def get_db() -> AsyncSession:
    from app import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        yield session


# ─────────────────────────────────────────────────────────────
# GET /devices
# ─────────────────────────────────────────────────────────────
@router.get("/devices", tags=["Lookup"])
async def get_devices(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Device))
    devices = result.scalars().all()
    return [{"id": d.id, "device_name": d.device_name} for d in devices]


# ─────────────────────────────────────────────────────────────
# GET /os
# ─────────────────────────────────────────────────────────────
@router.get("/os", tags=["Lookup"])
async def get_os(
    device_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(OperatingSystem)
    if device_id:
        stmt = stmt.where(OperatingSystem.device_id == device_id)
    result = await db.execute(stmt)
    os_list = result.scalars().all()
    return [{"id": o.id, "os_name": o.os_name, "device_id": o.device_id} for o in os_list]


# ─────────────────────────────────────────────────────────────
# GET /categories
# ─────────────────────────────────────────────────────────────
@router.get("/categories", tags=["Lookup"])
async def get_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ErrorCategory))
    cats = result.scalars().all()
    return [{"id": c.id, "category_name": c.category_name, "description": c.description} for c in cats]


# ─────────────────────────────────────────────────────────────
# POST /diagnostic
# ─────────────────────────────────────────────────────────────
@router.post("/diagnostic", tags=["Diagnostic"])
async def run_diagnostic(payload: dict, db: AsyncSession = Depends(get_db)):
    device_name  = payload.get("device", "")
    os_name      = payload.get("os", "")
    category_name = payload.get("category", "")

    stmt = (
        select(Error)
        .options(
            selectinload(Error.device),
            selectinload(Error.os),
            selectinload(Error.category),
            selectinload(Error.error_scripts).selectinload(ErrorScript.script),
        )
        .join(Error.device, isouter=True)
        .join(Error.os, isouter=True)
        .join(Error.category, isouter=True)
    )

    if device_name:
        stmt = stmt.where(Device.device_name.ilike(f"%{device_name}%"))
    if os_name:
        stmt = stmt.where(OperatingSystem.os_name.ilike(f"%{os_name}%"))
    if category_name:
        stmt = stmt.where(ErrorCategory.category_name.ilike(f"%{category_name}%"))

    result = await db.execute(stmt)
    errors = result.scalars().unique().all()

    return {
        "count": len(errors),
        "errors": [
            {
                "id":          e.id,
                "error_code":  e.error_code,
                "error_name":  e.error_name,
                "description": e.description,
                "solution":    e.solution,
                "video_link":  e.video_link,
                "severity":    e.severity,
                "device":      e.device.device_name if e.device else None,
                "os":          e.os.os_name if e.os else None,
                "category":    e.category.category_name if e.category else None,
                "scripts": [
                    {
                        "id":          es.script.id,
                        "script_name": es.script.script_name,
                        "script_type": es.script.script_type,
                        "note":        es.note,
                    }
                    for es in e.error_scripts
                ],
            }
            for e in errors
        ],
    }


# ─────────────────────────────────────────────────────────────
# GET /guides
# ─────────────────────────────────────────────────────────────
@router.get("/guides", tags=["Guides"])
async def get_guides(
    device_type: Optional[str] = None,
    os_type:     Optional[str] = None,
    category:    Optional[str] = None,
    search:      Optional[str] = None,
    limit:       int = 20,
    offset:      int = 0,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Guide)
    if device_type:
        stmt = stmt.where(Guide.device_type.ilike(f"%{device_type}%"))
    if os_type:
        stmt = stmt.where(Guide.os_type.ilike(f"%{os_type}%"))
    if category:
        stmt = stmt.where(Guide.category.ilike(f"%{category}%"))
    if search:
        stmt = stmt.where(
            or_(Guide.title.ilike(f"%{search}%"), Guide.content.ilike(f"%{search}%"))
        )
    stmt = stmt.offset(offset).limit(limit)
    result = await db.execute(stmt)
    guides = result.scalars().all()
    return [
        {
            "id":          g.id,
            "title":       g.title,
            "device_type": g.device_type,
            "os_type":     g.os_type,
            "category":    g.category,
            "view_count":  g.view_count,
            "excerpt":     (g.content or "")[:200],
        }
        for g in guides
    ]


# ─────────────────────────────────────────────────────────────
# GET /guides/{guide_id}
# ─────────────────────────────────────────────────────────────
@router.get("/guides/{guide_id}", tags=["Guides"])
async def get_guide(guide_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Guide).where(Guide.id == guide_id))
    guide = result.scalar_one_or_none()
    if not guide:
        raise HTTPException(status_code=404, detail="Guide not found")

    # Increment view count
    guide.view_count = (guide.view_count or 0) + 1
    await db.commit()

    return {
        "id":          guide.id,
        "title":       guide.title,
        "content":     guide.content,
        "device_type": guide.device_type,
        "os_type":     guide.os_type,
        "category":    guide.category,
        "view_count":  guide.view_count,
    }


# ─────────────────────────────────────────────────────────────
# GET /scripts
# ─────────────────────────────────────────────────────────────
@router.get("/scripts", tags=["Scripts"])
async def get_scripts(
    script_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Script)
    if script_type:
        stmt = stmt.where(Script.script_type == script_type)
    result = await db.execute(stmt)
    scripts = result.scalars().all()
    return [
        {
            "id":             s.id,
            "script_name":    s.script_name,
            "description":    s.description,
            "script_type":    s.script_type,
            "compatible_os":  s.compatible_os,
            "download_count": s.download_count,
            "file_path":      s.file_path,
        }
        for s in scripts
    ]


# ─────────────────────────────────────────────────────────────
# GET /scripts/download/{script_id}
# ─────────────────────────────────────────────────────────────
@router.get("/scripts/download/{script_id}", tags=["Scripts"])
async def download_script(script_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Script).where(Script.id == script_id))
    script = result.scalar_one_or_none()
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")

    script.download_count = (script.download_count or 0) + 1
    await db.commit()

    return {
        "script_name": script.script_name,
        "file_path":   script.file_path,
        "script_type": script.script_type,
    }


# ─────────────────────────────────────────────────────────────
# POST /scan-error  (EasyOCR)
# ─────────────────────────────────────────────────────────────
@router.post("/scan-error", tags=["OCR"])
async def scan_error(
    file: UploadFile = File(...),
    db:   AsyncSession = Depends(get_db),
):
    # Validate file type
    allowed = {"image/jpeg", "image/png", "image/webp", "image/bmp"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Only image files are accepted (JPEG, PNG, WEBP, BMP)")

    # Save temp file
    suffix = Path(file.filename).suffix or ".jpg"
    tmp_path = UPLOAD_DIR / f"{uuid.uuid4()}{suffix}"
    with open(tmp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        ocr_result = await analyze_error_image(str(tmp_path))
        error_codes = ocr_result["error_codes"]
        raw_text    = ocr_result["raw_text"]

        matched_errors = []
        if error_codes:
            for code in error_codes:
                stmt = (
                    select(Error)
                    .options(
                        selectinload(Error.device),
                        selectinload(Error.os),
                        selectinload(Error.category),
                    )
                    .where(Error.error_code.ilike(f"%{code}%"))
                )
                res = await db.execute(stmt)
                found = res.scalars().all()
                for e in found:
                    matched_errors.append({
                        "id":          e.id,
                        "error_code":  e.error_code,
                        "error_name":  e.error_name,
                        "description": e.description,
                        "solution":    e.solution,
                        "severity":    e.severity,
                        "device":      e.device.device_name if e.device else None,
                        "os":          e.os.os_name if e.os else None,
                        "category":    e.category.category_name if e.category else None,
                    })

        # Full-text search fallback if no code matches
        if not matched_errors and raw_text:
            keywords = [w for w in raw_text.split() if len(w) > 4][:10]
            for kw in keywords:
                stmt = (
                    select(Error)
                    .options(
                        selectinload(Error.device),
                        selectinload(Error.os),
                        selectinload(Error.category),
                    )
                    .where(
                        or_(
                            Error.error_name.ilike(f"%{kw}%"),
                            Error.description.ilike(f"%{kw}%"),
                        )
                    )
                    .limit(3)
                )
                res = await db.execute(stmt)
                found = res.scalars().unique().all()
                for e in found:
                    if not any(m["id"] == e.id for m in matched_errors):
                        matched_errors.append({
                            "id":          e.id,
                            "error_code":  e.error_code,
                            "error_name":  e.error_name,
                            "description": e.description,
                            "solution":    e.solution,
                            "severity":    e.severity,
                            "device":      e.device.device_name if e.device else None,
                            "os":          e.os.os_name if e.os else None,
                            "category":    e.category.category_name if e.category else None,
                        })
                if len(matched_errors) >= 5:
                    break

        return {
            "raw_text":      raw_text,
            "error_codes":   error_codes,
            "matched_count": len(matched_errors),
            "results":       matched_errors[:10],
        }

    finally:
        tmp_path.unlink(missing_ok=True)


# ─────────────────────────────────────────────────────────────
# GET /search
# ─────────────────────────────────────────────────────────────
@router.get("/search", tags=["Search"])
async def global_search(q: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Error)
        .options(selectinload(Error.device), selectinload(Error.os), selectinload(Error.category))
        .where(
            or_(
                Error.error_name.ilike(f"%{q}%"),
                Error.error_code.ilike(f"%{q}%"),
                Error.description.ilike(f"%{q}%"),
            )
        )
        .limit(20)
    )
    res = await db.execute(stmt)
    errors = res.scalars().unique().all()

    guides_stmt = select(Guide).where(
        or_(Guide.title.ilike(f"%{q}%"), Guide.content.ilike(f"%{q}%"))
    ).limit(10)
    guides_res = await db.execute(guides_stmt)
    guides = guides_res.scalars().all()

    return {
        "query":  q,
        "errors": [{"id": e.id, "error_name": e.error_name, "error_code": e.error_code} for e in errors],
        "guides": [{"id": g.id, "title": g.title, "device_type": g.device_type} for g in guides],
    }
