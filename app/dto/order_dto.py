from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, field_validator

class OrderItem(BaseModel):
    order_item_id: str
    request_id: str
    product_id: str
    quantity: int
    unit_price: int
    subtotal: int

class OrderRequest(BaseModel):
    request_id: str
    user_id: str
    total_amount: float
    order_items: List[OrderItem]
    status: str
    date_created: datetime
    approved_by: Optional[str] = None
    
    # @field_validator("user_id")
    # @classmethod
    # def check_id(cls, user_id: str):
        
    #     return{}

