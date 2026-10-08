from typing import Any

from app.ai.gemini_client import gemini_client


class TopicClassifier:

    async def classify(
        self,
        text: str,
        language: str = "en",
        level: str = "beginner",
    ) -> dict[str, Any]:

        prompt = f"""
You are an educational topic analysis engine.

The learner wants videos ONLY about the exact topic they searched for.

Learner query:
{text}

Learner language:
{language}

Requested learning level:
{level}

IMPORTANT RULES:

1. Identify the EXACT main topic from the learner query.
2. Do NOT replace the topic with a broader related topic.
3. Do NOT recommend adjacent technologies or subjects.
4. If the query is "Python", the topic MUST remain "Python".
5. For "Python", do not treat C++, Java, JavaScript, C#, PHP,
   HTML, CSS, React, Django or other technologies as the same topic.
6. For "React", do not return Angular, Vue or unrelated JavaScript videos.
7. For "Machine Learning", do not return generic programming videos.
8. For "Physics", do not return Chemistry or Mathematics videos unless
   they are explicitly part of the searched topic.
9. Search queries must remain tightly focused on the exact topic.
10. The requested learning level must be reflected in the search query.

Difficulty:
- beginner
- intermediate
- advanced

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
                    }
                },
                "prerequisites": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "related_topics": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "difficulty": {
                    "type": "string",
                    "enum": [
                        "beginner",
                        "intermediate",
                        "advanced"
                    ]
                },
                "search_queries": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                }
            },
            "required": [
                "topic",
                "domain",
                "subtopics",
                "prerequisites",
                "related_topics",
                "difficulty",
                "search_queries"
            ]
        }

        result = await gemini_client.generate_json(
            prompt,
            schema,
        )

        resolved_topic = result.get(
            "topic",
            text.strip(),
        )

        # Prevent Gemini from changing the user's actual topic.
        if not resolved_topic.strip():
            resolved_topic = text.strip()

        return {
            "topic": resolved_topic,
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
                [],
            ),
        }


topic_classifier = TopicClassifier()