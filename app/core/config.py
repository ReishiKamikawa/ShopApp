from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # MongoDB
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "shopapp"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # JWT
    secret_key: str = "your-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # App
    debug: bool = True

    class Config:
        env_file = ".env"


settings = Settings()

