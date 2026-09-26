import json

from app.ai.gemini_client import gemini_client


class MultilingualQuiz:

    async def generate(
        self,
        topic: str,
        content: str,
        language: str = "en",
        question_count: int = 5,
        difficulty: str = "medium",
    ) -> list[dict]:

        language_names = {
            "en": "English",
            "bn": "Bengali",
            "hi": "Hindi",
        }

        language_name = language_names.get(
            language,
            "English",
        )

        prompt = f"""
Create {question_count} educational
multiple-choice questions.

Topic: {topic}
Language: {language_name}
Difficulty: {difficulty}

Content:
{content}

Return ONLY valid JSON.

Format:
[
  {{
    "id": "q1",
    "question": "...",
    "options": ["A", "B", "C", "D"],
    "correct_answer": "A",
    "explanation": "..."
  }}
]
"""

        result = await gemini_client.generate(
            prompt
        )

        try:
            data = json.loads(result)

            if isinstance(data, list):
                return data

        except (
            json.JSONDecodeError,
            TypeError,
        ):
            pass

        return []


multilingual_quiz = MultilingualQuiz()