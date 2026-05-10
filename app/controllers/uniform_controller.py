from fastapi import APIRouter
import pandas as pd

router = APIRouter(prefix="/api/uniforms", tags=["Uniforms"])
UNIFORMS_PATH = "data/uniforms/uniform_data.csv"

@router.delete("/delete-uniform/{product_id}")
def delete_uniform(product_id: str):
    df = pd.read_csv(UNIFORMS_PATH)

    if product_id not in df['product_id'].astype(str).values:
        return {"error": "Uniform not found"}

    if "is_deleted" not in df.columns:
        df["is_deleted"] = False

    df.loc[df['product_id'] == product_id, 'is_deleted'] = True
    df.to_csv(UNIFORMS_PATH, index=False)
    return {"message": f"Uniform {product_id} marked as deleted."}
