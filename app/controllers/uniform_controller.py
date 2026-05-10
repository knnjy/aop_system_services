from fastapi import APIRouter
import pandas as pd

router = APIRouter(prefix="/api/uniforms", tags=["Uniforms"])
UNIFORMS_PATH = "data/uniforms/uniform_data.csv"

@router.delete("/delete-uniform/{product_id}") 
def delete_uniform(product_id: str):
    # Load the CSV file
    df = pd.read_csv(UNIFORMS_PATH)

    # Ensure 'product_id' column is string for comparison
    df['product_id'] = df['product_id'].astype(str)

    # Check if product_id exists
    if str(product_id) not in df['product_id'].values:
        return {"error": "Uniform not found"}

    # Soft delete: mark is_deleted = True
    if 'is_deleted' not in df.columns:
        df['is_deleted'] = False  # create column if missing

    df.loc[df['product_id'] == str(product_id), 'is_deleted'] = True

    # Save changes
    df.to_csv(UNIFORMS_PATH, index=False)
    return {"message": f"Uniform {product_id} marked as deleted."}
