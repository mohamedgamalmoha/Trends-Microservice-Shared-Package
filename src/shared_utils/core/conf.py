import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: Optional[str] = os.environ.get('SQLALCHEMY_DATABASE_URL')
    USER_AUTH_URL: Optional[str] = os.environ.get('USER_AUTH_URL')
    USER_INFO_URL: Optional[str] = os.environ.get('USER_INFO_URL')


settings = Settings()
