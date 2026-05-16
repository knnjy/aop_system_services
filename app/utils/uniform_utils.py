import pandas as pd
from typing import Dict, Any

BOOKS_PATH = "data/books/books_data.csv"

def get_size_abbreviation(size: str) -> str:
    """Convert size name to abbreviation"""
    size_map = {
        "Small": "S",
        "Medium": "M", 
        "Large": "L",
        "XL": "XL",
        "2XL": "2XL",
        "3XL": "3XL",
    }
    return size_map.get(size, size.upper()[:3])


def extract_prefix(name: str) -> str:
    """Extract prefix from product name or uniform type"""
    if not name:
        return "PRD"
    # Get first 3 letters and convert to uppercase
    prefix = name.replace(" ", "")[:3].upper()
    return prefix if len(prefix) == 3 else (prefix + "D")[:3]


#FIltering and cleaning utilities for uniforms
def clean_row(row: pd.Series) -> Dict[str, Any]:
    """Clean a pandas row into a dict with stripped values."""
    cleaned = {}
    for col, val in row.items():
        if pd.isna(val):
            continue
        if isinstance(val, str) and val.strip() == "":
            continue
        cleaned[col] = str(val).strip() if isinstance(val, str) else val
    return cleaned

def strip_unwanted_fields(data: dict) -> dict:
    """
    Remove unwanted fields from dict (date_added, date_updated, is_deleted).
    """
    excluded = {"date_added", "date_updated", "is_deleted"}
    return {k: v for k, v in data.items() if k not in excluded and v is not None}