from http.client import HTTPException
from datetime import datetime
from typing import Dict, Optional, Union, List

import pandas as pd

from app.dao.uniform_dao import UniformDAO
from app.dto.catalog_dto import SizeUpdate, UniformDTO, SizeDTO
from app.utils.csv_loader import load_csv, DATA_DIR
from app.utils.uniform_utils import get_size_abbreviation, extract_prefix

class UniformService:
    def __init__(self):
        self._uniform_dao = UniformDAO()

    def create_new_uniform(self, uniform: UniformDTO, sizes: list = None):
        """Create a new uniform with sizes"""
        if not uniform.product_id:
            prefix = extract_prefix(uniform.product_name or uniform.uniform_type)
            uniform.product_id = self._uniform_dao.get_next_product_id(prefix)
        else:
            if self._uniform_dao.get_by_product_id(uniform.product_id):
                raise HTTPException(status_code=409, detail=f"Product with ID {uniform.product_id} already exists")
        
        current_date = datetime.now()
        uniform.date_added = current_date
        uniform.date_updated = current_date
        
        if uniform.is_deleted is None:
            uniform.is_deleted = False
        
        size_dtos = []
        sizes_list = sizes or uniform.sizes or []
        if sizes_list:
            for size_data in sizes_list:
                if isinstance(size_data, dict):
                    size_str = size_data.get('size', 'S')
                    size_abbrev = get_size_abbreviation(size_str)
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
                    if not size_data.uniform_size_id or not size_data.product_id:
                        size_abbrev = get_size_abbreviation(size_data.size)
                        size_data.uniform_size_id = f"{uniform.product_id}-{size_abbrev}"
                        size_data.product_id = uniform.product_id
                    size_dtos.append(size_data)
                
        saved_uniform = self._uniform_dao.save_uniform(uniform, size_dtos)
        
        return {
            "message": "Uniform added successfully",
            "product_id": saved_uniform.product_id,
            "product_name": saved_uniform.product_name,
            "uniform_type": saved_uniform.uniform_type,
            "sizes_added": len(size_dtos)
        }


    def update_uniform(
        self,
        product_id: str,
        updates: Dict[str, Union[str, float, bool]],
        size_updates: Optional[List[Union[Dict, SizeUpdate]]] = None
    ):
        """
        Update a uniform's product details and/or sizes.
        - product_id: the ID of the uniform to update
        - updates: dict of product fields to update (e.g. {"product_name": "New Name", "price": 950.0})
        - size_updates: optional list of dicts or Pydantic SizeUpdate objects
        """
        # Fetch the uniform
        uniform = self._uniform_dao.get_by_product_id(product_id)
        if not uniform:
            return {"error": "Uniform not found", "product_id": product_id}

        # Check if deleted (handle both string and boolean)
        is_deleted = uniform.is_deleted
        if isinstance(is_deleted, str):
            is_deleted = is_deleted.lower() in ("true", "1")
        if is_deleted:
            return {"error": "Cannot update a deleted uniform", "product_id": product_id}

        # Apply product updates
        for key, value in updates.items():
            if hasattr(uniform, key) and value is not None:
                setattr(uniform, key, value)

        # Always update date_updated timestamp
        uniform.date_updated = datetime.now()

        # Apply size updates if provided
        if size_updates:
            for size_update in size_updates:
                # Convert Pydantic model to dict if needed
                if not isinstance(size_update, dict):
                    size_update = size_update.dict()

                for size in (uniform.sizes or []):
                    if size.uniform_size_id == size_update.get("uniform_size_id"):
                        for key, value in size_update.items():
                            if hasattr(size, key) and value is not None:
                                setattr(size, key, value)

        # Persist changes back to CSV
        self._uniform_dao.save_uniform(uniform, uniform.sizes or [])

        # Return updated uniform as JSON-friendly dict
        return {
            "message": f"Uniform {product_id} updated successfully",
            "product_id": uniform.product_id,
            "product_name": uniform.product_name,
        }

    def list_uniforms(self):
        """Return all uniforms with sizes (formatted JSON response)"""
        uniforms = self._uniform_dao.get_all()
        result = []

        for uniform in uniforms:
            if uniform.is_deleted.lower() == "true":
                continue
            result.append({
                "product_id": uniform.product_id,
                "product_name": uniform.product_name,
                "price": uniform.price,
                "uniform_type": uniform.uniform_type,
                "sizes": [
                    {
                        k: v
                        for k, v in {
                            "size": size.size,
                            "length": size.length,
                            "waistline": size.waistline,
                            "bust_chest": size.bust_chest,
                            "hips": size.hips,
                            "shoulder": size.shoulder,
                            "bottom_width": size.bottom_width,
                            "product_stock": size.product_stock,
                        }.items()
                        if v not in (None, "", "NaN")
                    }
                    for size in (uniform.sizes or [])
                ]
            })

        return result

    def filter_uniforms(self, uniform_type: str):
        """Return uniforms filtered by uniform_type (only non-deleted)"""
        uniforms = self._uniform_dao.get_all()

        result = []

        for uniform in uniforms:
            # Skip deleted uniforms
            if uniform.is_deleted.lower() == "true":
                continue

            # Only include matching uniform_type
            if uniform.uniform_type != uniform_type:
                continue

            result.append({
                "product_id": uniform.product_id,
                "product_name": uniform.product_name,
                "price": uniform.price,
                "uniform_type": uniform.uniform_type,
                "sizes": [
                    {
                        k: v
                        for k, v in {
                            "size": size.size,
                            "length": size.length,
                            "waistline": size.waistline,
                            "bust_chest": size.bust_chest,
                            "hips": size.hips,
                            "shoulder": size.shoulder,
                            "bottom_width": size.bottom_width,
                            "product_stock": size.product_stock,
                        }.items()
                        if v not in (None, "", "NaN")
                    }
                    for size in (uniform.sizes or [])
                ]
            })

        return result

    def delete_uniform(self, product_id: str) -> dict:
        """Soft delete a uniform by product_id"""
        uniform = self._uniform_dao.get_by_product_id(product_id)
        if not uniform:
            return {"error": "Uniform not found", "product_id": product_id}
        
        success = self._uniform_dao.soft_delete_uniform(product_id)
        
        if success:
            return {
                "success": True,
                "message": f"Uniform {product_id} marked as deleted.",
                "product_id": product_id
            }
        else:
            return {"error": "Failed to delete uniform", "product_id": product_id}