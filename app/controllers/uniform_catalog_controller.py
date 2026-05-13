from fastapi import APIRouter, HTTPException
import pandas as pd
from pydantic import BaseModel
from typing import Union, Optional, Dict, Any, List
import os

from app.utils.csv_loader import load_csv

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

class Uniform(BaseModel):
    product_id: str
    product_name: str
    price: float
    uniform_type: str
    size: List[dict[str, Any]]

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
    df = safe_read_csv(UNIFORMS_PATH)

    mask = df["product_id"].astype(str).str.strip() == uniform_code.strip()
    if not mask.any():
        return {"error": "Uniform not found"}

    # Auto-restore soft-deleted uniforms
    if "is_deleted" in df.columns:
        deleted_mask = mask & df["is_deleted"].isin([True, "True", "true", 1, "1"])
        if deleted_mask.any():
            df.loc[deleted_mask, "is_deleted"] = False

    if product_name is not None:
        df.loc[mask, "product_name"] = product_name

    if price is not None:
        df.loc[mask, "price"] = price

    if uniform_type is not None:
        df.loc[mask, "uniform_type"] = uniform_type

    if "date_updated" in df.columns:
        df.loc[mask, "date_updated"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

    df.to_csv(UNIFORMS_PATH, index=False)

    # Update product_sizes.csv if size-related parameters are provided
    if size is not None and any(param is not None for param in [length, waistline, bust_chest, hips, shoulder, bottom_width]):
        sizes_df = safe_read_csv(SIZES_PATH)
        sizes_df.columns = sizes_df.columns.str.strip()

        size_mask = (sizes_df["product_id"].astype(str).str.strip() == uniform_code.strip()) & \
                    (sizes_df["Size"].astype(str).str.strip() == size.strip())

        if size_mask.any():
            if length is not None:
                sizes_df.loc[size_mask, "Length"] = length
            if waistline is not None:
                sizes_df.loc[size_mask, "Waistline"] = waistline
            if bust_chest is not None:
                sizes_df.loc[size_mask, "Bust/Chest"] = bust_chest
            if hips is not None:
                sizes_df.loc[size_mask, "Hips"] = hips
            if shoulder is not None:
                sizes_df.loc[size_mask, "Shoulder"] = shoulder
            if bottom_width is not None:
                sizes_df.loc[size_mask, "Bottom Width"] = bottom_width

            sizes_df.to_csv(SIZES_PATH, index=False)

    return {
        "success": True,
        "message": f"Uniform {uniform_code} updated successfully."
    }


# RTU UNIFORM FILTERING
RTU_UNIFORMS_PATH = "data/uniforms/products.csv"


def _load_rtu_uniforms() -> pd.DataFrame:
    df = load_csv("uniforms/products.csv")
    df["is_deleted"] = df.get("is_deleted", False)
    return df


@router.get("/filter-uniform")
def list_rtu_uniforms(
    size: str = None,
    gender: str = None,
    uniform_type: str = None
):
    df = _load_rtu_uniforms()
    sizes_df = load_csv("uniforms/product_sizes.csv")

    # Normalize product IDs and add gender mapping
    df["product_id"] = df["product_id"].astype(str).str.strip()
    sizes_df["product_id"] = sizes_df["product_id"].astype(str).str.strip()

    gender_mapping = {
        'TOP-001': 'Male',
        'TOP-002': 'Female',
        'BOT-001': 'Male',
        'SKT-001': 'Female',
        'PNT-001': 'Female',
        'SHT-001': 'Unisex',
        'PNT-002': 'Unisex',
        'SHT-002': 'Unisex'
    }
    df['Gender'] = df['product_id'].map(gender_mapping)

    # Exclude deleted rows
    df = df[df['is_deleted'].isin([False, 'False', 'false', 0, '0'])]

    # Apply filters only if parameters are provided
    if uniform_type:
        cleaned_uniform_type = uniform_type.strip().lower()
        df = df[df['uniform_type'].astype(str).str.strip().str.lower() == cleaned_uniform_type]

    if gender:
        cleaned_gender = gender.strip().lower()
        if cleaned_gender == 'male':
            allowed_genders = ['male', 'unisex']
        elif cleaned_gender == 'female':
            allowed_genders = ['female', 'unisex']
        else:
            allowed_genders = [cleaned_gender]

        df = df[df['Gender'].astype(str).str.strip().str.lower().isin(allowed_genders)]

    if size:
        cleaned_size = size.strip().lower()
        matching_ids = sizes_df[
            sizes_df['Size'].astype(str).str.strip().str.lower() == cleaned_size
        ]['product_id'].unique()
        df = df[df['product_id'].isin(matching_ids)]

    # Build nested size records per product
    result = []
    for _, product in df.iterrows():
        pid = product['product_id']
        product_sizes = sizes_df[sizes_df['product_id'] == pid]

        if size:
            product_sizes = product_sizes[product_sizes['Size'].astype(str).str.lower() == size.lower()]

        product_info = []
        for _, size_row in product_sizes.iterrows():
            cleaned_row = clean_size_data(size_row)
            if cleaned_row:
                product_info.append(cleaned_row)

        result.append({
            'product_name': product['product_name'],
            'uniform_type': product['uniform_type'],
            'Product Info': product_info
        })

    return result


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