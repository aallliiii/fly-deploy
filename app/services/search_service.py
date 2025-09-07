from datetime import datetime
from typing import List, Dict, Optional
from qdrant_client.http.models import Filter, MinShould
from app.services.qdrant_service import qdrant_service
from app.services.llm_service import llm_service
from app.schemas.query_enchancements_schemas import QueryEnhancement
from app.schemas.search_schemas import SearchResponse
from app.utils.date_utils import get_date_range
from app.config.settings import settings
from app.services.openai_service import openai_embedding_service
embedding_service = openai_embedding_service

class SearchService:
    def __init__(self):
        self.search_type_filters = {
            "event": {"key": "name_space", "match": {"value": "event"}},
            "product": {"key": "name_space", "match": {"value": "product"}}
        }
        self.audience_filters = {
            "male": {"key": "audience", "match": {"value": "Men"}},
            "female": {"key": "audience", "match": {"value": "Women"}},
            "unisex": {"key": "audience", "match": {"value": "Unisex"}}
        }
        self.weekend_filter = {"key": "event_on", "match": {"value": "weekend"}}

    def _build_time_filter(self, time_filter: Optional[str], search_type: str) -> Optional[Dict]:
        if search_type != "event" or not time_filter:
            return None

        start_date, end_date = get_date_range(time_filter)
        if not start_date or not end_date:
            return None

        time_filter_dict = {"key": "start_date", "range": {}}
        if start_date != datetime.min:
            time_filter_dict["range"]["gte"] = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        if end_date != datetime.max:
            time_filter_dict["range"]["lte"] = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        return time_filter_dict if time_filter_dict["range"] else None

    def _build_query_filter(self, enhancement: QueryEnhancement) -> Filter:
        must_filters = []
        should_filters = []

        if enhancement.search_type in self.search_type_filters:
            must_filters.append(self.search_type_filters[enhancement.search_type])

        # Apply audience filter
        if enhancement.audience in self.audience_filters:
            must_filters.append(self.audience_filters[enhancement.audience])

        # Apply weekend filter
        if enhancement.is_weekend:
            must_filters.append(self.weekend_filter)

        # Apply time filter
        time_filter = self._build_time_filter(enhancement.time_filter, enhancement.search_type)
        if time_filter:
            must_filters.append(time_filter)

        # Apply text filters
        if enhancement.other_keyword_filters:
            should_filters.extend(
                {"key": "content", "match": {"text": text_filter}}
                for text_filter in enhancement.other_keyword_filters
            )
        
        
        
        return Filter(
            must=must_filters,
            min_should=MinShould(min_count=len(should_filters), conditions=should_filters)
        )

    async def enhanced_semantic_search(self, enhancement: QueryEnhancement, limit: int = 15) -> List[Dict]:
        try:
            query_embedding = await embedding_service.get_text_embedding(enhancement.enhanced_query)
        except Exception as e:
            return e

        min_count = min(3, len(enhancement.other_keyword_filters or []))
        
        while min_count >= 0:
            try:
                
                query_filter = self._build_query_filter(enhancement)
                query_filter.min_should.min_count = min_count

                search_results = await qdrant_service.search(
                    query_embedding=query_embedding,
                    limit=limit,
                    query_filter=query_filter
                )
               
                
                if len(search_results.points) > 5:
                    break

                min_count -= 1
            except Exception as e:
                min_count -= 1
                continue
        if hasattr(search_results, "points"):
            points = search_results.points
        elif isinstance(search_results, dict) and "points" in search_results:
            points = search_results["points"]
        else:
            points = search_results
        formatted_results = []
        for result in points:
            
            formatted_result = {
                "score": result.score,
                "payload": result.payload,
                "original_id": result.payload.get("original_id"),
                "content": result.payload.get("content", ""),
                "name_space": result.payload.get("name_space", "")
            }
            formatted_results.append(formatted_result)
        
        return formatted_results

    async def intelligent_search(self, user_query: str, return_top_k: int = 7) -> SearchResponse:
        """Perform an intelligent search with query enhancement and reranking."""
        enhancement = None
        try:
            enhancement = await llm_service.enhance_query(user_query)
            
            search_results = await self.enhanced_semantic_search(enhancement, limit=15)
            if not search_results:
                return SearchResponse(
                    results=[],
                    enhancement=enhancement,
                    total_retrieved=0,
                    final_count=0
                )

            reranked_results = await llm_service.rerank_results(user_query, search_results, top_k=return_top_k)

            final_results = []
            for ranked_result in reranked_results.results:
                for search_result in search_results:
                    if (search_result['original_id'] == ranked_result.original_id and 
                        search_result['name_space'] == ranked_result.name_space):
                        final_results.append({
                            "original_id": ranked_result.original_id,
                            "relevance_score": ranked_result.relevance_score,
                            "relevance_reason": ranked_result.relevance_reason,
                            "payload": search_result['payload'],
                            "name_space": search_result['name_space']
                        })
                        break

            return SearchResponse(
                results=final_results,
                enhancement=enhancement,
                total_retrieved=len(search_results),
                final_count=len(final_results)
            )
        except Exception as e:
            # Create a default enhancement if it failed to generate
            if enhancement is None:
                enhancement = QueryEnhancement(
                    enhanced_query=user_query,
                    search_type="both",
                    audience=None,
                    other_keyword_filters=None,
                    time_filter=None,
                    is_weekend=False
                )
            
            return SearchResponse(
                results=[],
                enhancement=enhancement,
                total_retrieved=0,
                final_count=0
            )

search_service = SearchService()