from fastapi import APIRouter
import pandas as pd

router = APIRouter(prefix="/api/uniforms", tags=["Uniforms"])
UNIFORMS_PATH = "data/uniforms/products.csv"

@router.delete("/delete/{product_id}")
def delete_uniform(product_id: str):
    # Load the CSV file
    df = pd.read_csv(UNIFORMS_PATH)

    # Check if the product_id exists
    if product_id not in df['product_id'].values:
        return {"error": "Uniform not found"}

    # Add column if it doesn't exist
    if "is_deleted" not in df.columns:
        df["is_deleted"] = False

    # Mark as deleted
    df.loc[df['product_id'] == product_id, 'is_deleted'] = True

    # Save the changes
    df.to_csv(UNIFORMS_PATH, index=False)
    return {"message": f"Uniform {product_id} marked as deleted."}
