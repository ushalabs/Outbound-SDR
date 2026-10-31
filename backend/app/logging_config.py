import json
import logging
import re

from app.config import get_settings


def redact(message: str) -> str:
    settings = get_settings()
    for secret in (settings.database_url, settings.direct_database_url, settings.gemini_api_key):
        value = secret.get_secret_value()
        if value:
            message = message.replace(value, "[REDACTED]")
    message = re.sub(r"postgres(?:ql)?(?:\+psycopg)?://\S+", "[REDACTED_DATABASE_URL]", message)
    return re.sub(r"AIza[\w-]+", "[REDACTED_KEY]", message)


class SafeFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps({"level": record.levelname, "logger": record.name,
                           "message": redact(record.getMessage())})


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(SafeFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)
