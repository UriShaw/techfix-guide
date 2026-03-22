"""
ocr_reader.py — Async EasyOCR wrapper for TechFix Guide
Uses EasyOCR for superior multilingual accuracy (EN + VI).
"""

import re
import asyncio
from pathlib import Path
from typing import Optional

# EasyOCR is imported lazily to avoid slow startup
_reader = None


def _get_reader():
    """Lazy-load EasyOCR reader (heavy init, done once)."""
    global _reader
    if _reader is None:
        import easyocr
        _reader = easyocr.Reader(["en", "vi"], gpu=False, verbose=False)
    return _reader


async def extract_text_from_image(image_path: str) -> str:
    """
    Run EasyOCR in a thread pool to keep FastAPI async.
    Returns combined text extracted from the image.
    """
    loop = asyncio.get_running_loop()
    text = await loop.run_in_executor(None, _run_ocr, image_path)
    return text


def _run_ocr(image_path: str) -> str:
    """Synchronous OCR call (runs in thread pool)."""
    import cv2
    import numpy as np

    # Pre-process image for better OCR accuracy
    img = cv2.imread(image_path)
    if img is None:
        return ""

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Adaptive thresholding — helps with varying backgrounds
    processed = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )

    # Denoise
    denoised = cv2.fastNlMeansDenoising(processed, h=10)

    # Scale up small images for better accuracy
    h, w = denoised.shape
    if max(h, w) < 1000:
        scale = 2
        denoised = cv2.resize(
            denoised, (w * scale, h * scale),
            interpolation=cv2.INTER_CUBIC
        )

    reader = _get_reader()
    results = reader.readtext(denoised, detail=0, paragraph=True)
    return "\n".join(results)


def extract_error_codes(text: str) -> list[str]:
    """
    Extract Windows error codes and common error patterns from OCR text.
    """
    patterns = [
        r"0x[0-9A-Fa-f]{7,8}",           # Windows BSOD hex codes
        r"Error\s*(?:Code|:)?\s*[\w\-]+", # Generic "Error: XXX"
        r"\b[A-Z]{2,6}-\d{3,6}\b",        # Custom codes like NET-001
        r"0x\d{4}",                        # Short hex codes
        r"STOP\s*:\s*0x[0-9A-Fa-f]+",     # STOP codes
        r"\b\d{4,6}\b",                    # Numeric error codes
    ]
    codes = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        codes.extend(matches)

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for c in codes:
        if c.upper() not in seen:
            seen.add(c.upper())
            unique.append(c)
    return unique


async def analyze_error_image(image_path: str) -> dict:
    """
    Full OCR pipeline: extract text → extract error codes → return dict.
    """
    raw_text = await extract_text_from_image(image_path)
    error_codes = extract_error_codes(raw_text)

    return {
        "raw_text": raw_text,
        "error_codes": error_codes,
        "has_errors": len(error_codes) > 0,
    }
