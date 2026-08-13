# Universal AI File Converter

A production-ready, modular SaaS platform for converting, extracting, and
AI-processing files across every major category. Built with FastAPI + React.

---

## Tech Stack

| Layer       | Technology                                          |
|-------------|-----------------------------------------------------|
| Frontend    | React 19, Vite, Tailwind CSS v3, React Router v6, Axios |
| Backend     | Python 3.12, FastAPI, Uvicorn, SQLAlchemy, Alembic  |
| Auth        | JWT (access + refresh), bcrypt password hashing     |
| Queue       | Celery + Redis (falls back to eager / synchronous)  |
| Database    | PostgreSQL (production) / SQLite (development)      |
| Storage     | Local filesystem (dev) / S3-compatible (production) |
| AI / OCR    | Tesseract (local), Anthropic Claude API (optional)  |
| Deployment  | Docker, Docker Compose, Nginx reverse proxy         |

---

## Supported Conversions (fully implemented)

| Category  | Engines used                   | Formats                                     |
|-----------|-------------------------------|----------------------------------------------|
| Images    | Pillow, cairosvg              | PNG, JPG, WEBP, GIF, BMP, TIFF, ICO, SVG→raster |
| Documents | PyMuPDF, python-docx          | PDF ↔ TXT / MD / PNG / DOCX                  |
| Documents | LibreOffice headless          | DOCX, DOC, ODT, RTF, PPTX, XLSX ↔ PDF / each other |
| Text      | Pure Python                   | TXT ↔ MD ↔ HTML                              |
| Audio     | FFmpeg                        | MP3, WAV, AAC, FLAC, OGG ↔ each other       |
| Video     | FFmpeg                        | MP4, AVI, MOV, MKV, WEBM ↔ each other       |
| Archives  | zipfile, tarfile, py7zr       | ZIP, TAR, GZ, 7Z ↔ each other; RAR (extract only) |
| Code/Data | PyYAML, xmltodict, Pygments   | JSON ↔ YAML ↔ XML; code → syntax-highlighted HTML |
| Ebooks    | Calibre CLI (optional)        | EPUB, MOBI, AZW3 ↔ each other               |
| OCR       | Tesseract (local, no API key) | Image → text; Scanned PDF → searchable PDF   |
| AI tasks  | Anthropic Claude API          | Summarise, tags, keywords, translate, headings, metadata |

---

## Quick Start (local development, no Docker)

```bash
# 1. Clone
git clone <repo-url> && cd converter-platform

# 2. Backend setup
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # Edit JWT_SECRET_KEY at minimum
alembic upgrade head    # Creates the SQLite dev database
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 3. Frontend setup (new terminal)
cd frontend
npm install
npm run dev             # Starts on http://localhost:5173
                        # Proxies /api → localhost:8000 automatically

# 4. Open http://localhost:5173
```

API docs (Swagger): http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc

---

## Production Deployment (Docker Compose)

```bash
cp .env.example .env
# Fill in: JWT_SECRET_KEY, POSTGRES_PASSWORD, FRONTEND_URL
# Optionally: STORAGE_BACKEND=s3 + AWS_* vars, ANTHROPIC_API_KEY

docker compose up -d --build

# Run migrations (one-time or after schema changes):
docker compose exec api alembic upgrade head
```

Nginx listens on ports 80 (→ HTTPS redirect) and 443.
Mount your TLS certificates to `./nginx/ssl/fullchain.pem` and `./nginx/ssl/privkey.pem`.

---

## Architecture: how to add a new format

1. Write a class inheriting from `BaseConverter` in `backend/app/converters/`
2. Set `category`, `supported_conversions`, and implement `convert()`
3. Add the class to `_ALL_CONVERTERS` in `backend/app/converters/registry.py`
4. Add the extension → category mapping to `CATEGORY_BY_EXTENSION` in `backend/app/utils/validation.py`

That's it. No other files need to change.

---

## Running Tests

```bash
cd backend
source venv/bin/activate
pytest tests/ -v
# 20 tests covering auth flows, security, and every live converter engine
```

---

## Project Structure

```
converter-platform/
├── backend/
│   ├── app/
│   │   ├── api/routes/       # FastAPI endpoints (auth, files, convert, ai, admin)
│   │   ├── auth/             # JWT + bcrypt security
│   │   ├── converters/       # Format converters + registry
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── schemas/          # Pydantic request/response models
│   │   ├── services/         # Business logic (file, conversion, AI)
│   │   ├── storage/          # Storage backends (local, S3)
│   │   ├── utils/            # Validation, sanitization
│   │   ├── workers/          # Celery tasks
│   │   ├── config.py         # Pydantic Settings
│   │   ├── database.py       # SQLAlchemy engine/session
│   │   └── main.py           # FastAPI app entrypoint
│   ├── alembic/              # Database migrations
│   ├── tests/                # pytest suite (20 tests, all passing)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/              # Axios client + typed helpers
│   │   ├── components/       # Navbar, UploadCard, StatusBadge, StatCard
│   │   ├── context/          # AuthContext (user state, dark mode)
│   │   └── pages/            # Home, Login, Register, Dashboard, History, Settings, Admin, Docs, Pricing
│   ├── Dockerfile
│   └── vite.config.js
├── nginx/nginx.conf
├── docker-compose.yml
└── .env.example
```

---

## What still needs to be added before going live

| Item | Status | Note |
|------|--------|------|
| Email delivery (password reset) | Scaffolded | Wire up SES/Postmark in auth routes |
| Billing / subscription enforcement | Not implemented | Spec calls for future SaaS plans |
| File virus scanning | Scaffolded | Integrate ClamAV in the upload flow |
| Video conversion (large files) | Working | Needs robust worker memory limits in prod |
| Ebook conversion | Scaffolded | Install `calibre` on workers |
| RAR extraction | Scaffolded | Install `unrar` system package |
| Google Drive / Dropbox integration | Roadmap item | Spec marks as future |
| Webhook notifications | Roadmap item | Add a Celery task to POST to a user URL on completion |
