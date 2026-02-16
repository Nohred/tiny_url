# Tiny URL (FastAPI + MongoDB + Redis)

A minimal URL shortener API built with FastAPI. It stores short-code mappings in MongoDB, caches lookups in Redis, and redirects short links to their original URLs.

## Features

- Create short URLs via `POST /api/shorten`.
- Redirect with `GET /{code}` using a `302` redirect.
- Exact deduplication: if the same long URL was already shortened, the existing short code is returned.
- Redis caching with TTL to speed up redirects.
- CORS configured via an environment setting to support a separate frontend.

## Architecture

- **FastAPI** provides the HTTP API and validation via Pydantic models.
- **MongoDB** stores `{ code, long_url }` documents (typically with a unique index on `code`).
- **Redis** caches `code -> long_url` entries using TTL (e.g., `SETEX`).

## API

### Health check

`GET /health`

**Response**
```json
{ "status": "ok" }
```

### Shorten a URL

`POST /api/shorten`

FastAPI validates the JSON body against the input model (your `long_url` is typed as a URL), and will return `422` if validation fails. [fastapi.tiangolo](https://fastapi.tiangolo.com/tutorial/body/)

**Request**
```json
{
  "long_url": "https://example.com/some/very/long/url"
}
```

**Response (created)**
```json
{
  "code": "a1B2c3D",
  "short_url": "http://localhost:8090/a1B2c3D",
  "long_url": "https://example.com/some/very/long/url",
  "reduced": true,
  "message": "Created new short URL."
}
```

**Response (already existed / dedupe)**
```json
{
  "code": "a1B2c3D",
  "short_url": "http://localhost:8090/a1B2c3D",
  "long_url": "https://example.com/some/very/long/url",
  "reduced": true,
  "message": "URL already existed; returning existing short URL."
}
```

**Response (not worth shortening)**
If the long URL is already shorter than (or equal to) the final short URL length, the API returns the original URL with `reduced=false`.

```json
{
  "code": null,
  "short_url": "https://x.co",
  "long_url": "https://x.co",
  "reduced": false,
  "message": "URL can’t be reduced more (already short)."
}
```

### Redirect

`GET /{code}`

- Checks Redis first.
- If not cached, queries MongoDB.
- If found, returns a `302` redirect to the long URL.
- If not found, returns `404`.

## Configuration

This app uses a settings class (Pydantic Settings) to load configuration from environment variables and/or a `.env` file, which is a standard FastAPI pattern for settings management. [fastapi.tiangolo](https://fastapi.tiangolo.com/advanced/settings/)

Common environment variables (names may differ in your project—adjust to your `settings.py`):

- `BASE_URL`  
  Public base URL used to build the returned `short_url` (e.g., `http://localhost:8090`).

- `CODE_LEN`  
  Length of generated codes (e.g., `7`).

- `CORS_ORIGINS`  
  Comma-separated list of allowed browser origins, e.g.  
  `http://localhost:5173,http://127.0.0.1:5173`

- `MONGO_URI` / `MONGO_DB_NAME` / `MONGO_COLLECTION`  
  Mongo connection string and database/collection names.

- `REDIS_URL`  
  Redis connection string (e.g., `redis://localhost:6379/0`).

- `REDIS_TTL_SECONDS`  
  TTL used for cached redirect lookups.

## Running locally (without Docker)

### 1) Install dependencies
Create and activate a virtual environment, then install requirements:

```bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows

pip install -r requirements.txt
```

### 2) Start MongoDB and Redis
You can run them via your local installation or Docker.

### 3) Run the API
From the backend folder (adjust module path to your project layout):

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8090 --reload
```

Open:
- API docs: `http://127.0.0.1:8090/docs`
- Health: `http://127.0.0.1:8090/health`

## Running with Docker Compose

```bash
docker compose up --build
```

