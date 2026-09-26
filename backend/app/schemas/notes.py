from pydantic import BaseModel, Field


class NotesRequest(BaseModel):
    topic: str = Field(min_length=1)
    content: str = Field(min_length=1)
    language: str = "en"


class NotesResponse(BaseModel):
    topic: str
    language: str
    notes: str