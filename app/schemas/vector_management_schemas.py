from pydantic import BaseModel
from typing import List, Optional, Literal

class EventData(BaseModel):
    id: str
    name: str
    description: str
    start_date: str
    start_time:str
    end_date: str
    end_time: str
    address: str
    city: str
    state: str
    country: str
    zip_code: str
    ticket_price: str
    groups: str
    types_name: str
    status: str
    genre: str
    audience: str
    age_restriction: str
    features: str
    indoor_outdoor: str
    dress_code: str
    language: str
    season: str
    tags: str



class ProductData(BaseModel):
    id: str
    product_name: str
    product_description: str
    category_name: str
    brand_name: str
    type_name: str
    color: str
    material: str
    style: str
    occasion: str
    fit: str
    pattern: str
    season: str
    audience: str
    special_features: str
    tags: str



class UploadRequest(BaseModel):
    data_type: Literal["event", "product"]
    data: List[dict]
    

class DeleteEntryRequest(BaseModel):
    name_space: str
    original_id: str


class DeleteEntryResponse(BaseModel):
    message: str
    name_space: str
    original_id: str
    deleted: bool
    operation_result: Optional[dict] = None