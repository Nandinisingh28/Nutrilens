# NutriLens

A full-stack nutrition label scanning application with OCR, NLP rule engine, and premium health-tech UI.

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.10+ (for local backend development)
- TablePlus or similar DB client (optional)

### Using Docker Compose (Recommended)

```bash
# Clone and navigate to the project
cd nutrilens

# Copy environment file
cp .env.example .env

# Start all services
./scripts/dev-up.sh
# Or on Windows: docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
./scripts/dev-down.sh
# Or: docker-compose down

# Reset (wipe database and restart)
./scripts/dev-reset.sh
```

### Access Points

| Service   | URL                          |
|-----------|------------------------------|
| Frontend  | http://localhost:5173        |
| Backend   | http://localhost:8000        |
| API Docs  | http://localhost:8000/docs   |
| MySQL     | localhost:3306               |

---

## 🔗 TablePlus Connection

Connect to the MySQL database using:

| Field    | Value            |
|----------|------------------|
| Host     | `localhost`      |
| Port     | `3306`           |
| User     | `nutrilens`      |
| Password | `nutrilens_dev`  |
| Database | `nutrilens`      |

---

## 🛠️ Local Development

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build
```

---

## 📁 Project Structure

```
nutrilens/
├── README.md
├── .gitignore
├── docker-compose.yml
├── .env.example
├── scripts/
│   ├── dev-up.sh
│   ├── dev-down.sh
│   └── dev-reset.sh
├── backend/
│   ├── pyproject.toml
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   ├── db/
│   │   ├── api/
│   │   ├── services/
│   │   ├── schemas/
│   │   └── utils/
│   └── README.md
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── src/
    │   ├── main.tsx
    │   ├── app/
    │   ├── components/
    │   ├── pages/
    │   └── styles/
    └── index.html
```

---

## 🔑 Environment Variables

Copy `.env.example` to `.env` and configure:

### Database
- `MYSQL_HOST` - MySQL host (default: `mysql` in Docker, `localhost` for local)
- `MYSQL_PORT` - MySQL port (default: `3306`)
- `MYSQL_USER` - Database user
- `MYSQL_PASSWORD` - Database password
- `MYSQL_DATABASE` - Database name

### Authentication
- `JWT_SECRET_KEY` - Secret key for JWT signing
- `JWT_ALGORITHM` - JWT algorithm (default: `HS256`)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration time

### Backend
- `BACKEND_CORS_ORIGINS` - Allowed CORS origins

### Frontend
- `VITE_API_URL` - Backend API URL

---

## 📋 API Endpoints

| Method | Endpoint              | Description            |
|--------|-----------------------|------------------------|
| GET    | `/health`             | Health check           |
| POST   | `/api/v1/auth/register` | User registration    |
| POST   | `/api/v1/auth/login`    | User login           |
| POST   | `/api/v1/auth/refresh`  | Refresh token        |
| GET    | `/api/v1/users/me`      | Get current user     |
| PUT    | `/api/v1/users/me`      | Update current user  |
| GET    | `/api/v1/categories`    | List categories      |
| POST   | `/api/v1/scans`         | Create scan          |
| GET    | `/api/v1/scans`         | List user scans      |
| GET    | `/api/v1/scans/{id}`    | Get scan by ID       |
| POST   | `/api/v1/files/upload`  | Upload file          |
| GET    | `/api/v1/rules`         | List rules           |

---

## 🎨 Tech Stack

### Frontend
- React 18 + TypeScript
- Vite
- TailwindCSS + shadcn/ui
- Framer Motion (animations)
- React Router (routing)
- TanStack Query (data fetching)
- React Hook Form + Zod (forms & validation)
- Sonner (toasts)

### Backend
- Python 3.10+
- FastAPI
- SQLAlchemy 2.0 (async)
- Alembic (migrations)
- MySQL 8
- JWT authentication
- pytesseract + OpenCV (OCR)

---

## 📄 License

MIT License - see LICENSE file for details.
