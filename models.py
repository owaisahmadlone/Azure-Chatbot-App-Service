from pydantic import BaseModel
class Question(BaseModel):
    question: str

class Answer(BaseModel):
    answer: str
    ref_chunks: list[str] | None = None
    ref_docs: list[str] | None = None
    ref_pages:list[int] | None = None