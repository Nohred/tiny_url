from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, AnyHttpUrl

from .settings import settings
from .short_func import generate_code
from .mongo_db import init_mongo, get_collection
from .redis_cache import init_redis, get_redis

app = FastAPI(title="Tiny URL")

origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ShortenIn(BaseModel):
    long_url: AnyHttpUrl

class ShortenOut(BaseModel):
    code: str | None = None
    short_url: str
    long_url: str
    reduced: bool
    message: str

@app.on_event("startup")
async def startup():
    await init_mongo()
    await init_redis()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/api/shorten", response_model=ShortenOut)
async def shorten(payload: ShortenIn):
    long_url = str(payload.long_url)

    # Rule: only shorten if it will be shorter than the final short URL
    short_len = len(settings.BASE_URL) + 1 + settings.CODE_LEN
    if len(long_url) <= short_len:
        return ShortenOut(
            code=None,
            short_url=long_url,
            long_url=long_url,
            reduced=False,
            message="URL can’t be reduced more (already short).",
        )

    col = get_collection()

    # Rule: exact dedupe by long_url
    existing = await col.find_one({"long_url": long_url})
    if existing:
        code = existing["code"]
        # Optional: warm cache on dedupe (recommended)
        r = get_redis()
        await r.setex(f"code:{code}", settings.REDIS_TTL_SECONDS, long_url)
        return ShortenOut(
            code=code,
            short_url=f"{settings.BASE_URL}/{code}",
            long_url=long_url,
            reduced=True,
            message="URL already existed; returning existing short URL.",
        )

    r = get_redis()

    # Create new
    for _ in range(10):
        code = generate_code(settings.CODE_LEN)
        try:
            await col.insert_one({"code": code, "long_url": long_url})
            await r.setex(f"code:{code}", settings.REDIS_TTL_SECONDS, long_url)
            return ShortenOut(
                code=code,
                short_url=f"{settings.BASE_URL}/{code}",
                long_url=long_url,
                reduced=True,
                message="Created new short URL.",
            )
        except Exception:
            # If code collides, retry (unique index on code prevents duplicates)
            continue

    raise HTTPException(status_code=500, detail="Could not generate unique code")

@app.get("/{code}")
async def go(code: str):
    r = get_redis()
    cached = await r.get(f"code:{code}")
    if cached:
        return RedirectResponse(url=cached, status_code=302)

    col = get_collection()
    doc = await col.find_one({"code": code})
    if not doc:
        raise HTTPException(status_code=404, detail="Short code not found")

    long_url = doc["long_url"]
    await r.setex(f"code:{code}", settings.REDIS_TTL_SECONDS, long_url)
    return RedirectResponse(url=long_url, status_code=302)
