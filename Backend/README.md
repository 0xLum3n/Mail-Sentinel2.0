# Mail Sentinel 2.0 Backend

FastAPI backend for Mail Sentinel 2.0: AI-powered email threat detection, phishing analysis, forensic investigation, threat intelligence, reporting, and SOC assistance.

## Planned stack

- FastAPI
- PostgreSQL
- SQLAlchemy 2.x
- Alembic
- Redis
- Pydantic Settings
- AI provider abstraction

## Development

Create a virtual environment, install the dependencies from `requirements.txt`, copy `.env.example` to `.env`, configure PostgreSQL/Redis, and then start the FastAPI application.

Implementation is being built incrementally and validated layer-by-layer.

## Current API foundation

Base API prefix: `/api/v1`

Authentication endpoints:

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me` (Bearer access token required)

Authentication uses short-lived JWT access tokens and persisted, rotated opaque refresh tokens. Refresh tokens are stored only as SHA-256 hashes in PostgreSQL.


## AI-assisted analysis

Set `AI_PROVIDER=openai` (or `openai-compatible`), `AI_MODEL`, `AI_API_KEY`, and optionally `AI_BASE_URL`. The analysis endpoint sends structured email evidence, deterministic findings, IOC reputation evidence, and attachment metadata to the configured model. The model response is validated against a strict Pydantic schema. AI failures fail closed and do not discard deterministic or threat-intelligence results.

AI risk is combined conservatively: the final risk score cannot be lower than the deterministic + threat-intelligence evidence score. AI findings are persisted separately with `source=ai`, and the full AI reasoning/recommended actions are retained in analysis metadata.

## AI SOC Analyst chat

The authenticated SOC Analyst API is scoped to the current organization and can bind a conversation to one email investigation:

- `GET /api/v1/ai/context/{email_id}`
- `POST /api/v1/ai/chat`

The chat service builds a model-safe investigation context from the stored email, latest analysis, findings, indicators, threat-intelligence enrichment, MITRE mappings, headers, and attachment metadata. Client messages can contain only `user` or `assistant` roles; system instructions are server-controlled. The backend limits history and evidence size before sending it to the AI provider. AI provider failures return `503` from the API without exposing provider error details.

Example request:

```json
{
  "email_id": "00000000-0000-0000-0000-000000000000",
  "message": "Why is this investigation high risk, and what should I do next?",
  "history": []
}
```
