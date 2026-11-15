from functools import lru_cache
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    database_url: str = 'sqlite:///./barakah.db'
    secret_key: str = 'development-only-change-this-secret-before-deployment'
    environment: str = 'development'
    allowed_origins: str = 'http://localhost:5173,http://127.0.0.1:5173'
    cookie_secure: bool = False
    frontend_dist: str | None = None
    ai_mode: Literal['unavailable'] = 'unavailable'
    reset_outbox: str | None = None
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_sender: str = 'noreply@example.com'
    reset_url: str = 'http://localhost:5173/reset-password'
    auth_rate_limit: int = 20
    advisor_rate_limit: int = 30

    @property
    def origins(self):
        return [s.strip() for s in self.allowed_origins.split(',') if s.strip()]

    @model_validator(mode='after')
    def secure_config(self):
        if self.environment not in {'development', 'test', 'production'}:
            raise ValueError('Invalid environment')
        if self.environment == 'production':
            if not self.cookie_secure or len(self.secret_key) < 32 or self.secret_key.startswith('development-'):
                raise ValueError('Production requires secure cookies and a strong secret key')
            if self.smtp_host and not self.reset_url.startswith('https://'):
                raise ValueError('Production reset URL requires HTTPS')
            if self.reset_outbox:
                raise ValueError('Local reset outbox is development-only')
            if not self.origins or any(not origin.startswith('https://') for origin in self.origins):
                raise ValueError('Production requires explicit HTTPS origins')
        if '*' in self.origins:
            raise ValueError('Wildcard origins are forbidden')
        return self


@lru_cache
def get_settings():
    return Settings()
