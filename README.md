# 🛡️ Mail Sentinel 2.0

![Next.js](https://img.shields.io/badge/Next.js-16.3.3-black?logo=next.js)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5.7.3-3178C6?logo=typescript&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16%2B-4169E1?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7%2B-DC382D?logo=redis&logoColor=white)
![License](https://img.shields.io/badge/status-development-yellow)

Mail Sentinel 2.0 is an AI-powered email security and SOC platform for phishing detection, email forensics, IOC extraction, threat-intelligence enrichment, AI-assisted analysis, investigation management, and analyst assistance.

The repository contains both the Next.js frontend and FastAPI backend.

---

## 📚 Table of contents

| # | Section |
|---|---------|
| 1 | [📦 What is included](#-1-what-is-included) |
| 2 | [🏗️ High-level architecture](#-2-high-level-architecture) |
| 3 | [📁 Repository structure](#-3-repository-structure) |
| 4 | [✅ Prerequisites](#-4-prerequisites) |
| 5 | [📥 Clone the project](#-5-clone-the-project) |
| 6 | [🔐 Protect secrets before pushing to GitHub](#-6-important-protect-secrets-before-pushing-to-github) |
| 7 | [🐘 PostgreSQL setup](#-7-postgresql-setup) |
| 8 | [🔴 Redis setup](#-8-redis-setup) |
| 9 | [⚙️ Backend setup](#-9-backend-setup) |
| 10 | [🔧 Backend environment configuration](#-10-backend-environment-configuration) |
| 11 | [🗄️ Database migrations](#-11-database-migrations) |
| 12 | [▶️ Run the backend](#-12-run-the-backend) |
| 13 | [💓 Backend health checks](#-13-backend-health-checks) |
| 14 | [🧪 Backend tests](#-14-backend-tests) |
| 15 | [🎨 Frontend setup](#-15-frontend-setup) |
| 16 | [🔧 Frontend environment](#-16-frontend-environment) |
| 17 | [▶️ Run the frontend](#-17-run-the-frontend) |
| 18 | [🖥️ Recommended three-terminal workflow](#-18-recommended-three-terminal-workflow) |
| 19 | [🔑 Authentication flow](#-19-authentication-flow) |
| 20 | [📧 Email analysis flow](#-20-email-analysis-flow) |
| 21 | [🌐 Threat intelligence](#-21-threat-intelligence) |
| 22 | [🤖 AI analysis](#-22-ai-analysis) |
| 23 | [🧑‍💻 AI SOC Analyst](#-23-ai-soc-analyst) |
| 24 | [🖼️ Frontend pages/features](#-24-frontend-pagesfeatures) |
| 25 | [🧭 First end-to-end test](#-25-first-end-to-end-test) |
| 26 | [🧵 Useful API testing sequence](#-26-useful-api-testing-sequence) |
| 27 | [🛠️ Common problems and fixes](#-27-common-problems-and-fixes) |
| 28 | [🔒 Security notes](#-28-security-notes) |
| 29 | [🧠 Development philosophy](#-29-development-philosophy) |
| 30 | [⚡ Quick-start summary](#-30-quick-start-summary) |
| 31 | [✅ Current validation status](#-31-current-validation-status) |
| 32 | [🙌 Credits / project notes](#-32-credits--project-notes) |

---

## 📦 1. What is included

### 🎨 Frontend

- Next.js 16.3.3
- React 19
- TypeScript 5.7.3
- Tailwind CSS 4
- shadcn/Base UI components
- Lucide icons
- Vercel AI SDK packages
- Authentication-aware frontend API client
- AI SOC Analyst drawer
- Dashboard / investigations / email-analysis UI

### ⚙️ Backend

- FastAPI
- Uvicorn
- PostgreSQL
- SQLAlchemy 2.x async ORM
- Psycopg 3
- Alembic migrations
- Redis
- Pydantic Settings
- JWT access tokens
- Rotating opaque refresh tokens stored as hashes
- Passlib/Bcrypt password hashing
- RFC822 email parsing
- Security header analysis
- IOC extraction
- Explainable deterministic risk scoring
- Threat-intelligence provider abstraction
- VirusTotal integration
- AbuseIPDB integration
- urlscan.io integration
- Redis TI caching
- AI analysis pipeline
- AI SOC Analyst investigation-aware chat API

---

## 🏗️ 2. High-level architecture

```text
                         Browser
                            |
                            v
                 +----------------------+
                 | Next.js Frontend     |
                 | http://localhost:3000|
                 +----------+-----------+
                            |
                      REST / JSON
                            |
                            v
                 +----------------------+
                 | FastAPI Backend      |
                 | http://localhost:8000|
                 +----------+-----------+
                            |
          +-----------------+------------------+
          |                 |                  |
          v                 v                  v
   +-------------+   +-------------+   +----------------+
   | PostgreSQL  |   |    Redis    |   | External APIs  |
   | :5432       |   | :6379       |   | AI / TI        |
   +-------------+   +-------------+   +----------------+
```

### 📧 Email analysis flow

```text
Upload .eml / .txt / .nine
            |
            v
       Email parser
            |
            v
   Deterministic analysis
   - SPF / DKIM / DMARC
   - Reply-To anomalies
   - Received IPs
   - URLs / domains / hashes
   - Social-engineering signals
   - Attachment metadata
            |
            v
   Threat intelligence
   - VirusTotal
   - AbuseIPDB
   - urlscan
   - Redis cache
            |
            v
      Structured evidence
            |
            v
        AI analysis
            |
            v
     Evidence fusion
            |
            v
        Investigation
            |
            v
      AI SOC Analyst
```

> 💡 Threat-intelligence and AI results are treated as **evidence**. Provider failures and conflicting provider results must not automatically turn an email into a malicious verdict.

---

## 📁 3. Repository structure

```text
MailSentinel2.0 Project/
|
├── Backend/
│   ├── app/
│   │   ├── api/
│   │   ├── ai/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── security/
│   │   ├── services/
│   │   ├── threat_intel/
│   │   ├── workers/
│   │   └── main.py
│   ├── alembic/
│   │   └── versions/
│   ├── tests/
│   ├── scripts/
│   ├── .env.example
│   ├── alembic.ini
│   ├── requirements.txt
│   └── README.md
│
├── Frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── public/
│   ├── .env.example
│   ├── package.json
│   ├── pnpm-lock.yaml
│   └── next.config.mjs
│
├── docker-compose.yml   # optional; review secrets before using/committing
└── README.md
```

---

## ✅ 4. Prerequisites

The instructions below assume Windows + PowerShell, because that is the environment used during development. Linux/macOS work with the same Python/Node commands after adapting activation commands and service installation.

Install:

1. **Git**
2. **Python 3.12 recommended**
3. **Node.js 22 LTS recommended**
4. **pnpm**
5. **PostgreSQL 16+** (PostgreSQL 18 also works in the tested environment)
6. **Redis 7+** or a Redis-compatible local service
7. **An AI API key** for AI analysis/chat
8. Optional threat-intelligence API keys for VirusTotal, AbuseIPDB and urlscan

### 🔍 Check versions

```powershell
python --version
node --version
npm --version
pnpm --version
psql --version
git --version
docker --version
```

Python 3.12 is the recommended development target. Python 3.14 was successfully used during local testing, but Python 3.12 is preferred for maximum package compatibility.

---

## 📥 5. Clone the project

```powershell
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd "MailSentinel2.0 Project"
```

The exact path/name does not matter; just make sure the `Backend` and `Frontend` directories remain siblings.

---

## 🔐 6. IMPORTANT: protect secrets before pushing to GitHub

> ⚠️ **Never commit credentials.**

The following must stay local:

```text
Backend/.env
Frontend/.env.local
```

The backend `.gitignore` and frontend `.gitignore` already ignore local environment files.

Before pushing the repository, inspect `docker-compose.yml`. If it contains a real PostgreSQL password, AI key, Redis password, or any other secret, remove it and replace it with an environment-variable reference or a placeholder.

If a real password/key has already been committed to Git history, treat it as exposed and rotate it.

---

## 🐘 7. PostgreSQL setup

### Option A — Use an existing local PostgreSQL installation

This matches the setup used during development.

Open pgAdmin and create a separate database for Mail Sentinel:

```text
Database: mail_sentinel
Owner:    postgres
```

> 💡 Do not use the default `postgres` database as the application database.

Verify PostgreSQL is running:

```powershell
Get-Service *postgres*
```

Then verify the port:

```powershell
Test-NetConnection localhost -Port 5432
```

Expected:

```text
TcpTestSucceeded : True
```

#### If your existing database is named differently

For example, if you create `mail-sentinel` instead of `mail_sentinel`, put that exact name in `Backend/.env`.

---

### Option B — Run PostgreSQL with Docker

If PostgreSQL is not installed locally, use a PostgreSQL container instead.

Example:

```powershell
docker run --name mail-sentinel-postgres `
  -e POSTGRES_DB=mail_sentinel `
  -e POSTGRES_USER=postgres `
  -e POSTGRES_PASSWORD=CHANGE_THIS_PASSWORD `
  -p 5432:5432 `
  -d postgres:16
```

Then make the same values available in `Backend/.env`.

> ⚠️ Do not run two different PostgreSQL servers bound to port 5432 at the same time.

---

## 🔴 8. Redis setup

Redis is used for threat-intelligence caching and backend runtime support.

Verify it is reachable:

```powershell
Test-NetConnection localhost -Port 6379
```

Expected:

```text
TcpTestSucceeded : True
```

### Docker Redis (recommended for Windows if Redis is not already installed)

```powershell
docker run --name mail-sentinel-redis -p 6379:6379 -d redis:7
```

Check:

```powershell
docker ps
```

> ⚠️ If Redis is already running on Windows, do not start a second Redis service on the same port.

---

## ⚙️ 9. Backend setup

Open a terminal at the repository root and enter the backend:

```powershell
cd Backend
```

### Create the Python virtual environment

```powershell
python -m venv venv
```

Activate it:

```powershell
venv\Scripts\Activate.ps1
```

If PowerShell blocks activation for this session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
venv\Scripts\Activate.ps1
```

You should now see `(venv)` in the terminal prompt.

### Install backend dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The test suite uses `pytest-asyncio`. If it is not already listed in your checked-out `requirements.txt`, install it explicitly:

```powershell
pip install pytest-asyncio
```

### Verify dependency consistency

```powershell
pip check
```

Expected:

```text
No broken requirements found.
```

---

## 🔧 10. Backend environment configuration

Copy the example file:

```powershell
copy .env.example .env
```

Open it:

```powershell
notepad .env
```

Use values appropriate for your machine.

A practical development configuration is:

```env
# Application
APP_NAME=Mail Sentinel API
APP_ENV=development
DEBUG=true
API_V1_PREFIX=/api/v1

# Security
SECRET_KEY=REPLACE_WITH_A_LONG_RANDOM_SECRET
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=14

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=mail_sentinel
POSTGRES_USER=postgres
POSTGRES_PASSWORD=REPLACE_WITH_YOUR_POSTGRES_PASSWORD

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# CORS
CORS_ORIGINS=http://localhost:3000

# AI
AI_PROVIDER=openai
AI_MODEL=REPLACE_WITH_YOUR_MODEL
AI_API_KEY=REPLACE_WITH_YOUR_AI_API_KEY
AI_BASE_URL=https://api.openai.com/v1
AI_TIMEOUT_SECONDS=30

# Threat intelligence (optional)
VIRUSTOTAL_API_KEY=
ABUSEIPDB_API_KEY=
URLSCAN_API_KEY=
THREAT_INTEL_TIMEOUT_SECONDS=8
THREAT_INTEL_CACHE_TTL_SECONDS=3600
```

### 🔑 Generate a strong secret key

```powershell
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Copy the output into `SECRET_KEY`.

### 🗝️ API key behavior

AI keys are required only if you want AI analysis and SOC Analyst responses.

Threat-intelligence keys are optional. The backend is designed to continue analysing an email if a provider is unavailable, unconfigured, times out, or returns unknown evidence.

---

## 🗄️ 11. Database migrations

After PostgreSQL is running and `Backend/.env` is correct:

```powershell
alembic upgrade head
```

Successful migration means the Mail Sentinel database schema has been created.

### 🪟 Windows + Psycopg note

The backend uses async SQLAlchemy/Psycopg. The Alembic environment contains a Windows selector-event-loop workaround so async PostgreSQL connections work correctly on Windows.

Do not remove the selector-event-loop configuration from `Backend/alembic/env.py` when working on Windows unless you have a tested replacement.

---

## ▶️ 12. Run the backend

From `Backend` with the virtual environment active:

```powershell
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend URL:

```text
http://localhost:8000
```

Swagger/OpenAPI:

```text
http://localhost:8000/docs
```

ReDoc:

```text
http://localhost:8000/redoc
```

---

## 💓 13. Backend health checks

### Liveness

Open:

```text
http://localhost:8000/api/v1/health/live
```

Expected:

```json
{"status":"ok"}
```

### Readiness

Open:

```text
http://localhost:8000/api/v1/health/ready
```

Expected structure:

```json
{
  "status": "ok",
  "checks": {
    "postgresql": "ok",
    "redis": "ok"
  }
}
```

The readiness endpoint is the best quick test that FastAPI, PostgreSQL and Redis are communicating.

---

## 🧪 14. Backend tests

Run the complete unit suite from `Backend`:

```powershell
python -m pytest
```

At the point the system was validated during development, the suite contained 10 unit tests and passed:

```text
10 passed
```

If pytest says:

```text
async def functions are not natively supported
```

or shows:

```text
PytestUnknownMarkWarning: Unknown pytest.mark.asyncio
```

install:

```powershell
pip install pytest-asyncio
```

and rerun:

```powershell
python -m pytest
```

---

## 🎨 15. Frontend setup

Open a new terminal and go to the frontend:

```powershell
cd Frontend
```

Install Node dependencies:

```powershell
pnpm install
```

The repository contains `pnpm-lock.yaml`; prefer `pnpm` instead of npm for this project.

If `pnpm` is not installed:

```powershell
npm install -g pnpm
```

Or with supported Node installations using Corepack:

```powershell
corepack enable
```

---

## 🔧 16. Frontend environment

Create:

```text
Frontend/.env.local
```

The easiest option is:

```powershell
copy .env.example .env.local
```

It should contain:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
```

### ⚠️ Important

If `.env.local` is created or changed while Next.js is already running, stop Next.js and restart it. Next.js loads environment variables when the development server starts.

---

## ▶️ 17. Run the frontend

From `Frontend`:

```powershell
pnpm dev
```

Open:

```text
http://localhost:3000
```

Production-style check:

```powershell
pnpm build
pnpm start
```

---

## 🖥️ 18. Recommended three-terminal workflow

### 🟦 Terminal 1 — PostgreSQL / Redis

These can be Windows services or Docker containers. Keep them running.

### 🟨 Terminal 2 — Backend

```powershell
cd Backend
venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --port 8000
```

### 🟩 Terminal 3 — Frontend

```powershell
cd Frontend
pnpm dev
```

Then the local system is:

```text
Frontend   http://localhost:3000
Backend    http://localhost:8000
PostgreSQL localhost:5432
Redis      localhost:6379
```

---

## 🔑 19. Authentication flow

The backend provides:

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
GET  /api/v1/auth/me
```

Registration creates:

```text
User
Organization
OrganizationMembership
```

The backend uses:

- short-lived JWT access tokens
- long-lived opaque refresh tokens
- SHA-256 hashes of refresh tokens in PostgreSQL
- refresh-token rotation
- password hashing with Passlib/Bcrypt

The frontend API client automatically attaches the access token and attempts refresh when it receives a 401 response.

---

## 📧 20. Email analysis flow

The frontend/backend pipeline accepts email files compatible with the current UI, including:

```text
.eml
.txt
.nine
```

The current upload limit is **5 MB**.

Main endpoints:

```text
POST /api/v1/emails
GET  /api/v1/emails/{email_id}
POST /api/v1/emails/{email_id}/analyze
```

The backend stores parsed message data and creates analysis records.

The analysis engine performs:

- SPF analysis
- DKIM analysis
- DMARC analysis
- Reply-To mismatch detection
- Received-header IP extraction
- URL extraction
- domain extraction
- public IP extraction
- email/hash extraction
- risky attachment metadata handling
- social-engineering signal detection
- explainable risk scoring

---

## 🌐 21. Threat intelligence

The threat-intelligence service supports:

### 🦠 VirusTotal

Supports IP, domain, URL and hash lookups.

### 🚫 AbuseIPDB

Supports IP reputation lookups.

### 🔗 urlscan.io

Provides URL/domain search and contextual observations.

### 🔴 Redis cache

Normalized threat-intel results are cached in Redis to reduce repeated external requests.

### ⚠️ Important design rule

Threat-intelligence providers are evidence sources, not unquestionable truth.

Examples:

- a malicious result can raise risk when the evidence is strong
- conflicting providers remain visible in enrichment
- `Unknown` results do not automatically mean malicious
- provider failure does not automatically mean malicious
- urlscan contextual observations do not independently declare an IOC malicious

---

## 🤖 22. AI analysis

The AI layer receives structured security evidence produced by the deterministic analyzer and threat-intelligence layer.

This avoids making the model blindly judge raw email content without evidence.

The AI pipeline can contribute:

- AI risk assessment
- confidence
- contextual reasoning
- additional findings
- recommended analyst actions

AI results are fused conservatively with deterministic/security evidence rather than blindly overwriting stronger security signals.

---

## 🧑‍💻 23. AI SOC Analyst

The backend exposes:

```text
POST /api/v1/ai/chat
```

The frontend AI SOC Analyst sends:

- the selected investigation/email ID
- the user's question
- bounded conversation history

The backend retrieves the investigation context and gives the analyst model structured evidence such as:

- email metadata
- analysis result
- risk/severity
- deterministic findings
- TI-enriched indicators
- MITRE mappings
- AI analysis metadata

The chat is therefore **investigation-aware**, not just a generic chatbot.

A typical test question is:

> Analyze the current investigation and explain the strongest phishing indicators.

Another useful test:

> What IOCs were observed in this investigation?

---

## 🖼️ 24. Frontend pages/features

The frontend currently contains the public product pages, authentication UI, dashboard and security analysis UI.

Important areas include:

```text
/
/about
/pricing
/signin
/dashboard
/dashboard/[section]
```

The dashboard UI includes areas for:

- Dashboard
- Email Analysis
- Investigations
- Threat Intelligence
- Forensic Timeline
- Reports
- Settings
- AI SOC Analyst

---

## 🧭 25. First end-to-end test

After PostgreSQL, Redis, FastAPI and Next.js are running:

### A. 🩺 Check backend

```text
http://localhost:8000/api/v1/health/ready
```

### B. 🌐 Open frontend

```text
http://localhost:3000
```

### C. 👤 Create an account

Go to the sign-in/register page and create a test workspace.

### D. 🔓 Login

Use the same credentials.

### E. 📩 Upload a synthetic test email

Use a harmless local `.eml` test file. Example:

```eml
From: Security Team <security@example.com>
To: analyst@example.com
Subject: Urgent account verification
Authentication-Results: mx.example.com; spf=fail; dkim=fail; dmarc=fail;
Reply-To: attacker@different-example.com

Hello,

Your account requires urgent verification.

Please visit:
https://example.com/verify

Regards,
Security Team
```

> ⚠️ Do not use a real malicious URL as a test target.

### F. 🔍 Run analysis

Confirm that the backend produces:

- risk score
- severity
- verdict
- authentication results
- findings
- indicators
- MITRE mappings when applicable
- AI analysis when AI is configured

### G. 🧑‍💻 Test AI SOC Analyst

Select the investigation and ask:

> Summarize this investigation and explain the strongest indicators.

Then ask:

> What IOCs were observed?

The responses should refer to the selected investigation.

---

## 🧵 26. Useful API testing sequence

A simple backend-only test order is:

```text
GET  /api/v1/health/live
GET  /api/v1/health/ready
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me
POST /api/v1/emails
POST /api/v1/emails/{id}/analyze
GET  /api/v1/emails/{id}
POST /api/v1/ai/chat
POST /api/v1/auth/logout
```

Swagger is available at:

```text
http://localhost:8000/docs
```

Use Swagger when you want to test the backend without depending on the frontend.

---

## 🛠️ 27. Common problems and fixes

### ❌ `ModuleNotFoundError: No module named 'app'`

Run commands from the `Backend` directory and prefer:

```powershell
python -m pytest
```

The Alembic environment includes a project-root path fix so:

```powershell
alembic upgrade head
```

works when launched from the backend directory.

---

### ❌ `async def functions are not natively supported`

Install:

```powershell
pip install pytest-asyncio
```

Then:

```powershell
python -m pytest
```

---

### ❌ `FATAL: password authentication failed for user "postgres"`

PostgreSQL is reachable, but `POSTGRES_PASSWORD` in `Backend/.env` does not match the password configured for the PostgreSQL user.

Fix the password in PostgreSQL/pgAdmin and update `.env`.

Do not confuse a Docker PostgreSQL password with the password for an already-running local PostgreSQL service.

---

### ❌ `connection to server at localhost, port 5432 failed`

Check:

```powershell
Get-Service *postgres*
Test-NetConnection localhost -Port 5432
```

Make sure PostgreSQL is running and no second PostgreSQL instance is competing for the same port.

---

### ❌ Redis connection failure

Check:

```powershell
Test-NetConnection localhost -Port 6379
```

If Redis is not running and Docker is available:

```powershell
docker run --name mail-sentinel-redis -p 6379:6379 -d redis:7
```

---

### ❌ Frontend says `Unable to reach the Mail Sentinel backend`

Check that FastAPI is running on port 8000 and that:

```text
Frontend/.env.local
```

contains:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
```

If `.env.local` was created or changed while Next.js was already running, restart it:

```powershell
Ctrl+C
pnpm dev
```

---

### ⚠️ Browser hydration warning

A browser extension that modifies form inputs before React hydrates can cause a Next.js hydration warning.

For example, password managers/autofill/security extensions may inject styles or controls into email/password inputs.

To distinguish application problems from extension interference, test in a private/incognito window with extensions disabled.

If the warning disappears there, inspect browser extensions before changing React code.

---

### 🪟 Alembic / Psycopg async issues on Windows

Keep the Windows selector-event-loop configuration in:

```text
Backend/alembic/env.py
```

The migration environment is intentionally configured for Windows + async Psycopg.

---

## 🔒 28. Security notes

> 🔒 This is a security product, so treat local development secrets seriously.

Do not commit:

```text
.env
.env.local
API keys
JWT secrets
PostgreSQL passwords
Redis passwords
provider credentials
real emails containing sensitive data
```

Do not put real credentials in source code or README examples.

For production deployment, also add proper:

- secret management
- HTTPS
- secure cookie/token strategy
- rate limiting
- audit logging
- background job execution
- object storage for original email bytes/attachments
- malware/sandbox analysis
- production CORS allowlist
- production database backups
- monitoring/observability

The current repository is a strong development foundation, but a production deployment still requires operational hardening.

---

## 🧠 29. Development philosophy

The backend intentionally separates:

```text
Deterministic evidence
        +
Threat intelligence
        +
AI reasoning
        =
Conservative security assessment
```

> 🧠 AI is not treated as an unquestionable source of truth.

Likewise, a single reputation provider does not automatically define the final verdict without considering the rest of the evidence.

This design is important for explainability, debugging and SOC workflows.

---

## ⚡ 30. Quick-start summary

If all prerequisites are already installed, the shortest setup is:

### 🟦 Terminal 1 — infrastructure

Make sure PostgreSQL and Redis are running.

### 🟨 Terminal 2 — backend

```powershell
cd Backend
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install pytest-asyncio
copy .env.example .env
# edit .env
alembic upgrade head
python -m pytest
python -m uvicorn app.main:app --reload --port 8000
```

### 🟩 Terminal 3 — frontend

```powershell
cd Frontend
pnpm install
copy .env.example .env.local
pnpm dev
```

Then open:

```text
http://localhost:3000
```

Backend docs:

```text
http://localhost:8000/docs
```

Backend readiness:

```text
http://localhost:8000/api/v1/health/ready
```

---

## ✅ 31. Current validation status

During development and local integration testing, the backend unit suite reached:

```text
10 passed
```

The following infrastructure layers were also verified in the development environment:

```text
PostgreSQL connectivity     ✅
PostgreSQL migrations       ✅
Redis connectivity          ✅
FastAPI startup             ✅
Backend unit tests          ✅
Next.js development server  ✅
Frontend ↔ backend client    ✅
```

A browser-extension-induced hydration warning was also reproduced in a normal browser session and disappeared in a private window with extensions disabled, indicating extension interference rather than an application hydration defect.

---

## 🙌 32. Credits / project notes

Mail Sentinel 2.0 was developed as an AI-assisted email security and SOC platform with a strong emphasis on explainable analysis, evidence preservation, threat-intelligence enrichment and investigation-aware AI assistance.

For future contributors, read this README first, then inspect:

```text
Backend/app/security/
Backend/app/services/
Backend/app/threat_intel/
Backend/app/ai/
Frontend/lib/api.ts
Frontend/components/ai-chat-drawer.tsx
```

> ✅ When changing security-sensitive code, run the full backend test suite before committing.
