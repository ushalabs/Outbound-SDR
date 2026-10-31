import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.config import Settings, get_settings
from app.logging_config import redact
from app.main import app


def test_health():
    with TestClient(app, base_url="http://127.0.0.1") as client:
        response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["email_sending_enabled"] is False


def test_secrets_redacted():
    settings = get_settings()
    for secret in (settings.database_url, settings.direct_database_url, settings.gemini_api_key):
        assert secret.get_secret_value() not in redact("failure " + secret.get_secret_value())
        assert secret.get_secret_value() not in repr(settings)


def test_sending_cannot_be_enabled():
    with pytest.raises(ValidationError):
        Settings(enable_real_email_sending=True)


def test_existing_environment_aliases():
    settings = Settings()
    assert settings.app_env
    assert settings.gemini_model
