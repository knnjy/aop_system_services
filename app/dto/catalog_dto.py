from typing import Any, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SizeDTO:
    """Data Transfer Object for uniform sizes"""
    uniform_size_id: Optional[str] = None
    product_id: Optional[str] = None
    size: str = ""
    length: Optional[float] = None
    waistline: Optional[float] = None
    bust_chest: Optional[float] = None
    hips: Optional[float] = None
    shoulder: Optional[float] = None
    bottom_width: Optional[float] = None
    product_stock: Optional[int] = None


@dataclass
class UniformDTO:
    """Data Transfer Object for uniforms"""
    product_id: Optional[str] = None
    product_name: str = ""
    price: float = 0.0
    uniform_type: str = ""
    date_added: Optional[datetime] = None
    date_updated: Optional[datetime] = None
    is_deleted: str = None
    sizes: Optional[List[SizeDTO]] = None


@dataclass
class BookDTO:
    """Data Transfer Object for books"""
    book_id: Optional[str] = None
    subject_code: str = ""
    title: str = ""
    price: float = 0.0
    stock_quantity: int = 0
    semester_available: int = 0
    date_added: Optional[str] = None
    date_updated: Optional[str] = None
    program_related: str = ""
    availability: str = "available"
    is_deleted: bool = False


from pydantic import BaseModel

class SizeUpdate(BaseModel):
    uniform_size_id: str
    product_stock: Optional[int] = None
    length: Optional[float] = None
    waistline: Optional[float] = None
    bust_chest: Optional[float] = None
    hips: Optional[float] = None
    shoulder: Optional[float] = None
    bottom_width: Optional[float] = None

class UniformUpdateRequest(BaseModel):
    updates: dict
    size_updates: Optional[List[SizeUpdate]] = None
