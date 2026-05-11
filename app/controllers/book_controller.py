from fastapi import APIRouter
import pandas as pd

router = APIRouter(prefix="/api/books", tags=["Books"])
BOOKS_PATH = "data/books/books_data.csv"

@router.put("/update-book/{book_id}")
def update_book(book_id: str, updated_data: dict):
    # Load CSV fresh every request (para realtime)
    df = pd.read_csv(BOOKS_PATH)

    # Ensure book_id is string for comparison
    df['book_id'] = df['book_id'].astype(str)

    # Check if book exists
    if str(book_id) not in df['book_id'].values:
        return {"error": "Book not found"}

    # Update all columns except book_id
    for column, value in updated_data.items():
        if column in df.columns and column != "book_id":
            df.loc[df['book_id'] == str(book_id), column] = value

    # Save changes
    df.to_csv(BOOKS_PATH, index=False)

    return {"message": f"Book {book_id} updated successfully."}
