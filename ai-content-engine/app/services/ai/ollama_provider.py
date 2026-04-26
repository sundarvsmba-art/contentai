import json
import logging
import time
from typing import Optional

import requests

from .base_provider import BaseAIProvider

logger = logging.getLogger(__name__)

_AVAILABILITY_CACHE_TTL = 30  # seconds


class OllamaProvider(BaseAIProvider):
    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 60,
    ):
        from ...core.config import settings
        self.base_url = (base_url or settings.OLLAMA_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL
        self.timeout = timeout
        self._available: Optional[bool] = None
        self._cache_until: float = 0

    # ------------------------------------------------------------------
    # Availability
    # ------------------------------------------------------------------

    def is_available(self) -> bool:
        now = time.time()
        if now < self._cache_until and self._available is not None:
            return self._available
        try:
            resp = requests.get(f"{self.base_url}/", timeout=5)
            available = resp.status_code == 200
        except Exception:
            available = False
        self._available = available
        self._cache_until = now + _AVAILABILITY_CACHE_TTL
        return available

    def invalidate_cache(self) -> None:
        self._cache_until = 0

    # ------------------------------------------------------------------
    # Raw generation
    # ------------------------------------------------------------------

    def _generate(self, prompt: str) -> Optional[str]:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.85, "num_predict": 1024},
        }
        try:
            resp = requests.post(url, json=payload, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            text = (data.get("response") or "").strip()
            if text:
                return text
            logger.warning("Ollama returned empty response for model=%s", self.model)
            return None
        except Exception as exc:
            self.invalidate_cache()
            logger.warning("Ollama _generate failed: %s", exc)
            return None

    # ------------------------------------------------------------------
    # BaseAIProvider interface
    # ------------------------------------------------------------------

    def generate_content(self, topic: str) -> str:
        if not topic or len(topic) > 200:
            raise ValueError("Invalid topic length")
        prompt = (
            f"Write a 20-40 second emotional story about '{topic}'. "
            "Start with a single punchy hook line, then the story, then a clear one-line lesson. "
            "Keep it suitable for social media reels. Be concise and engaging."
        )
        result = self._generate(prompt)
        return result or "Failed to generate content. Try again."

    def generate_viral_content(self, topic: str, category: str) -> dict:
        if not topic or len(topic) > 200:
            raise ValueError("Invalid topic length")

        prompt = (
            f'Generate viral short-form reel content for topic: "{topic}" (category: {category}).\n\n'
            "Return ONLY a valid JSON object — no markdown, no explanation, no code fences:\n"
            '{\n'
            '  "hook": "one punchy opening line, max 15 words",\n'
            '  "reel_title": "catchy title, max 10 words",\n'
            '  "script": "30-second script, 60-80 words, emotional and engaging",\n'
            '  "caption": "social media caption with emotion, max 150 chars",\n'
            '  "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"],\n'
            '  "viral_score": 75\n'
            "}\n\n"
            "Do not include any text before or after the JSON."
        )

        raw = self._generate(prompt)
        if not raw:
            return self._fallback(topic, category)

        try:
            clean = raw.strip()
            if clean.startswith("```"):
                lines = clean.splitlines()
                clean = "\n".join(l for l in lines if not l.startswith("```"))
            # Find the JSON object in the response
            start = clean.find("{")
            end = clean.rfind("}") + 1
            if start != -1 and end > start:
                clean = clean[start:end]
            return json.loads(clean)
        except (json.JSONDecodeError, ValueError):
            logger.warning("Ollama returned non-JSON for viral content, using fallback")
            return self._fallback(topic, category, script=raw[:500] if raw else "")

    def _fallback(self, topic: str, category: str, script: str = "") -> dict:
        return {
            "hook": f"You won't believe what happened with {topic[:60]}",
            "reel_title": topic[:50],
            "script": script or f"This is an important story about {topic}. Watch till the end.",
            "caption": f"Incredible story about {topic[:80]}. Follow for more!",
            "hashtags": ["#viral", "#trending", "#reels", "#shorts", f"#{category}", "#fyp"],
            "viral_score": 50,
        }
