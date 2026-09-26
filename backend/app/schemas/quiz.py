from pydantic import BaseModel, Field


class QuizGenerateRequest(BaseModel):
    topic: str = Field(min_length=1)
    content: str = Field(min_length=1)
    language: str = "en"
    question_count: int = Field(
        default=5,
        ge=1,
        le=20,
    )


class QuizQuestionResponse(BaseModel):
    id: int | None = None
    question: str
    options: list[str]
    correct_answer: str | None = None
    explanation: str | None = None


class QuizResponse(BaseModel):
    id: int | None = None
    title: str
    topic: str
    language: str
    questions: list[QuizQuestionResponse]


class QuizSubmitRequest(BaseModel):
    answers: dict[int, str]


class QuizResultResponse(BaseModel):
    quiz_id: int
    total_questions: int
    correct_answers: int
    score: float
    passed: bool