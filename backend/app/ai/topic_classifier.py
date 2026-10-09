from typing import Any

from app.ai.gemini_client import (
    gemini_client,
)


class TopicClassifier:

    async def classify(
        self,
        text: str,
        language: str = "en",
        level: str = "beginner",
    ) -> dict[str, Any]:

        prompt = f"""
You are an educational topic analysis engine.

The user wants educational YouTube content.

User query:
{text}

Learning language:
{language}

Requested learning level:
{level}

IMPORTANT RULES:

1. Identify the EXACT main topic requested.
2. Do NOT replace the topic with a related technology.
3. If the user searches "Python", the main topic must be Python.
4. Do not broaden Python into C++, JavaScript, Java,
   web development, or other programming languages.
5. Related topics may be returned separately but must NOT
   replace the main topic.
6. Search queries must preserve the exact main topic.
7. Search queries must be suitable for educational content.
8. Avoid entertainment, music, movies, gaming, comedy,
   reactions, vlogs, celebrity content and general entertainment.
9. The requested level must be respected.

Supported domains include:

- Computer Science
- Programming
- Mathematics
- Physics
- Chemistry
- Biology
- Medicine
- Engineering
- History
- Geography
- Economics
- Literature
- Languages
- Arts
- Business
- Law
- Science
- General education
- Any other educational field

Difficulty:
{level}

Return only structured JSON.
"""

        schema = {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string"
                },
                "domain": {
                    "type": "string"
                },
                "subtopics": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                },
                "prerequisites": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                },
                "related_topics": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                },
                "difficulty": {
                    "type": "string"
                },
                "search_queries": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                },
            },
            "required": [
                "topic",
                "domain",
                "subtopics",
                "prerequisites",
                "related_topics",
                "difficulty",
                "search_queries",
            ],
        }

        result = await gemini_client.generate_json(
            prompt,
            schema,
        )

        return {
            "topic": (
                result.get(
                    "topic"
                )
                or text.strip()
            ),
            "domain": result.get(
                "domain",
                "General",
            ),
            "subtopics": result.get(
                "subtopics",
                [],
            ),
            "prerequisites": result.get(
                "prerequisites",
                [],
            ),
            "related_topics": result.get(
                "related_topics",
                [],
            ),
            "difficulty": level,
            "search_queries": result.get(
                "search_queries",
                [
                    text.strip()
                ],
            ),
        }


topic_classifier = TopicClassifier()