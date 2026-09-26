from typing import Any


class ProgressService:

    def calculate_progress(
        self,
        completed_topics: int,
        total_topics: int,
        completed_quizzes: int,
        average_quiz_score: float,
    ) -> dict[str, Any]:

        topic_progress = (
            completed_topics / total_topics
            if total_topics
            else 0
        )

        quiz_progress = (
            average_quiz_score / 100
        )

        overall = (
            topic_progress * 0.6
            + quiz_progress * 0.4
        )

        return {
            "overall_progress": round(
                overall * 100,
                2,
            ),
            "topics_completed": completed_topics,
            "total_topics": total_topics,
            "quizzes_completed": completed_quizzes,
            "average_quiz_score": average_quiz_score,
        }


progress_service = ProgressService()