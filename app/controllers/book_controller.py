from fastapi import APIRouter
import pandas as pd
from datetime import datetime

router = APIRouter(prefix="/api/books", tags=["Books"])
BOOKS_PATH = "data/books/books_data.csv"

@router.put("/update-book/{book_id}")
def update_book(book_id: str, updated_data: dict):
    # Load the CSV file fresh on every request (for real-time updates)
    df = pd.read_csv(BOOKS_PATH)

    # Ensure book_id is treated as string for comparison
    df['book_id'] = df['book_id'].astype(str)

    # Check if the book exists in the dataset
    if str(book_id) not in df['book_id'].values:
        return {"error": "Book not found"}

    # Apply updates to all columns except book_id
    for column, value in updated_data.items():
        if column in df.columns and column != "book_id":
            df.loc[df['book_id'] == str(book_id), column] = value

    # Automatically update the date_update column with current datetime
    if "date_update" in df.columns:
        df.loc[df['book_id'] == str(book_id), "date_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Save changes back to the CSV file
    df.to_csv(BOOKS_PATH, index=False)

    # Return success message
    return {"message": f"Book {book_id} updated successfully!"}
