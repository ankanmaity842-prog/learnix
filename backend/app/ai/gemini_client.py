from typing import Any

from google import genai
from google.genai import types

from app.config import settings


class GeminiClient:

    def __init__(self):
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )
        self.model = "gemini-2.5-flash-lite"

    async def generate(
        self,
        prompt: str,
    ) -> str:

        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        return response.text or ""

    async def generate_json(
        self,
        prompt: str,
        schema: dict[str, Any],
    ) -> dict[str, Any]:

        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema,
            ),
        )

        if not response.text:
            return {}

        import json

        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            return {}


gemini_client = GeminiClient()