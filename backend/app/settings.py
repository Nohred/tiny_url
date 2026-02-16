from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    BASE_URL: str = "http://127.0.0.1:8090"
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB: str = "tiny_url"
    MONGO_COLLECTION: str = "urls"

    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_TTL_SECONDS: int = 86400

    CODE_LEN: int = 7

settings = Settings()
