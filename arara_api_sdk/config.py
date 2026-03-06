from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class SDKConfig(BaseSettings):
    """SDK Configuration settings."""
    api_key: str = Field(..., env="ARARA_API_KEY")
    base_url: str = Field("https://api.arara.io", env="ARARA_BASE_URL")
    timeout: float = Field(30.0, env="ARARA_TIMEOUT")
    max_retries: int = Field(3, env="ARARA_MAX_RETRIES")

    class Config:
        env_prefix = "ARARA_"
        case_sensitive = False
