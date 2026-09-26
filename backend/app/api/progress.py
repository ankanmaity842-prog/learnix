from fastapi import APIRouter

router = APIRouter(prefix="/progress", tags=["Progress"])


@router.get("/")
async def get_progress():
    """
    Get overall learner progress.
    """

    return {
        "overall_progress": 0,
        "topics_completed": 0,
        "videos_completed": 0,
        "quizzes_completed": 0,
        "average_quiz_score": 0,
        "learning_streak": 0,
    }


@router.get("/topics")
async def topic_progress():
    """
    Progress for individual topics.
    """

    return {
        "topics": []
    }


@router.get("/weekly")
async def weekly_progress():
    """
    Weekly learning analytics.
    """

    return {
        "days": [],
        "minutes": [],
        "sessions": [],
    }


@router.get("/dashboard")
async def progress_dashboard():
    """
    Complete dashboard data.
    """

    return {
        "understanding_score": 0,
        "knowledge_coverage": 0,
        "learning_velocity": 0,
        "quiz_accuracy": 0,
        "knowledge_gaps": [],
        "recommended_topics": [],
    }