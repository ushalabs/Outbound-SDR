import json
from typing import TypeVar

import httpx
from google import genai
from google.genai import errors, types
from pydantic import BaseModel, ValidationError

from app.config import get_settings
from app.logging_config import redact

T = TypeVar("T", bound=BaseModel)


def provider_schema(schema: type[BaseModel]) -> dict:
    # Keep the full local validator, but simplify decoder constraints to avoid state explosion.
    def simplify(value):
        if isinstance(value, dict):
            return {
                key: simplify(item)
                for key, item in value.items()
                if key not in {"minLength", "maxLength", "minItems", "maxItems", "title", "default"}
            }
        if isinstance(value, list):
            return [simplify(item) for item in value]
        return value

    return simplify(schema.model_json_schema())


class AIError(ValueError):
    pass


def client():
    settings = get_settings()
    return genai.Client(
        api_key=settings.gemini_api_key.get_secret_value(),
        http_options=types.HttpOptions(
            timeout=60000, retry_options=types.HttpRetryOptions(attempts=3, initial_delay=1, max_delay=5)
        ),
    )


def generate(schema: type[T], instruction: str, evidence: dict) -> T:
    settings = get_settings()
    try:
        with client() as provider:
            response = provider.models.generate_content(
                model=settings.gemini_model,
                contents=json.dumps(evidence, ensure_ascii=False),
                config=types.GenerateContentConfig(
                    system_instruction=instruction,
                    response_mime_type="application/json",
                    response_json_schema=provider_schema(schema),
                ),
            )
            if not response.text:
                raise AIError("Gemini returned no content; no successful result was saved")
            return schema.model_validate_json(response.text)
    except errors.APIError as exc:
        reason = redact(exc.message or "Provider rejected the request")[:1200]
        raise AIError(f"Gemini request failed (HTTP {exc.code}, {exc.status}): {reason}") from exc
    except ValidationError as exc:
        raise AIError(
            "Gemini response failed local structured-output validation; no successful result saved"
        ) from exc
    except (TimeoutError, OSError, httpx.HTTPError) as exc:
        raise AIError("Gemini could not be reached or timed out") from exc
