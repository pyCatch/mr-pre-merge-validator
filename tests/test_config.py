from mr_validator.config import Settings


def test_settings_have_defaults() -> None:
    settings = Settings()

    assert settings.gitlab_base_url == "https://gitlab.com"
    assert settings.jira_base_url == "http://localhost:8080"
    