import json

import httpx

from app.categories import CATEGORY_VALUES, Category
from app.config import Settings


class ClassificationError(RuntimeError):
    pass


SYSTEM_PROMPT = f"""You classify consumer complaint narratives.
Choose exactly one category from this list:
{chr(10).join(f'- {category}' for category in CATEGORY_VALUES)}

Return JSON only, in this exact shape: {{"category": "one category exactly as written"}}.
Do not add commentary or markdown."""


class OllamaClassifier:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def classify(self, narrative: str) -> Category:
        payload = {
            "model": self.settings.ollama_model,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0},
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": narrative},
            ],
        }
        try:
            async with httpx.AsyncClient(
                base_url=self.settings.ollama_base_url,
                timeout=self.settings.ollama_timeout_seconds,
            ) as client:
                response = await client.post("/api/chat", json=payload)
                response.raise_for_status()
            content = response.json()["message"]["content"]
            category_text = json.loads(content)["category"]
            return Category(category_text)
        except (httpx.HTTPError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise ClassificationError(f"Ollama returned an invalid classification: {exc}") from exc

