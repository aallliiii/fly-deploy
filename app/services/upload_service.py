from typing import List, Dict, Callable, Optional
from datetime import datetime
import uuid
from qdrant_client.models import PointStruct
from app.services.qdrant_service import qdrant_service
from app.utils.text_preprocessing import prepare_event_text, prepare_product_text
from app.utils.date_utils import is_weekend
from app.config.settings import settings
from app.services.openai_service import openai_embedding_service
embedding_service = openai_embedding_service

class UploadService:
    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
        self.text_processors: Dict[str, Callable] = {
            "event": prepare_event_text,
            "product": prepare_product_text
        }

    def _parse_date(self, start_date: Optional[str]) -> str:
        """Parse date string to ISO format."""
        if not start_date:
            return ""
        try:
            if isinstance(start_date, str):
                if "/" in start_date:
                    parsed_date = datetime.strptime(start_date, "%d/%m/%Y")
                elif "-" in start_date and "T" in start_date:
                    parsed_date = datetime.fromisoformat(start_date.replace("Z", ""))
                else:
                    parsed_date = datetime.strptime(start_date, "%Y-%m-%d")
                return parsed_date.strftime("%Y-%m-%dT%H:%M:%SZ")
            elif hasattr(start_date, 'strftime'):
                return start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
            else:
                return str(start_date)
        except (ValueError, TypeError) as e:
            return str(start_date)

    async def _process_batch(self, data_type: str, data: List[Dict], start_idx: int, end_idx: int) -> List[PointStruct]:
        batch = data[start_idx:end_idx]
        texts = []
        processor = self.text_processors.get(data_type)
        if not processor:
            return []

        try:
            for item in batch:
                if not isinstance(item, dict) or "id" not in item:
                    continue
                text = processor(item)
                texts.append(text)
        except Exception as e:
            return []

        try:
            embeddings = await embedding_service.get_batch_embeddings(texts)
        except Exception as e:
            return []

        points = []
        for idx, item in enumerate(batch):
            try:
                payload = {
                    "name_space": data_type,
                    "original_id": str(item.get("id")),
                    "content": texts[idx]
                }
                if data_type == "event":
                    start_date = self._parse_date(item.get("start_date"))
                    payload.update({
                        "start_date": start_date,
                        "event_on": is_weekend(item.get("start_date", ""))
                    })
                else:
                    payload["audience"] = item.get("audience")

                unique_id = str(uuid.uuid4())
                point = PointStruct(
                    id=unique_id,
                    vector=embeddings[idx],
                    payload=payload
                )
                points.append(point)
            except Exception as e:
                continue

        return points

    async def process_and_upload_data(self, data_type: str, data: List[Dict]) -> Dict:
        if not data or data_type not in self.text_processors:
            return {
                "message": f"Failed to upload {data_type}s: Invalid input",
                "count": 0
            }

        all_points = []
        total_count = 0

        for start_idx in range(0, len(data), self.batch_size):
            end_idx = min(start_idx + self.batch_size, len(data))
            batch_points = await self._process_batch(data_type, data, start_idx, end_idx)

            if batch_points:
                try:
                    await qdrant_service.upsert_points(batch_points)
                    all_points.extend(batch_points)
                    total_count += len(batch_points)
                except Exception as e:
                    continue

        message = f"Successfully uploaded {total_count} {data_type}s"
        if total_count < len(data):
            message += f" ({len(data) - total_count} items failed)"

        return {
            "message": message,
            "count": total_count
        }

upload_service = UploadService()