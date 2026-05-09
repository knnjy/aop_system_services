from fastapi import APIRouter
import pandas as pd

router = APIRouter(prefix="/api/books", tags=["Books"])
BOOKS_PATH = "data/books/books_data.csv"

@router.put("/update/{book_id}")
def update_book(book_id: int, title: str = None):
    # Load the CSV file
    df = pd.read_csv(BOOKS_PATH)

    # Check if the book_id exists
    if book_id not in df['book_id'].values:
        return {"error": "Book not found"}

    # Update fields if values are provided
    if title:
        df.loc[df['book_id'] == book_id, 'Title'] = title

    # Save the changes
    df.to_csv(BOOKS_PATH, index=False)
    return {"message": f"Book {book_id} updated successfully!"}
