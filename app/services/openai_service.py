import asyncio
import numpy as np
from typing import List
from openai import OpenAI
from app.config.settings import settings

class OpenAIEmbeddingService:
   def __init__(self):
       self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
      
   async def get_text_embedding(self, text: str) -> np.ndarray:
       def _get_embedding():
           response = self.client.embeddings.create(
               input=text,
               model=settings.EMBEDDING_MODEL_NAME
           )
           return np.array(response.data[0].embedding)
       
       return await asyncio.to_thread(_get_embedding)
  
   async def get_batch_embeddings(self, texts: List[str], batch_size: int = 32) -> List[np.ndarray]:
       def _get_batch_embeddings():
           embeddings = []
          
           for i in range(0, len(texts), batch_size):
               batch_texts = texts[i:i + batch_size]
              
               response = self.client.embeddings.create(
                   input=batch_texts,
                   model=settings.EMBEDDING_MODEL_NAME
               )
               
               batch_embeddings = [np.array(data.embedding) for data in response.data]
               embeddings.extend(batch_embeddings)
          
           return embeddings
       
       return await asyncio.to_thread(_get_batch_embeddings)

openai_embedding_service = OpenAIEmbeddingService()