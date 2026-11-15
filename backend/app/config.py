from functools import lru_cache
from pydantic import Field, SecretStr, field_validator, model_validator
from urllib.parse import urlsplit
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
    ai_mode: Literal['unavailable', 'http'] = 'unavailable'
    ai_url: str | None = None
    ai_token: SecretStr | None = None
    ai_timeout_seconds: float = Field(default=90, ge=1, le=300, allow_inf_nan=False)
    user_ai_enabled: bool = False
    ai_credential_key: SecretStr | None = None
    ai_allowed_base_urls: str = ''
    external_ai_timeout_seconds: float = Field(default=35, ge=1, le=40, allow_inf_nan=False)
    ai_requests_per_minute: int = Field(default=6, ge=1, le=60)
    ai_requests_per_day: int = Field(default=30, ge=1, le=1000)
    ai_global_inflight_limit: int = Field(default=8, ge=1, le=100)
    reset_outbox: str | None = None
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_sender: str = 'noreply@example.com'
    reset_url: str = 'http://localhost:5173/reset-password'
    auth_rate_limit: int = 20
    advisor_rate_limit: int = 30

    @field_validator('database_url', mode='before')
    @classmethod
    def postgres_driver(cls, value):
        # Hosted providers export standard URLs; this project installs psycopg 3.
        for prefix in ('postgres://', 'postgresql://'):
            if isinstance(value, str) and value.startswith(prefix):
                return 'postgresql+psycopg://' + value[len(prefix):]
        return value

    @property
    def origins(self):
        return [s.strip() for s in self.allowed_origins.split(',') if s.strip()]

    @model_validator(mode='after')
    def secure_config(self):
        if self.ai_mode == 'http':
            url = urlsplit(self.ai_url or '')
            if (url.scheme != 'http' or url.hostname not in {'127.0.0.1', '::1'}
                    or url.username or url.password or url.query or url.fragment
                    or url.path != '/generate' or not url.port):
                raise ValueError('AI_URL must be an explicit loopback HTTP /generate endpoint (use an SSH tunnel)')
            token = self.ai_token.get_secret_value() if self.ai_token else ''
            if len(token) < 32 or not token.isascii() or any(char.isspace() for char in token):
                raise ValueError('HTTP AI requires a random URL-safe AI_TOKEN of at least 32 characters')
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
