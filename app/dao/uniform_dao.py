from typing import Any, Dict, List, Optional
from pathlib import Path

import pandas as pd

from app.utils.csv_loader import load_csv, DATA_DIR
from app.dto.catalog_dto import UniformDTO, SizeDTO


class UniformDAO:
    def __init__(self) -> None:
        self._products = load_csv("uniforms/products.csv")
        self._sizes = load_csv("uniforms/product_sizes.csv")
    
    def _build_uniform_dto(self, product_row: pd.Series) -> UniformDTO:
        """Convert a product row to UniformDTO with associated sizes"""
        product_id = product_row["product_id"]
        
        # Get sizes for this product
        sizes_df = self._sizes[self._sizes["product_id"] == product_id]
        sizes = []
        for _, size_row in sizes_df.iterrows():
            size_dto = SizeDTO(
                uniform_size_id=size_row["uniform_size_id"],
                product_id=size_row["product_id"],
                size=size_row["size"],
                length=size_row["length"] if pd.notna(size_row["length"]) else None,
                waistline=size_row["waistline"] if pd.notna(size_row["waistline"]) else None,
                bust_chest=size_row["bust_chest"] if pd.notna(size_row["bust_chest"]) else None,
                hips=size_row["hips"] if pd.notna(size_row["hips"]) else None,
                shoulder=size_row["shoulder"] if pd.notna(size_row["shoulder"]) else None,
                bottom_width=size_row["bottom_width"] if pd.notna(size_row["bottom_width"]) else None,
                product_stock=int(size_row["product_stock"]) if pd.notna(size_row["product_stock"]) else None,
            )
            sizes.append(size_dto)

        return UniformDTO(
            product_id=product_row["product_id"],
            product_name=product_row["product_name"],
            price=float(product_row["price"]),
            uniform_type=product_row["uniform_type"],
            date_added=pd.to_datetime(product_row["date_added"]),
            date_updated=pd.to_datetime(product_row["date_updated"]),
            is_deleted=str(product_row["is_deleted"]),
            sizes=sizes if sizes else None,
        )
    
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

    def get_next_product_id(self, prefix: str) -> str:
        """Generate the next product_id by incrementing from the last one with same prefix"""
        if self._products.empty:
            return f"{prefix}-001"
        
        # Filter products with same prefix
        matching = self._products[self._products["product_id"].str.startswith(prefix)]
        if matching.empty:
            return f"{prefix}-001"
        
        # Get the last product_id and extract the numeric part
        last_product_id = matching.iloc[-1]["product_id"]
        try:
            numeric_part = int(str(last_product_id).split("-")[1])
            next_numeric = numeric_part + 1
            return f"{prefix}-{next_numeric:03d}"
        except (ValueError, IndexError):
            return f"{prefix}-{len(matching) + 1:03d}"

    # def save_uniform(self, uniform: UniformDTO, sizes: List[SizeDTO]) -> UniformDTO:
    #     """Add a new uniform (product) with sizes to CSV files"""
    #     # Save product
    #     product_row = pd.DataFrame({
    #         "product_id": [uniform.product_id],
    #         "product_name": [uniform.product_name],
    #         "price": [str(uniform.price)],
    #         "uniform_type": [uniform.uniform_type],
    #         "date_added": [uniform.date_added.strftime("%Y-%m-%d %H:%M:%S")],
    #         "date_updated": [uniform.date_updated.strftime("%Y-%m-%d %H:%M:%S")],
    #         "is_deleted": [str(uniform.is_deleted)],
    #     })
    #     self._products = pd.concat([self._products, product_row], ignore_index=True)
        
    #     # Save product sizes
    #     if sizes:
    #         size_rows = []
    #         for size in sizes:
    #             size_rows.append({
    #                 "uniform_size_id": size.uniform_size_id,  # This must have a value
    #                 "product_id": size.product_id,             # This must have a value
    #                 "size": size.size,
    #                 "length": size.length if size.length else "",
    #                 "waistline": size.waistline if size.waistline else "",
    #                 "bust_chest": size.bust_chest if size.bust_chest else "",
    #                 "hips": size.hips if size.hips else "",
    #                 "shoulder": size.shoulder if size.shoulder else "",
    #                 "bottom_width": size.bottom_width if size.bottom_width else "",
    #                 "product_stock": size.product_stock if size.product_stock else "",
    #             })
    #         sizes_df = pd.DataFrame(size_rows)
    #         self._sizes = pd.concat([self._sizes, sizes_df], ignore_index=True)
            
    #         # Save sizes to CSV
    #         csv_path = DATA_DIR / "uniforms" / "product_sizes.csv"
    #         self._sizes.to_csv(csv_path, index=False)
        
    #     # Save products to CSV
    #     csv_path = DATA_DIR / "uniforms" / "products.csv"
    #     self._products.to_csv(csv_path, index=False)
        
    #     return uniform
    def save_uniform(self, uniform: UniformDTO, sizes: List[SizeDTO]) -> UniformDTO:
        """Add or update a uniform (product) with sizes in CSV files"""
        # Ensure date_added and date_updated are datetime objects for strftime
        date_added = uniform.date_added
        date_updated = uniform.date_updated
        
        if isinstance(date_added, str):
            date_added = pd.to_datetime(date_added)
        if isinstance(date_updated, str):
            date_updated = pd.to_datetime(date_updated)
        
        # Convert to string format for CSV
        date_added_str = date_added.strftime("%Y-%m-%d %H:%M:%S") if hasattr(date_added, 'strftime') else str(date_added)
        date_updated_str = date_updated.strftime("%Y-%m-%d %H:%M:%S") if hasattr(date_updated, 'strftime') else str(date_updated)
        
        # --- Update products.csv ---
        product_id_str = str(uniform.product_id).strip()
        products_with_id = self._products[self._products["product_id"].astype(str).str.strip() == product_id_str]
        
        if not products_with_id.empty:
            # Update existing row
            self._products.loc[self._products["product_id"].astype(str).str.strip() == product_id_str, [
                "product_name", "price", "uniform_type", "date_added", "date_updated", "is_deleted"
            ]] = [
                uniform.product_name,
                str(uniform.price),
                uniform.uniform_type,
                date_added_str,
                date_updated_str,
                str(uniform.is_deleted),
            ]
        else:
            # Add new row
            product_row = pd.DataFrame({
                "product_id": [product_id_str],
                "product_name": [uniform.product_name],
                "price": [str(uniform.price)],
                "uniform_type": [uniform.uniform_type],
                "date_added": [date_added_str],
                "date_updated": [date_updated_str],
                "is_deleted": [str(uniform.is_deleted)],
            })
            self._products = pd.concat([self._products, product_row], ignore_index=True)

        # Save products.csv
        csv_path = DATA_DIR / "uniforms" / "products.csv"
        self._products.to_csv(csv_path, index=False)

        # --- Update product_sizes.csv ---
        if sizes:
            # Remove old sizes for this product
            self._sizes = self._sizes[self._sizes["product_id"].astype(str).str.strip() != product_id_str]

            # Add new sizes
            size_rows = []
            for size in sizes:
                size_rows.append({
                    "uniform_size_id": size.uniform_size_id or "",
                    "product_id": size.product_id or "",
                    "size": size.size or "",
                    "length": size.length if size.length else "",
                    "waistline": size.waistline if size.waistline else "",
                    "bust_chest": size.bust_chest if size.bust_chest else "",
                    "hips": size.hips if size.hips else "",
                    "shoulder": size.shoulder if size.shoulder else "",
                    "bottom_width": size.bottom_width if size.bottom_width else "",
                    "product_stock": size.product_stock if size.product_stock else "",
                })
            if size_rows:
                sizes_df = pd.DataFrame(size_rows)
                self._sizes = pd.concat([self._sizes, sizes_df], ignore_index=True)

            # Save product_sizes.csv
            csv_path = DATA_DIR / "uniforms" / "product_sizes.csv"
            self._sizes.to_csv(csv_path, index=False)

        return uniform

  
    def soft_delete_uniform(self, product_id: str) -> bool:
        """Soft delete a uniform by marking is_deleted as True"""
        match = self._products[self._products["product_id"] == product_id]
        if match.empty:
            return False
        
        if "is_deleted" not in self._products.columns:
            self._products["is_deleted"] = False
        
        self._products.loc[self._products["product_id"] == product_id, "is_deleted"] = True
        self._products.loc[self._products["product_id"] == product_id, "date_updated"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Save to CSV
        csv_path = DATA_DIR / "uniforms" / "products.csv"
        self._products.to_csv(csv_path, index=False)
        
        return True