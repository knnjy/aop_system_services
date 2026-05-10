from fastapi import APIRouter
import pandas as pd

router = APIRouter(prefix="/api/uniforms", tags=["Uniforms"])

UNIFORMS_PATH = "data/uniforms/products.csv"


# LIST UNIFORMS
@router.get("/list-uniforms")
def list_uniforms():
    df = pd.read_csv(UNIFORMS_PATH)

    if "is_deleted" in df.columns:
        df = df[df["is_deleted"] == False]

    return df.to_dict(orient="records")


# ADD UNIFORM
@router.post("/add-uniform")
def add_uniform():
    return {
        "success": True,
        "message": "Uniform added successfully",
        "data": {
            "product_id": "U001"
        }
    }


# UPDATE UNIFORM (update by code)
@router.put("/update-uniform/{uniform_code}")
def update_uniform(uniform_code: str, product_name: str = None, price: float = None, uniform_type: str = None):
    df = pd.read_csv(UNIFORMS_PATH)

    if uniform_code not in df["product_id"].values:
        return {"error": "Uniform not found"}

    if product_name is not None:
        df.loc[df["product_id"] == uniform_code, "product_name"] = product_name

    if price is not None:
        df.loc[df["product_id"] == uniform_code, "price"] = price

    if uniform_type is not None:
        df.loc[df["product_id"] == uniform_code, "uniform_type"] = uniform_type

    df.loc[df["product_id"] == uniform_code, "date_updated"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    df.to_csv(UNIFORMS_PATH, index=False)

    return {"message": f"Uniform {uniform_code} updated successfully."}


# DELETE UNIFORM (soft delete)
@router.delete("/delete-uniform/{uniform_code}")
def delete_uniform(uniform_code: str):

    df = pd.read_csv(UNIFORMS_PATH)

    if uniform_code not in df["product_id"].values:
        return {"error": "Uniform not found"}

    if "is_deleted" not in df.columns:
        df["is_deleted"] = False

    df.loc[df["product_id"] == uniform_code, "is_deleted"] = True

    df.to_csv(UNIFORMS_PATH, index=False)

    return {"message": f"Uniform {uniform_code} marked as deleted."}