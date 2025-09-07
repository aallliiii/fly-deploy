import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        self.EMBEDDINGS: str = os.getenv("EMBEDDINGS")
        self.QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY")
        self.QDRANT_URL: str = os.getenv("QDRANT_URL")
    
        self.COLLECTION_NAME: str = "fly-senga-openai"
        self.EMBEDDING_DIMENSION: int = 1536
        self.EMBEDDING_MODEL_NAME: str = "text-embedding-3-small"

        self.SCORING_THRESHOLD: float = 0.0
        self.OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
        self.LLM_MODEL_ENHANCER: str = "gpt-4.1-mini"
        self.LLM_MODEL_RERANKER: str = "gpt-4.1"
        self.LLM_TEMPERATURE: float = 0.1


settings = Settings()
