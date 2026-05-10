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