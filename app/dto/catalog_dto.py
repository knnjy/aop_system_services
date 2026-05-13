from typing import Any, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SizeDTO:
    """Data Transfer Object for uniform sizes"""
    product_id: str
    size: str
    length: Optional[float] = None
    waistline: Optional[float] = None
    bust_chest: Optional[float] = None
    hips: Optional[float] = None
    shoulder: Optional[float] = None
    bottom_width: Optional[float] = None


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
    book_id: int
    subject_code: str
    title: str
    price: float
    stock_quantity: int
    semester_available: int
    date_added: str
    date_updated: str
    program_related: str
    availability: str
    is_deleted: bool
