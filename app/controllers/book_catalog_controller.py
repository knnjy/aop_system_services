from fastapi import APIRouter
import pandas as pd

router = APIRouter(prefix="/api/books")
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
    return df.to_dict(orient="records")


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

    return df.to_dict(orient="records")


# Add new book data on books_data
@router.post("/add-book")
def add_book():
    return {}


# Update book data on books_data
@router.put("/update-book/{book_code}")
def update_book(book_code: str, title: str = None):
    df = _load_books()
    mask = _book_matches(df, book_code)

    if not mask.any():
        return {"error": "Book not found"}

    if title:
        df.loc[mask, "Title"] = title
        df.loc[mask, "date_updated"] = pd.Timestamp.now().strftime("%Y-%m-%d")

    df.to_csv(BOOKS_PATH, index=False)
    return {"message": f"Book {book_code} updated successfully!"}


# Soft delete book on books_data
@router.delete("/delete-book/{book_id}")
def delete_book(book_id: int):
    df = _load_books()

    if book_id not in df["book_id"].values:
        return {"error": "Book not found"}

    df.loc[df["book_id"] == book_id, "is_deleted"] = True
    df.to_csv(BOOKS_PATH, index=False)

    return {"message": f"Book {book_id} marked as deleted."}


# ### UNIFORM CRUD

# # List all unifrom product
# @router.get("/list-uniforms")
# def list_all_uniforms():
#     return {}


# # Filter uniforms by type, size, gender
# @router.get("/filter-uniforms")
# def filter_uniforms():
#     return {}

# # Add new uniform
# @router.post("/add-uniform")
# def add_uniform():
#     return {}

# # Update uniform by code
# @router.put("/update-uniform/{uniform_code}")
# def update_uniform():
#     return {}

# # Soft delete uniform
# @router.delete("/delete-uniform/{uniform_code}")
# def delete_uniform():
#     return {}

