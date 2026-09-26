from datetime import datetime

from pydantic import BaseModel


class ProgressResponse(BaseModel):

    topic_id: int

    topic: str

    understanding_score: float

    quiz_score: float

    completion_percentage: float

    status: str

    last_accessed: datetime


class ProgressSummaryResponse(BaseModel):

    total_topics: int

    completed_topics: int

    in_progress_topics: int

    overall_progress: float

    average_understanding: float

    average_quiz_score: float