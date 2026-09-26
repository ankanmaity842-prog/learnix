from pydantic import BaseModel, Field


class KnowledgeResponse(BaseModel):
    topic_id: int
    topic: str
    mastery_score: float
    confidence_score: float
    status: str


class KnowledgeGapResponse(BaseModel):
    topic: str
    missing_topics: list[str]
    gap_score: float
    explanation: str


class LearningPathResponse(BaseModel):
    target_topic: str
    prerequisites: list[str]
    learning_path: list[str]
    ready: bool