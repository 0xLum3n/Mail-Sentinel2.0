Yes — the backend is ready at the current build.

[Download **Mail Sentinel 2.0 Backend**](sandbox:/mnt/data/mail-sentinel-backend-current.zip)

And the currently connected frontend is here:

[Download **Mail Sentinel 2.0 Frontend**](sandbox:/mnt/data/mail-sentinel-frontend-current.zip)

## Full technology installation

The project currently uses:

**Frontend**

* Next.js 16.3.3
* React 19
* TypeScript 5.7.3
* Tailwind CSS 4
* shadcn/Base UI
* Vercel AI SDK

**Backend**

* Python
* FastAPI
* Uvicorn
* PostgreSQL
* SQLAlchemy 2.x
* Alembic
* Redis
* Pydantic Settings
* JWT authentication
* Passlib/Bcrypt
* HTTPX
* AI provider API
* VirusTotal / AbuseIPDB / urlscan integrations

For development, I recommend running **PostgreSQL and Redis through Docker**, rather than installing them directly into Windows.

---

# 1. Install the system prerequisites

On Windows, install:

### Python

Use Python **3.12**.

Check:

```powershell
python --version
```

You want something like:

```text
Python 3.12.x
```

### Node.js

Install Node.js **22 LTS**.

Check:

```powershell
node --version
npm --version
```

### pnpm

The frontend is using pnpm and already contains `pnpm-lock.yaml`.

Install:

```powershell
npm install -g pnpm
```

Check:

```powershell
pnpm --version
```

### Docker Desktop

Install Docker Desktop and make sure it is running.

Check:

```powershell
docker --version
docker compose version
```

---

# 2. Extract the project

I recommend creating:

```text
mail-sentinel/
├── frontend/
└── backend/
```

Put the frontend ZIP contents inside `frontend`.

Put the backend ZIP contents inside `backend`.

The backend ZIP is already correctly rooted, so you should get:

```text
backend/
├── app/
├── alembic/
├── tests/
├── requirements.txt
├── .env.example
└── alembic.ini
```

---

# 3. Start PostgreSQL and Redis

From the project root, create a file:

```text
docker-compose.yml
```

Use:

```yaml
services:
  postgres:
    image: postgres:16
    container_name: mail-sentinel-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: mail_sentinel
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - mail_sentinel_postgres:/var/lib/postgresql/data

  redis:
    image: redis:7
    container_name: mail-sentinel-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - mail_sentinel_redis:/data

volumes:
  mail_sentinel_postgres:
  mail_sentinel_redis:
```

Then:

```powershell
docker compose up -d
```

Check:

```powershell
docker ps
```

You should see both:

```text
mail-sentinel-postgres
mail-sentinel-redis
```

---

# 4. Install the backend

Go into the backend:

```powershell
cd backend
```

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

then:

```powershell
.venv\Scripts\Activate.ps1
```

Upgrade pip:

```powershell
python -m pip install --upgrade pip
```

Install everything:

```powershell
pip install -r requirements.txt
```

That installs the backend Python stack already defined by the project:

```text
fastapi
uvicorn
sqlalchemy
psycopg
alembic
redis
pydantic-settings
python-dotenv
python-jose
passlib
email-validator
python-multipart
pytest
httpx
```

---

# 5. Configure backend environment

Copy:

```powershell
copy .env.example .env
```

Open:

```text
backend/.env
```

At minimum, set:

```env
SECRET_KEY=put-a-long-random-secret-here

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=mail_sentinel
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

CORS_ORIGINS=http://localhost:3000
```

For the AI features:

```env
AI_PROVIDER=openai
AI_MODEL=your-model-name
AI_API_KEY=your-api-key
AI_BASE_URL=https://api.openai.com/v1
```

Threat-intelligence providers are optional:

```env
VIRUSTOTAL_API_KEY=
ABUSEIPDB_API_KEY=
URLSCAN_API_KEY=
```

You can start the application without those keys; those integrations simply won't have external reputation data available.

---

# 6. Generate a secure SECRET_KEY

Don't use the example value in production.

Generate one with Python:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Put the resulting value into:

```env
SECRET_KEY=...
```

---

# 7. Run the database migrations

Still inside `backend` with `.venv` active:

```powershell
alembic upgrade head
```

This creates the Mail Sentinel database schema.

---

# 8. Start the FastAPI backend

Run:

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend:

```text
http://localhost:8000
```

FastAPI documentation:

```text
http://localhost:8000/docs
```

Health check:

```text
http://localhost:8000/api/v1/health/live
```

Readiness check:

```text
http://localhost:8000/api/v1/health/ready
```

Keep this terminal running.

---

# 9. Install the frontend

Open a **new PowerShell terminal**.

Go to:

```powershell
cd frontend
```

Install the exact dependencies from the lockfile:

```powershell
pnpm install
```

Create:

```text
frontend/.env.local
```

with:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
```

Then start Next.js:

```powershell
pnpm dev
```

Open:

```text
http://localhost:3000
```

---

# 10. Recommended terminal layout

You'll effectively have three processes running:

### Terminal 1 — Infrastructure

```powershell
docker compose up -d
```

### Terminal 2 — Backend

```powershell
cd backend
.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

### Terminal 3 — Frontend

```powershell
cd frontend
pnpm dev
```

Then:

```text
Browser
   │
   ▼
Next.js :3000
   │
   ▼
FastAPI :8000
   │
   ├── PostgreSQL :5432
   ├── Redis :6379
   ├── AI Provider
   └── Threat Intelligence APIs
```

## 11. Quick verification

After everything is running:

```powershell
curl http://localhost:8000/api/v1/health/live
```

Then:

```powershell
curl http://localhost:8000/api/v1/health/ready
```

The second endpoint should report that PostgreSQL and Redis are available.

For backend tests:

```powershell
cd backend
.venv\Scripts\Activate.ps1
pytest
```

For frontend:

```powershell
cd frontend
pnpm build
```

---

## One important thing

You **do not need to separately install PostgreSQL, Redis, or the Python packages globally**. Docker handles PostgreSQL/Redis, and the Python virtual environment handles the backend packages. Likewise, `pnpm install` handles the entire frontend dependency tree.

So the practical setup is:

```powershell
# infrastructure
docker compose up -d

# backend
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# frontend (new terminal)
cd frontend
pnpm install
pnpm dev
```

The only external credentials you need to add yourself are the **AI API key** and, optionally, the **VirusTotal/AbuseIPDB/urlscan API keys**.
