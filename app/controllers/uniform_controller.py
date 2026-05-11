from fastapi import APIRouter, HTTPException
import pandas as pd
from pydantic import BaseModel
from typing import Union, Optional, Dict, Any, List
import os

from app.utils.csv_loader import load_csv


class Uniform(BaseModel):
    product_id: str
    product_name: str
    price: float
    uniform_type: str


router = APIRouter(prefix="/api/uniforms", tags=["Uniforms"])

UNIFORMS_PATH = "data/uniforms/products.csv"
SIZES_PATH = "data/uniforms/product_sizes.csv"

# Measurement column names
MEASUREMENT_COLUMNS = ["Length", "Waistline", "Bust/Chest", "Hips", "Shoulder", "Bottom Width"]


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
    """Remove null, NaN, and empty measurement fields from size data."""
    cleaned = {}
    for col in MEASUREMENT_COLUMNS:
        if col in size_row.index:
            value = size_row[col]
            # Check if value is not null, not NaN, and not empty string
            if pd.notna(value) and str(value).strip() != "":
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
def add_uniform(uniform: Uniform):
    try:
        df = pd.read_csv("data/uniforms/products.csv")
    except Exception:
        df = pd.DataFrame(columns=[
            "product_id",
            "product_name",
            "price",
            "uniform_type",
            "date_added",
            "date_updated",
            "is_deleted"
        ])

    new_data = {
        "product_id": uniform.product_id,
        "product_name": uniform.product_name,
        "price": uniform.price,
        "uniform_type": uniform.uniform_type,
        "date_added": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "date_updated": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "is_deleted": False
    }

    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    df.to_csv("data/uniforms/products.csv", index=False)

    return {
        "success": True,
        "message": "Uniform added successfully",
        "data": new_data
    }


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
    # Update products.csv
    df = pd.read_csv(UNIFORMS_PATH, index_col=False)

    if uniform_code not in df["product_id"].values:
        return {"error": "Uniform not found"}

    if product_name is not None:
        df.loc[df["product_id"] == uniform_code, "product_name"] = product_name

    if price is not None:
        df.loc[df["product_id"] == uniform_code, "price"] = price

    if uniform_type is not None:
        df.loc[df["product_id"] == uniform_code, "uniform_type"] = uniform_type

    df.loc[df["product_id"] == uniform_code, "date_updated"] = \
        pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

    df.to_csv(UNIFORMS_PATH, index=False)

    # Update product_sizes.csv if size-related parameters are provided
    if size is not None and any(param is not None for param in [length, waistline, bust_chest, hips, shoulder, bottom_width]):
        sizes_df = pd.read_csv(SIZES_PATH, index_col=False)
        sizes_df.columns = sizes_df.columns.str.strip()

        # Filter by both product_id and Size
        mask = (sizes_df["product_id"].astype(str).str.strip() == uniform_code.strip()) & \
               (sizes_df["Size"].astype(str).str.strip() == size.strip())

        if mask.any():
            if length is not None:
                sizes_df.loc[mask, "Length"] = length
            if waistline is not None:
                sizes_df.loc[mask, "Waistline"] = waistline
            if bust_chest is not None:
                sizes_df.loc[mask, "Bust/Chest"] = bust_chest
            if hips is not None:
                sizes_df.loc[mask, "Hips"] = hips
            if shoulder is not None:
                sizes_df.loc[mask, "Shoulder"] = shoulder
            if bottom_width is not None:
                sizes_df.loc[mask, "Bottom Width"] = bottom_width

            sizes_df.to_csv(SIZES_PATH, index=False)

    return {"success": True, "message": f"Uniform {uniform_code} updated successfully."}


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