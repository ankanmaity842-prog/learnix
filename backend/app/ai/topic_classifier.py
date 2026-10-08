from typing import Any

from app.ai.gemini_client import gemini_client


class TopicClassifier:
    async def classify(
        self,
        text: str,
        language: str = "en",
        level: str | None = None,
    ) -> dict[str, Any]:
        prompt = f"""
You are an educational topic analysis engine.

Analyze the learner's query and identify the learning structure
needed to understand the requested subject.

The subject can belong to ANY educational domain. Do not restrict
the answer to a predefined topic list.

Learner query:
{text}

Learner language:
{language}

Selected learner level:
{level or "Determine the most suitable level"}

Difficulty must be one of beginner, intermediate, advanced.

When a selected learner level is supplied, generate search queries
appropriate to that level:
- beginner: fundamentals, basics, and explanations from scratch
- intermediate: practical examples, applied concepts, and exercises
- advanced: deeper theory, advanced concepts, and complex applications

Language preferences:
- en: prefer English educational content
- hi: prefer Hindi educational content suitable for Indian learners;
  include Hindi terms where useful
- bn: prefer Bengali educational content; include Bengali script
  and phrases such as বাংলা ভাষায় where useful

Determine:
1. The main educational topic.
2. The academic or professional domain.
3. Important subtopics.
4. Prerequisites.
5. Related topics.
6. Estimated difficulty.
7. Up to three useful YouTube search queries.

Return only structured JSON.
"""

        schema = {
            "type": "object",
            "properties": {
                "topic": {"type": "string"},
                "domain": {"type": "string"},
                "subtopics": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "prerequisites": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "related_topics": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "difficulty": {
                    "type": "string",
                    "enum": ["beginner", "intermediate", "advanced"],
                },
                "search_queries": {
                    "type": "array",
                    "items": {"type": "string"},
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

        result = await gemini_client.generate_json(prompt, schema)

        allowed_levels = {"beginner", "intermediate", "advanced"}
        detected_level = result.get("difficulty", "intermediate")
        if detected_level not in allowed_levels:
            detected_level = "intermediate"

        queries = result.get("search_queries", [])
        if not isinstance(queries, list):
            queries = []
        queries = [str(item).strip() for item in queries if str(item).strip()]

        return {
            "topic": result.get("topic") or text.strip(),
            "domain": result.get("domain") or "General",
            "subtopics": result.get("subtopics") or [],
            "prerequisites": result.get("prerequisites") or [],
            "related_topics": result.get("related_topics") or [],
            "difficulty": level or detected_level,
            "search_queries": queries[:3] or [text.strip()],
        }


topic_classifier = TopicClassifier()