import os
from functools import lru_cache

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class CognitoConfig(BaseSettings):
    region: str = "us-east-1"
    user_pool_id: str
    client_id: str
    client_secret: str
    domain: str

    model_config = SettingsConfigDict(
        env_prefix="COGNITO_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_cognito_config() -> CognitoConfig:
    """
    Get Cognito configuration from environment variables or .env file
    """
    return CognitoConfig()