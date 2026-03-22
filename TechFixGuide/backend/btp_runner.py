"""
btp_runner.py — BTP Tool 2026 runner endpoint
Add this to routes.py or import into app.py
"""

import asyncio
import json
import subprocess
import os
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

btp_router = APIRouter()

# Path to BTP Tool exe — place the extracted exe here
BTP_EXE_PATH = Path(__file__).parent.parent / "scripts" / "BTP Tool 2026 Final.exe"


def log(msg: str, type_: str = "", progress: int = 0, status: str = "") -> str:
    """Serialize a log line as JSON."""
    return json.dumps({
        "msg":      msg,
        "type":     type_,
        "progress": progress,
        "status":   status,
    }, ensure_ascii=False) + "\n"


async def stream_btp_execution():
    """
    Run BTP Tool 2026 Final.exe and stream output line by line.
    Falls back to simulation if exe not found.
    """
    yield log("BTP Tool 2026 Final — Khởi động...", "info", 5, "Đang khởi động...")

    if not BTP_EXE_PATH.exists():
        # ── Exe not found: stream a helpful message ──
        yield log(f"⚠ Không tìm thấy exe tại: {BTP_EXE_PATH}", "warn", 10)
        yield log("💡 Hướng dẫn: Giải nén BTP Tool 2026 Final.rar (pass: 1) vào thư mục scripts/", "info", 12)
        yield log("Đang chạy chế độ demo...", "info", 15, "Demo mode")

        # Demo simulation steps
        demo_steps = [
            ("Kiểm tra quyền Administrator...",      "info",  20, 600),
            ("✓ Quyền Administrator: OK",             "ok",    25, 400),
            ("Phân tích hệ thống...",                 "info",  30, 800),
            ("✓ Hệ thống sẵn sàng",                   "ok",    35, 400),
            ("━━━ MODULE 1: Dọn Dẹp ━━━",             "info",  38, 500),
            ("Xóa Temp files...",                     "",      45, 700),
            ("✓ 847 MB đã được giải phóng",            "ok",    52, 600),
            ("Xóa Windows Cache...",                  "",      58, 800),
            ("✓ 1.2 GB Cache cleared",                 "ok",    64, 500),
            ("━━━ MODULE 2: Tối Ưu Boot ━━━",         "info",  67, 500),
            ("Phân tích Startup Programs...",         "",      72, 900),
            ("✓ Tắt 6 startup apps không cần",        "ok",    77, 600),
            ("━━━ MODULE 3: Hardware Check ━━━",      "info",  80, 500),
            ("Kiểm tra RAM, Disk, CPU temp...",       "",      84, 1000),
            ("✓ Tất cả phần cứng: Bình thường",       "ok",    88, 600),
            ("━━━ MODULE 4: Network Fix ━━━",         "info",  91, 400),
            ("Flush DNS, Reset Winsock...",           "",      95, 700),
            ("✓ Mạng đã được tối ưu",                 "ok",    98, 400),
            ("✅ BTP Tool hoàn tất!",                  "ok",   100, 200),
        ]
        for msg, type_, progress, delay_ms in demo_steps:
            await asyncio.sleep(delay_ms / 1000)
            yield log(msg, type_, progress, f"Đang xử lý... {progress}%")
        return

    # ── Exe found: run it and stream stdout ──────────────────
    yield log(f"✓ Tìm thấy: {BTP_EXE_PATH.name}", "ok", 8, "Đang khởi động exe...")

    try:
        process = await asyncio.create_subprocess_exec(
            str(BTP_EXE_PATH),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=str(BTP_EXE_PATH.parent),
        )

        yield log("✓ Process khởi động thành công", "ok", 12)

        line_count = 0
        async for raw_line in process.stdout:
            line = raw_line.decode("utf-8", errors="replace").rstrip()
            if not line:
                continue
            line_count += 1

            # Detect type from content
            type_ = ""
            if any(x in line for x in ["✓", "[OK]", "success", "done", "complete"]):
                type_ = "ok"
            elif any(x in line for x in ["ERROR", "error", "failed", "FAILED"]):
                type_ = "err"
            elif any(x in line for x in ["WARNING", "warn", "⚠"]):
                type_ = "warn"
            elif any(x in line for x in ["━━", "===", "MODULE", "---"]):
                type_ = "info"

            # Rough progress estimate (0 → 95 over 50 lines)
            progress = min(12 + int(line_count * 1.7), 95)
            yield log(line, type_, progress, f"Đang xử lý... {progress}%")

        await process.wait()
        exit_code = process.returncode

        if exit_code == 0:
            yield log("✅ BTP Tool hoàn tất thành công!", "ok", 100, "Hoàn tất!")
        else:
            yield log(f"⚠ Process kết thúc với exit code: {exit_code}", "warn", 100)

    except PermissionError:
        yield log("❌ Cần quyền Administrator để chạy BTP Tool.", "err", 0)
        yield log("💡 Mở Terminal/PowerShell với 'Run as Administrator' rồi thử lại.", "info", 0)
    except Exception as e:
        yield log(f"❌ Lỗi khi chạy exe: {e}", "err", 0)


@btp_router.post("/run-btp-tool", tags=["BTP Tool"])
async def run_btp_tool():
    """
    Stream BTP Tool execution output as NDJSON.
    Each line is a JSON object: { msg, type, progress, status }
    """
    return StreamingResponse(
        stream_btp_execution(),
        media_type="application/x-ndjson",
        headers={"X-Content-Type-Options": "nosniff"},
    )
