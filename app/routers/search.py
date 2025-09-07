from fastapi import APIRouter, HTTPException
from app.schemas.search_schemas import SearchRequest, SearchResponse
from app.services.search_service import search_service

router = APIRouter()

@router.post("/search", response_model=SearchResponse)
async def search_data(request: SearchRequest):
    """Search for events or products"""
    try:
        result = await search_service.intelligent_search(request.query, request.top_k)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")