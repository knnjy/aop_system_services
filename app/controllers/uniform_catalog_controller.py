from app.dto.catalog_dto import UniformDTO
from app.services.uniform_service import UniformService
from fastapi import APIRouter, HTTPException
import pandas as pd
from pathlib import Path
from pydantic import BaseModel
from typing import Union, Optional, Dict, Any, List
import os

from app.utils.csv_loader import load_csv
from app.services.uniform_service import UniformService
router = APIRouter(prefix="/api/uniforms", tags=["Uniforms"])

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
UNIFORMS_PATH = DATA_DIR / "uniforms" / "products.csv"
SIZES_PATH = DATA_DIR / "uniforms" / "product_sizes.csv"

# Measurement column names
MEASUREMENT_COLUMNS = ["Length", "Waistline", "Bust/Chest", "Hips", "Shoulder", "Bottom Width"]


_uniform_service = UniformService()


def safe_read_csv(file_path: str) -> pd.DataFrame:
    """Safely read CSV with consistent settings."""
    if not os.path.exists(file_path):
        raise HTTPException(status_code=500, detail=f"CSV file not found: {file_path}")

    try:
        df = pd.read_csv(file_path, index_col=False)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading CSV file: {str(e)}")


def safe_write_csv(df: pd.DataFrame, file_path: str):
    """Safely write CSV with consistent formatting."""
    try:
        df.to_csv(file_path, index=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error writing CSV file: {str(e)}")


def clean_size_data(size_row: pd.Series) -> Dict[str, Any]:
    """Remove null, empty, and placeholder fields from size data while preserving field order."""
    placeholders = {"black", "n/a", "na", "none", "-", "--"}
    cleaned = {}
    ordered_columns = ["product_id", "Size"] + MEASUREMENT_COLUMNS

    for col in ordered_columns:
        if col not in size_row.index:
            continue
        value = size_row[col]
        if pd.isna(value):
            continue
        value_str = str(value).strip()
        if value_str == "":
            continue
        if value_str.lower() in placeholders:
            continue
        cleaned[col] = value

    return cleaned


def validate_uniform_exists(df: pd.DataFrame, uniform_code: str):
    """Validate that a uniform exists in the dataframe."""
    if uniform_code not in df["product_id"].values:
        raise HTTPException(status_code=404, detail=f"Uniform {uniform_code} not found")


def validate_size_exists(sizes_df: pd.DataFrame, uniform_code: str, size: str):
    """Validate that a size exists for the given uniform."""
    mask = (sizes_df["product_id"].astype(str).str.strip() == uniform_code.strip()) & \
           (sizes_df["Size"].astype(str).str.strip() == size.strip())

    if not mask.any():
        raise HTTPException(status_code=404, detail=f"Size {size} not found for uniform {uniform_code}")


# LIST UNIFORMS
@router.get("/list-uniforms")
def list_uniforms():
    products = load_csv("uniforms/products.csv")
    sizes = load_csv("uniforms/product_sizes.csv")

    result = []

    for _, product in products.iterrows():
        product_id = product["product_id"]

        product_sizes = sizes[
            sizes["product_id"].astype(str).str.strip()
            == str(product_id).strip()
        ]

        result.append({
            "product_id": product["product_id"],
            "product_name": product["product_name"],
            "price": product["price"],
            "uniform_type": product["uniform_type"],
            "sizes": product_sizes.to_dict(orient="records")
        })

    return result


# ADD UNIFORM
@router.post("/add-uniform")
def create_uniform(unfiorm: UniformDTO):
    return _uniform_service.create_new_uniform(unfiorm)


# UPDATE UNIFORM
@router.put("/update-uniform/{uniform_code}")
def update_uniform(
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
    return _uniform_service.update_uniform(
        uniform_code=uniform_code,
        product_name=product_name,
        price=price,
        uniform_type=uniform_type,
        size=size,
        length=length,
        waistline=waistline,
        bust_chest=bust_chest,
        hips=hips,
        shoulder=shoulder,
        bottom_width=bottom_width
    )


# RTU UNIFORM FILTERING
router = APIRouter(prefix="/api/uniforms", tags=["Uniforms"])
uniform_service = UniformService()

# List all uniforms (no filter)
@router.get("/list-uniforms")
def list_all_uniforms():
    return uniform_service.list_uniforms()

# Filter uniforms by type
@router.get("/filter-uniform")
def list_rtu_uniforms(uniform_type: str = None):
    return uniform_service.list_uniforms(uniform_type)



# DELETE (SOFT DELETE) UNIFORM
@router.delete("/delete-uniform/{product_id}")
def delete_uniform(product_id: str):
    df = pd.read_csv(UNIFORMS_PATH)

    df["product_id"] = df["product_id"].astype(str)

    if str(product_id) not in df["product_id"].values:
        return {"error": "Uniform not found"}

    if "is_deleted" not in df.columns:
        df["is_deleted"] = False

    df.loc[df["product_id"] == str(product_id), "is_deleted"] = True

    df.to_csv(UNIFORMS_PATH, index=False)

    return {"message": f"Uniform {product_id} marked as deleted."}