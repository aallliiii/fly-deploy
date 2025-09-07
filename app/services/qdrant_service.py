import asyncio
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter
from qdrant_client.http import models
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import Filter, FieldCondition, MatchValue
from app.config.settings import settings
from typing import List

class QdrantService:
    def __init__(self):
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY
        )
        self.collection_name = settings.COLLECTION_NAME
   
    async def create_collection(self):
        try:
            
            await asyncio.to_thread(
                self.client.get_collection,
                collection_name=self.collection_name
            )
            
            return
            
        except (UnexpectedResponse, Exception):
            
            await asyncio.to_thread(
                self.client.create_collection,
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=settings.EMBEDDING_DIMENSION,
                    distance=Distance.COSINE
                )
            )
           
            await asyncio.to_thread(
                self.client.create_payload_index,
                collection_name=self.collection_name,
                field_name="name_space",
                field_schema=models.PayloadSchemaType.KEYWORD
            )

            await asyncio.to_thread(
                self.client.create_payload_index,
                collection_name=self.collection_name,
                field_name="original_id",
                field_schema=models.PayloadSchemaType.KEYWORD
            )

            await asyncio.to_thread(
                self.client.create_payload_index,
                collection_name=self.collection_name,
                field_name="content",
                field_schema=models.PayloadSchemaType.TEXT
            )
            await asyncio.to_thread(
                self.client.create_payload_index,
                collection_name=self.collection_name,
                field_name="audience",
                field_schema=models.PayloadSchemaType.KEYWORD
            )
            await asyncio.to_thread(
                self.client.create_payload_index,
                collection_name=self.collection_name,
                field_name="start_date",
                field_schema=models.PayloadSchemaType.DATETIME
            )
            await asyncio.to_thread(
                self.client.create_payload_index,
                collection_name=self.collection_name,
                field_name="event_on",
                field_schema=models.PayloadSchemaType.KEYWORD
            )
            
            print(f"Collection '{self.collection_name}' created successfully with indexes.")
   
    async def upsert_points(self, points: List[PointStruct]):
        await asyncio.to_thread(
            self.client.upsert,
            collection_name=self.collection_name,
            points=points
        )
   
    async def search(self, query_embedding, limit: int = 15, query_filter: Filter = None):
        return await asyncio.to_thread(
            self.client.query_points,
            collection_name=self.collection_name,
            query=query_embedding,
            limit=limit,
            score_threshold=settings.SCORING_THRESHOLD,
            query_filter=query_filter
        )

    async def delete_entry(self, name_space: str, original_id: str):
        search_result = await asyncio.to_thread(
        self.client.scroll,
        collection_name=self.collection_name,
        scroll_filter=Filter(
            must=[
                FieldCondition(key="name_space", match=MatchValue(value=name_space)),
                FieldCondition(key="original_id", match=MatchValue(value=original_id))
            ]
        )
        )        
        points, _ = search_result
        
        if not points:
            return False
        
        result = await asyncio.to_thread(
            self.client.delete,
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(key="name_space", match=MatchValue(value=name_space)),
                    FieldCondition(key="original_id", match=MatchValue(value=original_id))
                ]
            )
        )    
        return result

qdrant_service = QdrantService()