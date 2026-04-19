import os
import logging
from ..core.config import settings

logger = logging.getLogger(__name__)


def generate_script(topic: str) -> str:
    """Generate a short emotional medical story using Gemini API.

    The function reads the GEMINI_API_KEY from environment and calls the
    external API. To keep this example runnable without credentials,
    if the key is missing it returns a mocked script.
    """
    api_key = settings.GEMINI_API_KEY
    prompt = (
        f"Write a 20-40 second emotional medical story about '{topic}'. "
        "Include a short hook, the story, and an ending lesson. Keep it concise and human-readable."
    )

    if not api_key:
        logger.warning("GEMINI_API_KEY not set, returning mocked script.")
        return (
            f"Hook: A patient named Alex faced {topic}. "
            "Story: In the clinic, Alex discovered... (mocked) "
            "Ending lesson: Empathy and early care matter."
        )

    # Placeholder for real Gemini API call. The actual Gemini HTTP API
    # client usage should be implemented per Google's docs. Here we'll
    # simulate a request and safe error handling.
    try:
        # Example pseudo-call (replace with real client):
        # response = gemini_client.generate_text(api_key=api_key, prompt=prompt)
        # return response.text
        # For now, we return a placeholder to avoid external network calls in this template.
        return (
            f"Hook: A patient named Alex faced {topic}. "
            "Story: In the clinic, Alex discovered... "
            "Ending lesson: Empathy and early care matter."
        )
    except Exception as e:
        logger.exception("Error while calling Gemini API")
        raise
