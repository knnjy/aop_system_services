from http.client import HTTPException
from datetime import datetime

from app.dao.uniform_dao import UniformDAO
from app.dto.catalog_dto import UniformDTO, SizeDTO


class UniformService:
    def __init__(self):
        self._uniform_dao = UniformDAO()

    def create_new_uniform(self, uniform: UniformDTO, sizes: list = None):
        """Create a new uniform with sizes"""
        # Auto-generate product_id if not provided
        if not uniform.product_id:
            # Extract prefix from product_name or uniform_type
            prefix = self._extract_prefix(uniform.product_name or uniform.uniform_type)
            uniform.product_id = self._uniform_dao.get_next_product_id(prefix)
        else:
            # Check if product_id already exists
            if self._uniform_dao.get_by_product_id(uniform.product_id):
                raise HTTPException(status_code=409, detail=f"Product with ID {uniform.product_id} already exists")
        
        # Always set timestamps to current date
        current_date = datetime.now()
        uniform.date_added = current_date
        uniform.date_updated = current_date
        
        # Set default values if not provided
        if uniform.is_deleted is None:
            uniform.is_deleted = False
        
        # Process sizes
        size_dtos = []
        sizes_list = sizes or uniform.sizes or []
        if sizes_list:
            for size_data in sizes_list:
                if isinstance(size_data, dict):
                    # Extract size abbreviation
                    size_str = size_data.get('size', 'S')
                    size_abbrev = self._get_size_abbreviation(size_str)
                    
                    # Generate uniform_size_id
                    size_id = f"{uniform.product_id}-{size_abbrev}"
                    size_dto = SizeDTO(
                        uniform_size_id=size_id,
                        product_id=uniform.product_id,
                        size=size_str,
                        length=float(size_data.get('length')) if size_data.get('length') else None,
                        waistline=float(size_data.get('waistline')) if size_data.get('waistline') else None,
                        bust_chest=float(size_data.get('bust_chest')) if size_data.get('bust_chest') else None,
                        hips=float(size_data.get('hips')) if size_data.get('hips') else None,
                        shoulder=float(size_data.get('shoulder')) if size_data.get('shoulder') else None,
                        bottom_width=float(size_data.get('bottom_width')) if size_data.get('bottom_width') else None,
                        product_stock=int(size_data.get('product_stock', 0)) if size_data.get('product_stock') else 0,
                    )
                    size_dtos.append(size_dto)
                    
                elif isinstance(size_data, SizeDTO):
                    # Generate the ID if not already set
                    if not size_data.uniform_size_id or not size_data.product_id:
                        size_abbrev = self._get_size_abbreviation(size_data.size)
                        size_data.uniform_size_id = f"{uniform.product_id}-{size_abbrev}"
                        size_data.product_id = uniform.product_id
                    size_dtos.append(size_data)
                
        # Save the uniform and sizes to CSV
        saved_uniform = self._uniform_dao.save_uniform(uniform, size_dtos)
        
        return {
            "message": "Uniform added successfully",
            "product_id": saved_uniform.product_id,
            "product_name": saved_uniform.product_name,
            "uniform_type": saved_uniform.uniform_type,
            "sizes_added": len(size_dtos)
        }
    
    def _get_size_abbreviation(self, size: str) -> str:
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

    def _extract_prefix(self, name: str) -> str:
        """Extract prefix from product name or uniform type"""
        if not name:
            return "PRD"
        # Get first 3 letters and convert to uppercase
        prefix = name.replace(" ", "")[:3].upper()
        return prefix if len(prefix) == 3 else (prefix + "D")[:3]