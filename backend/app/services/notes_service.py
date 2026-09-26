from typing import Any

from app.ai.gemini_client import gemini_client


class NotesService:

    async def generate(
        self,
        topic: str,
        content: str,
        language: str = "en",
        detail_level: str = "medium",
    ) -> dict[str, Any]:

        prompt = f"""
Create study notes for the topic: {topic}

Language: {language}
Detail level: {detail_level}

Content:
{content}

Return:
1. Short summary
2. Key points
3. Important definitions
4. Examples
5. Important formulas if applicable
"""

        result = await gemini_client.generate(
            prompt
        )

        return {
            "topic": topic,
            "language": language,
            "detail_level": detail_level,
            "content": result,
        }


notes_service = NotesService()