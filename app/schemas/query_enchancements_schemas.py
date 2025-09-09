from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class QueryEnhancement(BaseModel):
    event_enhanced_query: str = Field(description="Improved search query optimized for semantic search")
    product_enhanced_query: str = Field(description="Improved search query optimized for semantic search")
    search_type: Literal["event", "product", "both"] = Field(description="Type of item to search for")
    audience: Optional[Literal["male", "female", "unisex"]] = Field(description="Audience for the item")
    time_filter: Optional[Literal["past", "future", "today", "this_week", "this_month", "next_week", "next_month"]] = Field(
        default=None,
        description="Time filter for events (only applicable when search_type is 'event')"
    )
    is_weekend: Optional[bool] = Field(
        default=None,
        description="Is the query for a weekend (only applicable when search_type is 'event')"
    )
    other_keyword_filters: List[str] = Field(
        default=None,
        description="Keyword filter if applicable"
    )

class RankedResult(BaseModel):
    name_space: Literal["event", "product"] = Field(description="Type of item")
    original_id: str = Field(description="Original ID of the item")
    relevance_score: int = Field(description="Relevance score from 1-10")
    relevance_reason: str = Field(description="Brief explanation of why this item is relevant")

class RerankedResults(BaseModel):
    results: List[RankedResult] = Field(description="Top 7 most relevant results")