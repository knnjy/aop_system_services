from fastapi import APIRouter
import pandas as pd

router = APIRouter(prefix="/api/uniforms", tags=["Uniforms"])
UNIFORMS_PATH = "data/uniforms/uniform_data.csv"

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
