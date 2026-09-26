from typing import Any

from app.ai.gemini_client import gemini_client


class TopicClassifier:

    async def classify(
        self,
        text: str,
        language: str = "en",
    ) -> dict[str, Any]:

        prompt = f"""
You are an educational topic analysis engine.

Analyze the learner's query and identify the learning structure
needed to understand the requested subject.

The subject can belong to ANY educational domain, including:

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

Do not restrict the answer to a predefined topic list.

Learner query:
{text}

Learner language:
{language}

Determine:

1. The main educational topic.
2. The academic or professional domain.
3. Important subtopics.
4. Prerequisites needed to understand the topic.
5. Related topics.
6. Estimated difficulty.
7. Multiple useful YouTube search queries.

Difficulty must be one of:

beginner
intermediate
advanced

Search queries should be suitable for finding educational
YouTube videos.

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
                    "type": "string"
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

        return {
            "topic": result.get(
                "topic",
                text.strip(),
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
            "difficulty": result.get(
                "difficulty",
                "intermediate",
            ),
            "search_queries": result.get(
                "search_queries",
                [text],
            ),
        }


topic_classifier = TopicClassifier()