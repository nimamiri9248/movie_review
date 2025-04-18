from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    project_name: str = "Film Review Platform"
    db_url: str = "user:password@localhost:5432/film_review"
    secret_key: str = "supersecretkey"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 465
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    redis_url: str = "redis://localhost:6379/1"
    reset_code_expire_time: int = 600  # seconds
    admin_password: str = "helloAdmin"
    admin_email: str = "admin@gmail.com"


settings = Settings()