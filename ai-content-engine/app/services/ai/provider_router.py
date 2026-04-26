import logging
from typing import Optional

from .gemini_provider import GeminiProvider
from .ollama_provider import OllamaProvider

logger = logging.getLogger(__name__)


class AIProviderRouter:
    """Routes generation requests: Ollama first, Gemini as fallback."""

    def __init__(self):
        self._ollama = OllamaProvider()
        self._gemini = GeminiProvider()

    # ------------------------------------------------------------------
    # Public generation API
    # ------------------------------------------------------------------

    def generate_content(self, topic: str) -> str:
        if self._ollama.is_available():
            try:
                result = self._ollama.generate_content(topic)
                if result and "Failed to generate" not in result:
                    logger.info("generate_content served by ollama")
                    return result
            except Exception as exc:
                logger.warning("Ollama generate_content error, falling back: %s", exc)
        logger.info("generate_content served by gemini")
        return self._gemini.generate_content(topic)

    def generate_viral_content(self, topic: str, category: str) -> dict:
        if self._ollama.is_available():
            try:
                result = self._ollama.generate_viral_content(topic, category)
                if result and result.get("script"):
                    logger.info("generate_viral_content served by ollama")
                    return result
            except Exception as exc:
                logger.warning("Ollama generate_viral_content error, falling back: %s", exc)
        logger.info("generate_viral_content served by gemini")
        return self._gemini.generate_viral_content(topic, category)

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def provider_status(self) -> dict:
        ollama_ok = self._ollama.is_available()
        gemini_ok = bool(self._gemini.api_key)
        return {
            "ollama": "online" if ollama_ok else "offline",
            "gemini": "online" if gemini_ok else "offline",
            "active": "ollama" if ollama_ok else ("gemini" if gemini_ok else "none"),
        }

    @property
    def ollama(self) -> OllamaProvider:
        return self._ollama

    @property
    def gemini(self) -> GeminiProvider:
        return self._gemini


# Module-level singleton — shared across all requests
provider_router = AIProviderRouter()
