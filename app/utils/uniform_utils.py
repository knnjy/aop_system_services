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