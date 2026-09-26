import json
from typing import Any

from app.ai.gemini_client import gemini_client


class QuizService:

    async def generate(
        self,
        topic: str,
        content: str,
        language: str = "en",
        number_of_questions: int = 5,
        difficulty: str = "medium",
    ) -> dict[str, Any]:

        prompt = f"""
Generate {number_of_questions} multiple-choice
questions about {topic}.

Language: {language}
Difficulty: {difficulty}

Content:
{content}

Return valid JSON with:
question
options
correct_answer
explanation
"""

        result = await gemini_client.generate(
            prompt
        )

        try:
            questions = json.loads(result)
        except (json.JSONDecodeError, TypeError):
            questions = []

        return {
            "topic": topic,
            "language": language,
            "difficulty": difficulty,
            "questions": questions,
        }

    def evaluate(
        self,
        questions: list[dict[str, Any]],
        answers: dict[str, str],
    ) -> dict[str, Any]:

        correct = 0
        incorrect = 0
        knowledge_gaps = []

        for question in questions:
            question_id = str(
                question.get("id")
            )

            expected = question.get(
                "correct_answer"
            )

            actual = answers.get(
                question_id
            )

            if actual == expected:
                correct += 1
            else:
                incorrect += 1

                topic = question.get(
                    "topic"
                )

                if topic:
                    knowledge_gaps.append(
                        topic
                    )

        total = len(questions)

        percentage = (
            (correct / total) * 100
            if total
            else 0
        )

        return {
            "correct": correct,
            "incorrect": incorrect,
            "total": total,
            "percentage": round(
                percentage,
                2,
            ),
            "knowledge_gaps": list(
                set(knowledge_gaps)
            ),
        }


quiz_service = QuizService()