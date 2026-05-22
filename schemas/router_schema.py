import re
from pydantic import BaseModel, HttpUrl, field_validator


class IngestRequest(BaseModel):
    file_name: str
    s3_url: HttpUrl

    @field_validator("s3_url")
    @classmethod
    def must_be_pdf(cls, v: HttpUrl) -> HttpUrl:
        if not str(v).lower().endswith(".pdf"):
            raise ValueError("URL must point to a PDF file")
        return v

    @field_validator("file_name")
    @classmethod
    def safe_file_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("file_name cannot be empty")
        if re.search(r"[/\\.]", v):
            raise ValueError("file_name must not contain path separators or dots")
        if len(v) > 128:
            raise ValueError("file_name too long (max 128 characters)")
        return v


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
