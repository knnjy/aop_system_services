from fastapi import APIRouter
import pandas as pd
from pydantic import BaseModel

from app.utils.csv_loader import load_csv


class Uniform(BaseModel):
    product_id: str
    product_name: str
    price: float
    uniform_type: str


router = APIRouter(prefix="/api/uniforms", tags=["Uniforms"])

UNIFORMS_PATH = "data/uniforms/products.csv"


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
    uniform_type: str = None
):
    df = pd.read_csv(UNIFORMS_PATH)

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

    return {"message": f"Uniform {uniform_code} updated successfully."}


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