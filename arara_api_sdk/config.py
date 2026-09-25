from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_BASE_URL = "https://api.ararahq.com"
DEFAULT_TIMEOUT_SECONDS = 30.0
DEFAULT_MAX_RETRIES = 3


class SDKConfig(BaseSettings):
    """SDK configuration, read from arguments or ``ARARA_*`` env vars."""

    model_config = SettingsConfigDict(env_prefix="ARARA_", case_sensitive=False)

    api_key: str
    base_url: str = DEFAULT_BASE_URL
    timeout: float = DEFAULT_TIMEOUT_SECONDS
    max_retries: int = DEFAULT_MAX_RETRIES
