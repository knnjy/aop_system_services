from http.client import HTTPException
from datetime import datetime
from typing import Union, List

import pandas as pd

from app.dao.uniform_dao import UniformDAO
from app.dto.catalog_dto import UniformDTO, SizeDTO
from app.utils.csv_loader import load_csv, DATA_DIR
from app.utils.uniform_utils import get_size_abbreviation, extract_prefix
from app.utils.uniform_utils import clean_row, strip_unwanted_fields

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

    def _safe_write_csv(self, df: pd.DataFrame, csv_name: str):
        csv_path = DATA_DIR / "uniforms" / csv_name
        df.to_csv(csv_path, index=False)

    def update_uniform(
        self,
        uniform_code: str,
        product_name: str = None,
        price: float = None,
        uniform_type: str = None,
        size: str = None,
        length: Union[float, str] = None,
        waistline: Union[float, str] = None,
        bust_chest: Union[float, str] = None,
        hips: Union[float, str] = None,
        shoulder: Union[float, str] = None,
        bottom_width: Union[float, str] = None
    ):
        products = load_csv("uniforms/products.csv")
        uniform_code_str = str(uniform_code).strip()
        mask = products["product_id"].astype(str).str.strip() == uniform_code_str

        if not mask.any():
            return {"error": "Uniform not found"}

        if "is_deleted" in products.columns:
            deleted_mask = mask & products["is_deleted"].isin([True, "True", "true", 1, "1"])
            if deleted_mask.any():
                products.loc[deleted_mask, "is_deleted"] = False

        if product_name is not None:
            products.loc[mask, "product_name"] = product_name

        if price is not None:
            products.loc[mask, "price"] = price

        if uniform_type is not None:
            products.loc[mask, "uniform_type"] = uniform_type

        if "date_updated" in products.columns:
            products.loc[mask, "date_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self._safe_write_csv(products, "products.csv")

        # ✅ Updated to lowercase column names
        size_updates = {
            "length": length,
            "waistline": waistline,
            "bust_chest": bust_chest,
            "hips": hips,
            "shoulder": shoulder,
            "bottom_width": bottom_width
        }

        if size is not None and any(v is not None for v in size_updates.values()):
            sizes_df = load_csv("uniforms/product_sizes.csv")
            sizes_df.columns = sizes_df.columns.str.strip()

            # Updated "Size" to "size"
            size_mask = (
                sizes_df["product_id"].astype(str).str.strip() == uniform_code_str
            ) & (
                sizes_df["size"].astype(str).str.strip() == str(size).strip()
            )

            if size_mask.any():
                for column, value in size_updates.items():
                    if value is not None:
                        sizes_df.loc[size_mask, column] = value
                self._safe_write_csv(sizes_df, "product_sizes.csv")

        return {
            "success": True,
            "message": f"Uniform {uniform_code} updated successfully."
        }

    def list_uniforms(self):
        """Return all uniforms with sizes (formatted JSON response)"""
        uniforms = self._uniform_dao.get_all()

        result = []

        for uniform in uniforms:
            result.append({
                "product_id": uniform.product_id,
                "product_name": uniform.product_name,
                "price": uniform.price,
                "uniform_type": uniform.uniform_type,
                "sizes": [
                    {
                        "size": size.size,
                        "length": size.length,
                        "waistline": size.waistline,
                        "bust_chest": size.bust_chest,
                        "hips": size.hips,
                        "shoulder": size.shoulder,
                        "bottom_width": size.bottom_width,
                        "product_stock": size.product_stock
                    }
                    for size in (uniform.sizes or [])
                ]
            })

        return result
    

#Uniform Filter    
class UniformService:
    def __init__(self):
        self.dao = UniformDAO

    def list_uniforms(self, uniform_type: str = None) -> List[dict]:
        df = self.dao.load_uniforms()
        sizes_df = self.dao.load_sizes()

        df['product_id'] = df['product_id'].astype(str).str.strip()
        sizes_df['product_id'] = sizes_df['product_id'].astype(str).str.strip()

        df = df[df['is_deleted'].isin([False, 'False', 'false', 0, '0'])]

        if uniform_type:
            cleaned_uniform_type = uniform_type.strip().lower()
            df = df[df['uniform_type'].astype(str).str.strip().str.lower() == cleaned_uniform_type]

        uniforms: List[dict] = []
        for _, product in df.iterrows():
            product_data = clean_row(product)
            pid = product['product_id']
            product_sizes = sizes_df[sizes_df['product_id'] == pid]

            sizes_list: List[SizeDTO] = []
            for _, size_row in product_sizes.iterrows():
                cleaned_size = clean_row(size_row)
                if cleaned_size:
                    sizes_list.append(SizeDTO(**cleaned_size))

            uniform = UniformDTO(**product_data, sizes=sizes_list)
            data = strip_unwanted_fields(uniform.__dict__.copy())  

            # Clean nested sizes too
            cleaned_sizes = []
            for size in data.get("sizes", []):
                size_data = strip_unwanted_fields(size.__dict__.copy())
                cleaned_sizes.append(size_data)

            data["sizes"] = cleaned_sizes
            uniforms.append(data)

        return uniforms