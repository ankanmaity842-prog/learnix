
import json
import re
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

        content = content.strip()

        if len(content) < 50:
            raise ValueError(
                "The transcript or lesson notes are too short "
                "to generate a reliable quiz."
            )

        prompt = f"""
You are Learnix, an educational assessment generator.

Create exactly {number_of_questions} multiple-choice questions.

VIDEO TOPIC:
{topic}

LANGUAGE:
{language}

DIFFICULTY:
{difficulty}

SOURCE TRANSCRIPT OR LESSON NOTES:
<lesson_content>
{content[:30000]}
</lesson_content>

STRICT RULES:
1. Every question must test a concept actually explained in the source.
2. Do not create generic learning or study questions.
3. Do not invent facts or introduce unrelated concepts.
4. Each question must have exactly four distinct options.
5. The correct_answer must be A, B, C, or D.
6. Include a short explanation grounded in the source.
7. Write the questions and options in the requested language.
8. Return exactly {number_of_questions} questions.
9. Return valid JSON only. Do not include Markdown fences.

Required JSON format:
{{
  "questions": [
    {{
      "question": "Question based on the lesson",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "A",
      "explanation": "Explanation grounded in the lesson"
    }}
  ]
}}
"""

        raw = await gemini_client.generate(prompt)

        if not isinstance(raw, str):
            raise ValueError(
                "The AI returned an unexpected response."
            )

        # Handle responses wrapped in Markdown fences.
        raw = raw.strip()
        raw = re.sub(
            r"^```(?:json)?\s*|\s*```$",
            "",
            raw,
            flags=re.IGNORECASE,
        )

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "The AI returned invalid quiz data. Please retry."
            ) from exc

        questions = (
            parsed.get("questions")
            if isinstance(parsed, dict)
            else parsed
        )

        if not isinstance(questions, list):
            raise ValueError("Invalid quiz response format.")

        validated = []

        for item in questions:
            if not isinstance(item, dict):
                continue

            question = item.get("question")
            options = item.get("options")
            answer = str(
                item.get("correct_answer", "")
            ).strip().upper()
            explanation = item.get("explanation", "")

            if (
                not isinstance(question, str)
                or not question.strip()
                or not isinstance(options, list)
                or len(options) != 4
                or not all(
                    isinstance(option, str) and option.strip()
                    for option in options
                )
                or len(set(options)) != 4
                or answer not in {"A", "B", "C", "D"}
            ):
                continue

            validated.append({
                "id": len(validated) + 1,
                "question": question.strip(),
                "options": options,
                "correct_answer": answer,
                "explanation": (
                    explanation.strip()
                    if isinstance(explanation, str)
                    else ""
                ),
            })

        if len(validated) != number_of_questions:
            raise ValueError(
                f"Expected {number_of_questions} valid questions, "
                f"but received {len(validated)}. Please retry."
            )

        return {
            "topic": topic,
            "language": language,
            "difficulty": difficulty,
            "questions": validated,
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
            question_id = str(question.get("id"))
            expected = str(
                question.get("correct_answer", "")
            ).upper()
            actual = str(
                answers.get(question_id, "")
            ).upper()

            if actual == expected:
                correct += 1
            else:
                incorrect += 1
                topic = question.get("topic")

                if topic:
                    knowledge_gaps.append(topic)

        total = len(questions)

        return {
            "correct": correct,
            "incorrect": incorrect,
            "total": total,
            "percentage": round(
                correct / total * 100, 2
            ) if total else 0,
            "knowledge_gaps": list(set(knowledge_gaps)),
        }


quiz_service = QuizService()
