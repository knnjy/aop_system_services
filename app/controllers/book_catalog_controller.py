from app.dto.catalog_dto import BookDTO
from app.services.book_service import BookService
from fastapi import APIRouter
import pandas as pd
from datetime import datetime
from pydantic import BaseModel

router = APIRouter(prefix="/api/books")

_book_service = BookService()

BOOKS_PATH = "data/books/books_data.csv"


def _load_books():
    df = pd.read_csv(BOOKS_PATH)
    if "is_deleted" not in df.columns:
        df["is_deleted"] = False
    return df


def _book_matches(df, book_code: str):
    if book_code.isdigit():
        book_id = int(book_code)
        return (df["book_id"] == book_id) | (df["subject_code"] == book_code)
    return df["subject_code"] == book_code


# Get all the list of book on book_data
@router.get("/list-books")
def list_books():
    df = _load_books()
    df = df[df["is_deleted"] == False]
    columns = ["book_id", "subject_code", "Title", "Price", "stock_quantity", "semester_available", "date_added", "date_updated", "Program Related", "availability"]
    return df[columns].to_dict(orient="records")


# Filter book by Program_related, Title, & semester available
@router.get("/filter-books")
def filter_books(program_related: str = None, title: str = None, semester_available: int = None):
    df = _load_books()
    df = df[df["is_deleted"] == False]

    if program_related:
        df = df[df["Program Related"].astype(str).str.contains(program_related, case=False, na=False)]

    if title:
        df = df[df["Title"].astype(str).str.contains(title, case=False, na=False)]

    if semester_available is not None:
        df = df[df["semester_available"] == semester_available]

    columns = ["book_id", "subject_code", "Title", "Price", "stock_quantity", "semester_available", "date_added", "date_updated", "Program Related", "availability"]
    return df[columns].to_dict(orient="records")


# Soft delete book on books_data
@router.delete("/delete-book/{book_id}")
def delete_book(book_id: int):
    df = _load_books()
    
    df["book_id"] = pd.to_numeric(df["book_id"], errors="coerce")

    if book_id not in df["book_id"].values:
        return {"error": "Book not found"}

    df.loc[df["book_id"] == book_id, "is_deleted"] = True
    df.to_csv(BOOKS_PATH, index=False)

    return {"message": f"Book {book_id} marked as deleted."}



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

@router.get("/list-books", summary="List all books")
def list_books():
    df = pd.read_csv(BOOKS_PATH)
    books = df.to_dict(orient="records")
    return books



@router.post("/add-book")
def add_book(book: BookDTO):
    return _book_service.add_new_book(book)

@router.get("/get-book-stock")
def get_stock():
    return _book_service.book_stock_update()