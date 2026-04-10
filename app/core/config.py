from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # MongoDB
    mongodb_url: str = "mongodb://localhost:27018"
    database_name: str = "shopapp"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # JWT
    secret_key: str = "your-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # App
    debug: bool = True
    
    # Email/SMTP
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 465

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

