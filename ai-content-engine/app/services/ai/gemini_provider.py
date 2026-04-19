import time
import logging
from typing import Optional
import requests
from ..ai.base_provider import BaseAIProvider
from ...core.config import settings

logger = logging.getLogger(__name__)


class GeminiProvider(BaseAIProvider):
    """Google Gemini REST provider implementing standard REST shapes.

    Endpoint: https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateText
    """

    ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateText"

    def __init__(self, api_key: Optional[str] = None, retries: int = 3, backoff: float = 1.0, timeout: int = 8):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.retries = retries
        self.backoff = backoff
        self.timeout = timeout

    def _build_prompt(self, topic: str) -> str:
        # Build a clear instruction; returns plain text for prompt.text
        return (
            f"Write a 20-40 second emotional medical story about '{topic}'. "
            "Use simple English. Output must start with a single-line hook, then the story, "
            "and end with a clear one-line lesson. Keep the total length suitable for social media."
        )

    def _parse_response(self, data: dict) -> Optional[str]:
        try:
            # 1) candidates[0].content.parts[0].text
            candidates = data.get("candidates")
            if isinstance(candidates, list) and candidates:
                first = candidates[0]
                content = first.get("content") or {}
                parts = content.get("parts")
                if isinstance(parts, list) and parts:
                    text = parts[0].get("text")
                    if text and isinstance(text, str):
                        return text.strip()

            # 2) candidates[0].output
            if isinstance(candidates, list) and candidates and isinstance(candidates[0].get("output"), str):
                return candidates[0].get("output").strip()

            # 3) top-level 'output' or 'text'
            if isinstance(data.get("output"), str):
                return data.get("output").strip()
            if isinstance(data.get("text"), str):
                return data.get("text").strip()

        except Exception:
            logger.exception("Error parsing Gemini response")
        return None

    def generate_content(self, topic: str) -> str:
        # Validate topic length (security)
        if not topic or len(topic) > 100:
            logger.warning("Invalid topic length: %s", len(topic))
            raise ValueError("Invalid topic")

        if not self.api_key:
            logger.warning("GEMINI_API_KEY not set; returning fallback")
            return "Failed to generate content. Try again."

        instruction = self._build_prompt(topic)
        payload = {
            "prompt": {"text": instruction},
            "max_output_tokens": 300,
            "temperature": 0.3,
        }

        attempt = 0
        while attempt < self.retries:
            attempt += 1
            try:
                logger.info("Gemini request attempt %s for topic=%s", attempt, topic)
                headers = {"Content-Type": "application/json", "X-goog-api-key": self.api_key}
                resp = requests.post(self.ENDPOINT, json=payload, headers=headers, timeout=self.timeout)
                resp.raise_for_status()
                data = resp.json()
                text = self._parse_response(data)
                if text:
                    logger.info("Gemini success for topic=%s", topic)
                    return text
                else:
                    logger.warning("Gemini returned empty/invalid response on attempt %s", attempt)
                    raise RuntimeError("Empty response")
            except (requests.RequestException, RuntimeError) as e:
                logger.exception("Gemini call failed on attempt %s: %s", attempt, str(e))
                if attempt >= self.retries:
                    logger.error("Gemini exhausted retries (%s)", self.retries)
                    return "Failed to generate content. Try again."
                sleep_for = self.backoff * (2 ** (attempt - 1))
                time.sleep(sleep_for)
import time
import logging
from typing import Optional
import requests
from ..ai.base_provider import BaseAIProvider
from ...core.config import settings

logger = logging.getLogger(__name__)


class GeminiProvider(BaseAIProvider):
    """Google Gemini REST provider.

    Uses the v1beta endpoint to generate content. Implements retries, timeouts,
    exponential backoff, defensive response parsing, and a clean fallback message.
    """

    ENDPOINT = (
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    )

    def __init__(self, api_key: Optional[str] = None, retries: int = 3, backoff: float = 1.0, timeout: int = 8):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.retries = retries
        self.backoff = backoff
        self.timeout = timeout

    def _build_prompt(self, topic: str) -> dict:
        # Structured instructions: short, emotional, hook + story + ending lesson
        instruction = (
            f"Write a 20-40 second emotional medical story about '{topic}'. "
            "Use simple English. Output must start with a single-line hook, then the story, "
            "and end with a clear one-line lesson. Keep the total length suitable for social media."
        )
        # The Gemini API expects structured input; use `prompt`-like field depending on API
        return {
            "instances": [
                {
                    "content": instruction,
                }
            ]
        }

    def _parse_response(self, data: dict) -> Optional[str]:
        # Expected path per requirement
        try:
            candidates = data.get("candidates")
            if isinstance(candidates, list) and candidates:
                first = candidates[0]
                content = first.get("content") or {}
                parts = content.get("parts")
                if isinstance(parts, list) and parts:
                    text = parts[0].get("text")
                    if text and isinstance(text, str):
                        return text.strip()
        except Exception:
            logger.exception("Failed to parse Gemini response")
        return None

    def generate_content(self, topic: str) -> str:
        # Input validation (security)
        if not topic or len(topic) > 100:
            logger.warning("Invalid topic length: %s", len(topic))
            raise ValueError("Invalid topic")

        if not self.api_key:
            logger.warning("GEMINI_API_KEY not set; returning fallback message")
            return "Failed to generate content. Try again."

        payload = self._build_prompt(topic)

        attempt = 0
        while attempt < self.retries:
            attempt += 1
            try:
                logger.info("Gemini request attempt %s for topic '%s'", attempt, topic)
                headers = {"Content-Type": "application/json", "X-goog-api-key": self.api_key}
                resp = requests.post(self.ENDPOINT, json=payload, headers=headers, timeout=self.timeout)
                resp.raise_for_status()
                data = resp.json()
                text = self._parse_response(data)
                if text:
                    logger.info("Gemini success for topic '%s'", topic)
                    return text
                else:
                    logger.warning("Gemini returned empty or unexpected response; attempt %s", attempt)
                    raise RuntimeError("Empty response")
            except (requests.RequestException, RuntimeError) as e:
                logger.exception("Gemini call failed on attempt %s: %s", attempt, str(e))
                if attempt >= self.retries:
                    logger.error("Gemini failed after %s attempts", self.retries)
                    return "Failed to generate content. Try again."
                sleep_for = self.backoff * (2 ** (attempt - 1))
                time.sleep(sleep_for)

