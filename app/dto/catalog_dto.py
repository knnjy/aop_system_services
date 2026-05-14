from typing import Any, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SizeDTO:
    """Data Transfer Object for uniform sizes"""
    uniform_size_id: str
    product_id: str
    size: str
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
    product_id: str
    product_name: str
    price: float
    uniform_type: str
    date_added: datetime
    date_updated: datetime
    is_deleted: bool
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
