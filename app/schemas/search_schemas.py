from pydantic import BaseModel, Field
from typing import List, Optional
from app.schemas.query_enchancements_schemas import QueryEnhancement

class SearchRequest(BaseModel):
    query: str
    top_k: int = Field(default=7, ge=1, le=20)


class SearchResult(BaseModel):
    original_id: str
    relevance_score: int
    relevance_reason: str
    payload: dict
    name_space: str

class SearchResponse(BaseModel):
    results: List[SearchResult]
    enhancement: QueryEnhancement
    total_retrieved: int
    final_count: int