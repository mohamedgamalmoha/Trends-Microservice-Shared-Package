import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: Optional[str] = os.environ.get('SQLALCHEMY_DATABASE_URL', None)
    USER_AUTH_URL: Optional[str] = os.environ.get('USER_AUTH_URL', None)
    USER_INFO_URL: Optional[str] = os.environ.get('USER_INFO_URL', None)
    USER_REQUEST_TIMEOUT: Optional[int] = os.environ.get('USER_REQUEST_TIMEOUT', 10)


settings = Settings()
