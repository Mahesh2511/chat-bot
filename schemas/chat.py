from pydantic import BaseModel, field_validator


class ChatRequest(BaseModel):
    q: str

    @field_validator("q")
    @classmethod
    def question_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Question cannot be empty")
        if len(v) > 2000:
            raise ValueError("Question too long (max 2000 characters)")
        return v
