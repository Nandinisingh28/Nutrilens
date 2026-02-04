# NutriLens Backend

Production-grade FastAPI backend for the NutriLens nutrition label scanning application.

## Features

- 🔐 JWT Authentication (15 min access, 7 day refresh)
- 📷 OCR with pytesseract + OpenCV
- 🧠 NLP Rule Engine for nutrition claim verification
- 🗃️ MySQL database with SQLAlchemy 2.0
- 📝 Automatic API documentation
- 🚦 Rate limiting for auth endpoints
- 📊 Structured logging

## Quick Start

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Set up environment
cp ../.env.example .env

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔗 TablePlus Connection

Connect to the MySQL database using:

| Field    | Value           |
|----------|-----------------|
| Host     | `localhost`     |
| Port     | `3306`          |
| User     | `nutrilens`     |
| Password | `nutrilens_dev` |
| Database | `nutrilens`     |

## API Endpoints

### Authentication (`/api/auth`)
| Method | Endpoint           | Description                |
|--------|-------------------|----------------------------|
| POST   | `/signup`         | Register new user          |
| POST   | `/login`          | Login (rate limited)       |
| POST   | `/logout`         | Logout (clears cookies)    |
| POST   | `/refresh`        | Refresh access token       |
| POST   | `/forgot-password`| Request password reset     |
| POST   | `/reset-password` | Reset password with token  |

### Users (`/api/users`)
| Method | Endpoint      | Description          |
|--------|--------------|----------------------|
| GET    | `/me`        | Get current user     |
| PUT    | `/me`        | Update profile       |
| POST   | `/me/avatar` | Upload avatar        |
| PUT    | `/me/password` | Change password    |

### Categories (`/api/categories`)
| Method | Endpoint | Description       |
|--------|----------|-------------------|
| GET    | `/`      | List categories   |

### Scans (`/api/scans`)
| Method | Endpoint      | Description                |
|--------|--------------|----------------------------|
| POST   | `/`          | Create scan                |
| GET    | `/`          | List scans (paginated)     |
| GET    | `/{scan_id}` | Get scan by ID             |
| DELETE | `/{scan_id}` | Delete scan                |
| DELETE | `/`          | Bulk delete scans          |

### Files (`/api/files`)
| Method | Endpoint      | Description        |
|--------|--------------|-------------------|
| GET    | `/{file_id}` | Download file     |

## Response Format

All endpoints return a consistent response format:

```json
{
  "success": true,
  "message": "Success",
  "data": {...},
  "error": null
}
```

Error responses:
```json
{
  "success": false,
  "message": "Error description",
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "details": {...}
  }
}
```

## Project Structure

```
app/
├── main.py           # FastAPI app entry point
├── core/             # Configuration, security, logging, rate limiting
├── db/               # Database models, session, migrations
├── api/              # API routes and dependencies
├── services/         # Business logic
├── schemas/          # Pydantic models
└── utils/            # Helper utilities
```

## Database Models

- **User**: Authentication and profile
- **FileAsset**: Uploaded files (avatars, label images)
- **Category**: Product categories (protein-bars, breakfast-cereals)
- **Scan**: Nutrition label analysis records
- **Rule**: Claim verification rules (sugar aliases, thresholds)

## Security Features

- Password policy: min 8 chars, 1 upper, 1 lower, 1 digit
- Rate limiting: 5 login attempts/min, 3 forgot-password/10min
- JWT tokens with proper expiration
- Owner-only file access
- CORS configuration for frontend
