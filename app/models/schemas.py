from pydantic import BaseModel
from typing import Optional


class DocumentCreate(BaseModel):
    filename: str
    content: str
    source: Optional[str] = None


class DocumentResponse(BaseModel):
    id: int
    filename: str
    source: Optional[str] = None

    class Config:
        from_attributes = True


class QueryRequest(BaseModel):
    query: str
    n_results: Optional[int] = 5