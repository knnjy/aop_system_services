from fastapi import APIRouter
import pandas as pd

router = APIRouter(prefix="/api/books", tags=["Books"])
BOOKS_PATH = "data/books/books_data.csv"

@router.put("/update-book/{book_id}")
def update_book(book_id: str, program: str = None, books: str = None):
    # Load the CSV file
    df = pd.read_csv(BOOKS_PATH)

    # Ensure 'book_id' column is string for comparison
    df['book_id'] = df['book_id'].astype(str)

    # Check if book_id exists
    if str(book_id) not in df['book_id'].values:
        return {"error": "Book not found"}

    # Apply updates
    update_data = {
        "program": program,
        "books": books
    }

    for key, value in update_data.items():
        if value is not None and key in df.columns:
            df.loc[df['book_id'] == str(book_id), key] = value

    # Save changes
    df.to_csv(BOOKS_PATH, index=False)
    return {"message": f"Book {book_id} updated successfully!"}
