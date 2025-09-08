from datetime import datetime
from typing import List, Dict, Optional, Tuple
from abc import ABC, abstractmethod
from qdrant_client.http.models import Filter, MinShould
from app.services.qdrant_service import qdrant_service
from app.services.llm_service import llm_service
from app.schemas.query_enchancements_schemas import QueryEnhancement
from app.schemas.search_schemas import SearchResponse
from app.utils.date_utils import get_date_range
from app.services.openai_service import openai_embedding_service
embedding_service = openai_embedding_service

class FilterStrategy(ABC):
    @abstractmethod
    def build_filters(self, enhancement: QueryEnhancement) -> Tuple[List[Dict], List[Dict]]:
        """Returns (must_filters, should_filters)"""
        pass

class BaseFilterStrategy(FilterStrategy):
    def __init__(self):
        self.audience_filters = {
            "male": {"key": "audience", "match": {"value": "Men"}},
            "female": {"key": "audience", "match": {"value": "Women"}},
            "unisex": {"key": "audience", "match": {"value": "Unisex"}}
        }

    def build_filters(self, enhancement: QueryEnhancement) -> Tuple[List[Dict], List[Dict]]:
        must_filters = []
        should_filters = []

        if enhancement.audience in self.audience_filters:
            must_filters.append(self.audience_filters[enhancement.audience])

        if enhancement.other_keyword_filters:
            should_filters.extend(
                {"key": "content", "match": {"text": text_filter}}
                for text_filter in enhancement.other_keyword_filters
            )
        
        return must_filters, should_filters

class EventFilterStrategy(BaseFilterStrategy):
    def __init__(self):
        super().__init__()
        self.namespace_filter = {"key": "name_space", "match": {"value": "event"}}
        self.weekend_filter = {"key": "event_on", "match": {"value": "weekend"}}

    def _build_time_filter(self, time_filter: Optional[str]) -> Optional[Dict]:
        if not time_filter:
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

    def build_filters(self, enhancement: QueryEnhancement) -> Tuple[List[Dict], List[Dict]]:
        must_filters, should_filters = super().build_filters(enhancement)
        
        must_filters.append(self.namespace_filter)
        
        if enhancement.is_weekend:
            must_filters.append(self.weekend_filter)

        time_filter = self._build_time_filter(enhancement.time_filter)
        if time_filter:
            must_filters.append(time_filter)

        return must_filters, should_filters

class ProductFilterStrategy(BaseFilterStrategy):
    def __init__(self):
        super().__init__()
        self.namespace_filter = {"key": "name_space", "match": {"value": "product"}}

    def build_filters(self, enhancement: QueryEnhancement) -> Tuple[List[Dict], List[Dict]]:
        must_filters, should_filters = super().build_filters(enhancement)
        
        must_filters.append(self.namespace_filter)
        
        return must_filters, should_filters

class SearchTypeHandler:
    def __init__(self):
        self.strategies = {
            "event": EventFilterStrategy(),
            "product": ProductFilterStrategy()
        }

    def get_strategy(self, search_type: str) -> FilterStrategy:
        return self.strategies.get(search_type, BaseFilterStrategy())

    def get_search_types(self, search_type: str) -> List[str]:
        if search_type == "both":
            return ["event", "product"]
        return [search_type] if search_type in self.strategies else []


class ResultFormatter:
    @staticmethod
    def format_search_results(points) -> List[Dict]:
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

    @staticmethod
    def extract_points(search_results):
        if hasattr(search_results, "points"):
            return search_results.points
        elif isinstance(search_results, dict) and "points" in search_results:
            return search_results["points"]
        else:
            return search_results

class SearchService:
    def __init__(self):
        self.search_handler = SearchTypeHandler()
        self.formatter = ResultFormatter()

    def _build_query_filter(self, enhancement: QueryEnhancement, search_type: str) -> Filter:
        strategy = self.search_handler.get_strategy(search_type)
        must_filters, should_filters = strategy.build_filters(enhancement)
        
        return Filter(
            must=must_filters,
            min_should=MinShould(min_count=len(should_filters), conditions=should_filters)
        )

    async def _search_with_type(self, enhancement: QueryEnhancement, search_type: str, 
                               limit: int, query_embedding: List[float]) -> List[Dict]:
        """Perform search for a specific type with retry logic"""
        min_count = min(3, len(enhancement.other_keyword_filters or []))
        
        while min_count >= 0:
            try:
                query_filter = self._build_query_filter(enhancement, search_type)
                query_filter.min_should.min_count = min_count

                search_results = await qdrant_service.search(
                    query_embedding=query_embedding,
                    limit=limit,
                    query_filter=query_filter
                )
               
                points = self.formatter.extract_points(search_results)
                
                threshold = 2 if enhancement.search_type == "both" else 5
                if len(points) > threshold:
                    break

                min_count -= 1
            except Exception as e:
                min_count -= 1
                continue
        
        return self.formatter.format_search_results(points)

    async def enhanced_semantic_search(self, enhancement: QueryEnhancement, limit: int = 15) -> List[Dict]:
        try:
            query_embedding = await embedding_service.get_text_embedding(enhancement.enhanced_query)
        except Exception as e:
            return []

        search_types = self.search_handler.get_search_types(enhancement.search_type)
        
        if not search_types:
            return []

        if len(search_types) > 1:
            all_results = []
            type_limit = limit // len(search_types)
            
            for search_type in search_types:
                results = await self._search_with_type(enhancement, search_type, type_limit, query_embedding)
                all_results.extend(results)
            
            all_results.sort(key=lambda x: x["score"], reverse=True)
            return all_results
        
        return await self._search_with_type(enhancement, search_types[0], limit, query_embedding)

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