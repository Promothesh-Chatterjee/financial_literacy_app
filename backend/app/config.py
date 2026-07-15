from pydantic import BaseSettings


class Settings(BaseSettings):
    database_url: str
    redis_url: str
    yahoo_api_key: str | None = None
    newsapi_key: str | None = None
    claude_api_key: str | None = None
    secret_key: str
    access_token_expire_minutes: int = 60
    allow_dev_init: bool = False
    market_worker_secret: str | None = None

    class Config:
        env_file = "../.env"


settings = Settings()
