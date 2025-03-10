
from functools import lru_cache


from pydantic_settings import BaseSettings, SettingsConfigDict


class CognitoConfig(BaseSettings):
    COGNITO_REGION: str = "us-east-1"
    COGNITO_USER_POOL_ID: str
    COGNITO_CLIENT_ID: str
    COGNITO_CLIENT_SECRET: str
    COGNITO_DOMAIN: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str

    model_config = SettingsConfigDict(
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
