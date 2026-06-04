from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    gitlab_base_url: str = Field(
        default="https://gitlab.com",
        alias="GITLAB_BASE_URL",
    )

    jira_base_url: str = Field(
        default="http://localhost:8080",
        alias="JIRA_BASE_URL",
    )

    jira_token: str = Field(
        default="dummy-token",
        alias="JIRA_TOKEN",
    )

    request_timeout_seconds: float = Field(
        default=10.0,
        alias="REQUEST_TIMEOUT_SECONDS",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )