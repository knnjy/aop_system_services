from typing import Any, Dict, List, Optional

import pandas as pd

from app.utils.csv_loader import load_csv
from app.dto.catalog_dto import UniformDTO, SizeDTO


class UniformDAO:
    def __init__(self) -> None:
        self._products = load_csv("uniforms/products.csv")
        self._sizes = load_csv("uniforms/product_sizes.csv")

    def get_all(self) -> List[UniformDTO]:
        """Fetch all uniforms with their sizes"""
        uniforms = []
        for _, row in self._products.iterrows():
            uniform = self._build_uniform_dto(row)
            uniforms.append(uniform)
        return uniforms

    def get_by_product_id(self, product_id: str) -> Optional[UniformDTO]:
        """Fetch a specific uniform by product_id"""
        match = self._products[self._products["product_id"] == product_id]
        if match.empty:
            return None
        return self._build_uniform_dto(match.iloc[0])

    def get_by_uniform_type(self, uniform_type: str) -> List[UniformDTO]:
        """Fetch uniforms filtered by uniform_type"""
        matches = self._products[self._products["uniform_type"] == uniform_type]
        uniforms = []
        for _, row in matches.iterrows():
            uniform = self._build_uniform_dto(row)
            uniforms.append(uniform)
        return uniforms

    def get_active_uniforms(self) -> List[UniformDTO]:
        """Fetch only non-deleted uniforms"""
        active = self._products[self._products["is_deleted"] == False]
        uniforms = []
        for _, row in active.iterrows():
            uniform = self._build_uniform_dto(row)
            uniforms.append(uniform)
        return uniforms

    def _build_uniform_dto(self, product_row: pd.Series) -> UniformDTO:
        """Convert a product row to UniformDTO with associated sizes"""
        product_id = product_row["product_id"]
        
        # Get sizes for this product
        sizes_df = self._sizes[self._sizes["product_id"] == product_id]
        sizes = []
        for _, size_row in sizes_df.iterrows():
            size_dto = SizeDTO(
                product_id=size_row["product_id"],
                size=size_row["Size"],
                length=size_row["Length"] if pd.notna(size_row["Length"]) else None,
                waistline=size_row["Waistline"] if pd.notna(size_row["Waistline"]) else None,
                bust_chest=size_row["Bust/Chest"] if pd.notna(size_row["Bust/Chest"]) else None,
                hips=size_row["Hips"] if pd.notna(size_row["Hips"]) else None,
                shoulder=size_row["Shoulder"] if pd.notna(size_row["Shoulder"]) else None,
                bottom_width=size_row["Bottom Width"] if pd.notna(size_row["Bottom Width"]) else None,
            )
            sizes.append(size_dto)

        return UniformDTO(
            product_id=product_row["product_id"],
            product_name=product_row["product_name"],
            price=float(product_row["price"]),
            uniform_type=product_row["uniform_type"],
            date_added=pd.to_datetime(product_row["date_added"]),
            date_updated=pd.to_datetime(product_row["date_updated"]),
            is_deleted=bool(product_row["is_deleted"]),
            sizes=sizes if sizes else None,
        )
