"""Small live Gemini access check; never logs API keys or provider error bodies."""

import json
import sys

from google import genai
from google.genai import errors, types
from pydantic import BaseModel

from app.config import get_settings
from app.logging_config import redact


class AccessCheck(BaseModel):
    available: bool


def main():
    settings = get_settings()
    try:
        with genai.Client(
            api_key=settings.gemini_api_key.get_secret_value(),
            http_options=types.HttpOptions(
                timeout=30000, retry_options=types.HttpRetryOptions(attempts=3, initial_delay=2, max_delay=5)
            ),
        ) as client:
            model = client.models.get(model=settings.gemini_model)
            print(json.dumps({"configured_model": model.name, "model_access": "available"}))
            result = client.models.generate_content(
                model=settings.gemini_model,
                contents='Return {"available": true}. This is a minimal application connectivity check.',
                config=types.GenerateContentConfig(
                    response_mime_type="application/json", response_schema=AccessCheck
                ),
            )
            validated = AccessCheck.model_validate_json(result.text)
            if not validated.available:
                print("Gemini check failed: provider did not confirm availability")
                return 1
            print("Gemini structured generation: PASS")
            models = [
                model.name
                for model in client.models.list()
                if "embedContent" in (model.supported_actions or [])
            ]
            print(json.dumps({"available_embedding_models": models}))
    except errors.APIError as exc:
        action = (
            "Retry when the configured Gemini model's provider service is available"
            if exc.code in (500, 502, 503, 504)
            else "Usable GEMINI_API_KEY and GEMINI_MODEL with available quota"
        )
        print(
            json.dumps(
                {
                    "gemini_access": "failed",
                    "http_code": exc.code,
                    "status": exc.status,
                    "message": redact(exc.message or "Provider error"),
                    "required_action": action,
                }
            )
        )
        return 1
    except (OSError, ValueError, TimeoutError) as exc:
        print(
            json.dumps(
                {
                    "gemini_access": "failed",
                    "error_type": type(exc).__name__,
                    "required_configuration": "Reachable Gemini API and valid structured response",
                }
            )
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
