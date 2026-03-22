# 🔧 TechFix Guide (TFG) — Trạm Cứu Hộ Công Nghệ

> Hệ thống chẩn đoán lỗi Laptop & Điện thoại thông minh với OCR, script tự động và thư viện kiến thức.

![TechFix Guide](https://img.shields.io/badge/TechFix-Guide-7CFC00?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=for-the-badge)
![PWA](https://img.shields.io/badge/PWA-Ready-5A0FC8?style=for-the-badge)

---

## 📋 Mục Lục

- [Tính năng](#tính-năng)
- [Kiến trúc](#kiến-trúc)
- [Cài đặt](#cài-đặt)
- [Chạy project](#chạy-project)
- [API Reference](#api-reference)
- [Cấu trúc thư mục](#cấu-trúc-thư-mục)

---

## ✨ Tính Năng

| Module | Mô tả |
|--------|-------|
| 🔍 **Diagnostic Tool** | Lọc lỗi theo thiết bị, OS, loại lỗi — nhận giải pháp tức thì |
| 📸 **EasyOCR Scanner** | Upload ảnh màn hình lỗi → AI đọc mã lỗi → tìm giải pháp |
| ⚙️ **Script Tool** | Tải script `.bat`/`.py` tự động sửa lỗi Windows |
| 📚 **Knowledge Library** | Thư viện hướng dẫn Laptop & Mobile: BSOD, WeChat, Douyin... |
| 📴 **PWA Offline** | Cài đặt như app, đọc hướng dẫn khi không có mạng |
| 🔗 **Error→Script Map** | Mỗi lỗi được map với script sửa tự động phù hợp |

---

## 🏗️ Kiến Trúc

```
Frontend (HTML/CSS/JS)  ←→  FastAPI (Python Async)  ←→  MySQL 8.0
        ↓                           ↓
  Service Worker             EasyOCR + OpenCV
  (PWA Offline)          (OCR từ ảnh màn hình lỗi)
```

**Stack công nghệ:**
- **Backend:** FastAPI + SQLAlchemy Async + aiomysql
- **OCR:** EasyOCR (EN + VI) + OpenCV (pre-processing)
- **Database:** MySQL 8.0 (7 bảng + index tối ưu)
- **Frontend:** HTML5 + CSS3 Glassmorphism + Vanilla JS
- **PWA:** Service Worker (Stale-While-Revalidate) + Manifest

---

## 🚀 Cài Đặt

### Yêu cầu hệ thống
- Python 3.10+
- MySQL 8.0+
- Node.js (tuỳ chọn, cho live-server frontend)

### 1. Clone & Setup

```bash
git clone https://github.com/your-repo/techfix-guide.git
cd techfix-guide
```

### 2. Cài đặt MySQL

```bash
# Đăng nhập MySQL
mysql -u root -p

# Import database
mysql -u root -p < database/database.sql
```

### 3. Cài đặt Backend

```bash
cd backend

# Tạo virtual environment
python -m venv venv
source venv/bin/activate      # Linux/macOS
# hoặc
venv\Scripts\activate         # Windows

# Cài packages
pip install -r requirements.txt

# Cấu hình .env
cp .env.example .env
# Chỉnh sửa .env với thông tin MySQL của bạn
```

### 4. Chạy Backend

```bash
cd backend
uvicorn app:app --reload --port 8000
```

API docs: http://localhost:8000/api/docs

### 5. Chạy Frontend

**Option A — Python simple server:**
```bash
cd frontend
python -m http.server 3000
# Mở: http://localhost:3000
```

**Option B — Live Server (VS Code extension):**
Cài extension "Live Server" → Click "Go Live" trong VS Code.

---

## 📡 API Reference

### Base URL: `http://localhost:8000/api/v1`

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/devices` | Danh sách thiết bị |
| GET | `/os` | Danh sách hệ điều hành |
| GET | `/categories` | Danh sách nhóm lỗi |
| POST | `/diagnostic` | Chẩn đoán theo bộ lọc |
| GET | `/guides` | Danh sách hướng dẫn |
| GET | `/guides/{id}` | Chi tiết hướng dẫn |
| GET | `/scripts` | Danh sách script |
| GET | `/scripts/download/{id}` | Tải script |
| POST | `/scan-error` | OCR quét ảnh lỗi |
| GET | `/search?q=` | Tìm kiếm toàn cục |

### POST /diagnostic — Example

```json
// Request
{
  "device": "Laptop",
  "os": "Windows 11",
  "category": "Software"
}

// Response
{
  "count": 3,
  "errors": [
    {
      "id": 1,
      "error_code": "0x0000007E",
      "error_name": "Blue Screen of Death",
      "severity": "critical",
      "solution": "1. Khởi động Safe Mode\n2. Cập nhật driver...",
      "scripts": [
        { "id": 1, "script_name": "Windows Cleaner", "script_type": ".bat" }
      ]
    }
  ]
}
```

### POST /scan-error — OCR Upload

```bash
curl -X POST http://localhost:8000/api/v1/scan-error \
  -F "file=@screenshot_error.png"
```

---

## 📁 Cấu Trúc Thư Mục

```
TechFixGuide/
├── frontend/
│   ├── index.html          # Trang chủ
│   ├── diagnostic.html     # Công cụ chẩn đoán + OCR
│   ├── scripts.html        # Tải script tự động
│   ├── guides.html         # Thư viện hướng dẫn
│   ├── style.css           # Glassmorphism Deep Navy theme
│   ├── manifest.json       # PWA manifest (icons 72→512px)
│   ├── service-worker.js   # Stale-While-Revalidate SW
│   └── assets/
│       └── icons/          # PWA icons (72,96,128,192,512px)
│
├── backend/
│   ├── app.py              # FastAPI entry point
│   ├── config.py           # Config + env vars
│   ├── models.py           # SQLAlchemy async models
│   ├── routes.py           # Tất cả API endpoints
│   ├── ocr_reader.py       # EasyOCR + OpenCV pipeline
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Template biến môi trường
│
├── database/
│   └── database.sql        # Schema + sample data
│
└── scripts/
    ├── windows_cleaner.bat
    ├── battery_check.py
    ├── ssd_health.py
    ├── remove_bloatware.bat
    ├── network_reset.bat
    ├── startup_optimizer.bat
    ├── driver_backup.bat
    └── ram_diagnostic.bat
```

---

## 🗄️ Database Schema

```sql
Devices           → Thiết bị (Laptop, Smartphone)
OperatingSystems  → Hệ điều hành (Windows 10/11, Android, iOS...)
ErrorCategories   → Nhóm lỗi (Software, Hardware, Network...)
Errors            → Lỗi + giải pháp (với severity levels)
Scripts           → Script tự động
Guides            → Bài hướng dẫn
Error_Scripts     → Liên kết Lỗi ↔ Script (bảng mapping)
```

---

## 🎨 Design System

| Token | Value | Dùng cho |
|-------|-------|----------|
| `--primary` | `#7CFC00` | Accent, buttons, highlights |
| `--navy` | `#1A1A2E` | Background chính |
| `--navy-mid` | `#16213E` | Card background |
| `--cream` | `#FFFDD0` | Text primary |
| `--glass-border` | `rgba(255,255,255,0.1)` | Card borders |
| Font Display | Syne | Headers, brand |
| Font Body | DM Sans | Text thường |
| Font Mono | JetBrains Mono | Code, badges |

---

## 📴 PWA Offline Support

Service Worker sử dụng chiến lược **Stale-While-Revalidate**:
- ✅ Phản hồi ngay từ cache (không chờ mạng)
- ✅ Cập nhật cache trong nền sau khi serve
- ✅ Đọc hướng dẫn, xem scripts khi offline
- ✅ API fallback về cached data khi mất mạng

---

## 🤖 EasyOCR Pipeline

```
Upload ảnh → OpenCV pre-process → EasyOCR (EN+VI) → Extract error codes → MySQL query → Return solutions
```

Pre-processing:
1. Grayscale conversion
2. Adaptive thresholding
3. Fast denoising
4. 2x upscale (nếu ảnh nhỏ)

---

## 📄 License

MIT License — TechFix Guide © 2024
