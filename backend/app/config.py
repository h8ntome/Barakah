from functools import lru_cache
from pydantic import model_validator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import urlparse


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    database_url: str = 'sqlite:///./barakah.db'
    secret_key: str = 'development-only-change-this-secret-before-deployment'
    environment: str = 'development'
    allowed_origins: str = 'http://localhost:5173,http://127.0.0.1:5173'
    cookie_secure: bool = False
    ai_mode: str = 'mock'
    ai_request_timeout_seconds: float = Field(default=10, gt=0, le=120)
    ai_max_conversation_messages: int = Field(default=100, ge=2, le=1000)
    ai_model_name: str = 'lfm3-1.7b-pending'
    ai_local_url: str = 'http://127.0.0.1:8080/chat'
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
        if self.ai_mode not in {'mock', 'local'}:
            raise ValueError('Invalid AI mode')
        url = urlparse(self.ai_local_url)
        if url.scheme != 'http' or url.hostname not in {'127.0.0.1', '::1', 'localhost'} or url.username or url.password:
            raise ValueError('AI endpoint must be an administrator-configured loopback HTTP endpoint')
        return self


@lru_cache
def get_settings():
    return Settings()
