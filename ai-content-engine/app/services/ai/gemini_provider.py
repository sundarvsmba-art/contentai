import time
import json
import logging
from typing import Optional
import requests
from .base_provider import BaseAIProvider
from ...core.config import settings

logger = logging.getLogger(__name__)

GEMINI_ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-1.5-flash:generateContent"
)


class GeminiProvider(BaseAIProvider):
    def __init__(
        self,
        api_key: Optional[str] = None,
        retries: int = 3,
        backoff: float = 1.0,
        timeout: int = 30,
    ):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.retries = retries
        self.backoff = backoff
        self.timeout = timeout

    def _call(self, prompt: str) -> Optional[str]:
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not set")
            return None

        url = f"{GEMINI_ENDPOINT}?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.85, "maxOutputTokens": 1024},
        }

        for attempt in range(1, self.retries + 1):
            try:
                logger.info("Gemini attempt %s", attempt)
                resp = requests.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=self.timeout,
                )
                resp.raise_for_status()
                data = resp.json()
                candidates = data.get("candidates") or []
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts") or []
                    if parts:
                        text = parts[0].get("text", "").strip()
                        if text:
                            return text
                logger.warning("Empty Gemini response on attempt %s", attempt)
                raise RuntimeError("empty response")
            except Exception as exc:
                logger.warning("Gemini attempt %s failed: %s", attempt, exc)
                if attempt < self.retries:
                    time.sleep(self.backoff * (2 ** (attempt - 1)))
        return None

    def generate_content(self, topic: str) -> str:
        if not topic or len(topic) > 200:
            raise ValueError("Invalid topic length")
        prompt = (
            f"Write a 20-40 second emotional story about '{topic}'. "
            "Start with a single punchy hook line, then the story, then a clear one-line lesson. "
            "Keep it suitable for social media reels."
        )
        return self._call(prompt) or "Failed to generate content. Try again."

    def generate_viral_content(self, topic: str, category: str) -> dict:
        if not topic or len(topic) > 200:
            raise ValueError("Invalid topic length")

        prompt = f"""Generate viral short-form reel content for this topic: "{topic}" (category: {category}).

Return ONLY a valid JSON object — no markdown, no explanation:
{{
  "hook": "one punchy opening sentence, max 15 words",
  "reel_title": "catchy reel/shorts title, max 10 words",
  "script": "30-second voice-over script, 60-80 words, emotional and engaging",
  "caption": "social media caption with emotion, max 150 chars",
  "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5", "#tag6"],
  "viral_score": <integer 1-100 based on emotional impact and trending potential>
}}"""

        raw = self._call(prompt)
        if not raw:
            return self._fallback_viral_content(topic, category)

        try:
            clean = raw.strip()
            # Strip markdown code fences if Gemini wraps output
            if clean.startswith("```"):
                lines = clean.splitlines()
                inner = [l for l in lines if not l.startswith("```")]
                clean = "\n".join(inner)
            return json.loads(clean)
        except (json.JSONDecodeError, ValueError):
            logger.warning("Gemini returned non-JSON for viral content, using raw as script")
            return self._fallback_viral_content(topic, category, script=raw)

    def _fallback_viral_content(self, topic: str, category: str, script: str = "") -> dict:
        return {
            "hook": f"You won't believe what happened with {topic[:60]}",
            "reel_title": topic[:50],
            "script": script or f"This is an important story about {topic}. Watch till the end.",
            "caption": f"Incredible story about {topic[:80]}. Follow for more!",
            "hashtags": ["#viral", "#trending", "#reels", "#shorts", f"#{category}", "#fyp"],
            "viral_score": 50,
        }
