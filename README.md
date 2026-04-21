# META Urls Manager

HTTP Metadata Inventory Service — collects and stores headers, cookies, and page source for any given URL.

## Tech Stack

- **Python 3.12+** / **FastAPI** — async API framework
- **MongoDB** — document storage via Motor + Beanie ODM
- **Docker Compose** — containerized environment

## Quick Start

### Prerequisites

- Docker & Docker Compose

### Run

```bash
# Copy env file
cp .env.example .env

# Start services
docker-compose up --build
```

The API will be available at **http://localhost:8000**.

### API Documentation

- Swagger UI: http://localhost:8000/api/docs
- OpenAPI JSON: http://localhost:8000/api/openapi.json

## API Endpoints

### POST `/api/urls/`

Create a metadata record for a URL.

```bash
curl -X POST http://localhost:8000/api/urls/ \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

**Response (201):** Full metadata object with headers, cookies, and page source.

### GET `/api/urls/?url=https://example.com`

Retrieve metadata for a URL.

```bash
curl http://localhost:8000/api/urls/?url=https://example.com
```

- **200:** Record exists — returns full metadata.
- **202:** Record missing — collection queued in background.

### GET `/api/health/`

Health check endpoint.

## Testing

```bash
# Run tests inside the container
docker-compose exec backend pytest

# Run with verbose output
docker-compose exec backend pytest -v
```

## Project Structure

```
src/
├── main.py                  # FastAPI app + lifespan
├── core/
│   ├── config.py            # Settings (env vars)
│   ├── constants.py         # Enums
│   ├── database.py          # Beanie init
│   └── health.py            # Health check router
├── database/
│   ├── base_class.py        # TimeStampedDocument base
│   └── crud_base.py         # Generic CRUD operations
└── url_manager/
    ├── models.py            # UrlMetaData document
    ├── schema.py            # Pydantic request/response schemas
    ├── crud.py              # URL-specific CRUD
    ├── service.py           # Business logic (fetch + store)
    └── router.py            # API endpoints
tests/
├── conftest.py              # Fixtures + mock MongoDB
├── test_models.py           # Model + schema tests
├── test_service.py          # Service layer tests
└── test_router.py           # Integration tests
```
