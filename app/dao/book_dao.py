from typing import List, Optional
from pathlib import Path

import pandas as pd

from app.utils.csv_loader import load_csv, DATA_DIR
from app.dto.catalog_dto import BookDTO



class BookDAO:
    def __init__(self) -> None:
        self._books = load_csv("books/books_data.csv")

    def _build_book_dto(self, book_row: pd.Series) -> BookDTO:
        """Convert a book row to BookDTO"""
        return BookDTO(
            book_id=str(book_row["book_id"]),
            subject_code=str(book_row["subject_code"]),
            title=str(book_row["title"]),
            price=float(book_row["price"]),
            stock_quantity=int(book_row["stock_quantity"]),
            semester_available=int(book_row["semester_available"]),
            date_added=str(book_row["date_added"]),
            date_updated=str(book_row["date_updated"]),
            program_related=str(book_row["program_related"]),
            availability=str(book_row["availability"]),
            is_deleted=str(book_row["is_deleted"]),
        )
    
    def get_all(self) -> List[BookDTO]:
        books_df = load_csv("books/books_data.csv")
        return [self._build_book_dto(row) for _, row in books_df.iterrows()]


    def get_by_book_id(self, book_id: int) -> Optional[BookDTO]:
        """Fetch a specific book by book_id"""
        match = self._books[self._books["book_id"] == book_id]
        if match.empty:
            return None
        return self._build_book_dto(match.iloc[0])

    def get_by_subject_code(self, subject_code: str) -> List[BookDTO]:
        """Fetch books filtered by subject_code"""
        matches = self._books[self._books["subject_code"] == subject_code]
        books = []
        for _, row in matches.iterrows():
            book = self._build_book_dto(row)
            books.append(book)
        return books

    def get_by_program(self, program: str) -> List[BookDTO]:
        """Fetch books filtered by program_related"""
        matches = self._books[self._books["program_related"] == program]
        books = []
        for _, row in matches.iterrows():
            book = self._build_book_dto(row)
            books.append(book)
        return books

    def get_by_semester(self, semester: int) -> List[BookDTO]:
        """Fetch books available for a specific semester"""
        matches = self._books[self._books["semester_available"] == semester]
        books = []
        for _, row in matches.iterrows():
            book = self._build_book_dto(row)
            books.append(book)
        return books

    def get_next_book_id(self) -> str:
        """Generate the next book_id by incrementing from the last one"""
        if self._books.empty:
            return "BK0001"
        
        # Get the last book_id and extract the numeric part
        last_book_id = self._books.iloc[-1]["book_id"]
        # Remove 'BK' prefix and convert to int
        try:
            numeric_part = int(str(last_book_id).replace("BK", ""))
            next_numeric = numeric_part + 1
            return f"BK{next_numeric:04d}"
        except (ValueError, AttributeError):
            # Fallback if format is unexpected
            return f"BK{len(self._books) + 1:04d}"

    def save_book(self, book: BookDTO) -> BookDTO:
        """Add a new book to the CSV file"""
        new_row = pd.DataFrame({
            "book_id": [str(book.book_id)],
            "subject_code": [book.subject_code],
            "title": [book.title],
            "price": [str(book.price)],
            "stock_quantity": [str(book.stock_quantity)],
            "semester_available": [str(book.semester_available)],
            "date_added": [book.date_added],
            "date_updated": [book.date_updated],
            "program_related": [book.program_related],
            "availability": [book.availability],
            "is_deleted": [str(book.is_deleted)],
        })
        self._books = pd.concat([self._books, new_row], ignore_index=True)
        
        # Save to CSV
        csv_path = DATA_DIR / "books" / "books_data.csv"
        self._books.to_csv(csv_path, index=False)
        
        return book

    def get_stock_by_subject_code(self) -> dict:
        """Return stock quantities grouped by subject_code"""
        if self._books.empty:
            return {}
        
        grouped = self._books.groupby("subject_code")["stock_quantity"].sum()
        return grouped.to_dict()
    
    def update_book_flag(self, book: BookDTO) -> BookDTO:
        """Update an existing book row in the CSV file"""
        books_df = load_csv("books/books_data.csv")

        # Update the row by book_id
        books_df.loc[books_df["book_id"] == book.book_id, "is_deleted"] = str(book.is_deleted)
        books_df.loc[books_df["book_id"] == book.book_id, "date_updated"] = book.date_updated

        # Save back to CSV
        csv_path = DATA_DIR / "books" / "books_data.csv"
        books_df.to_csv(csv_path, index=False)

        # Refresh in-memory DataFrame
        self._books = load_csv("books/books_data.csv")

        return book

    def update(self, book: BookDTO) -> BookDTO:
        books_df = load_csv("books/books_data.csv")

        for field in book.__dataclass_fields__:
            if field != "book_id":
                value = getattr(book, field)
                # Normalize booleans to strings
                if isinstance(value, bool):
                    value = "True" if value else "False"
                books_df.loc[books_df["book_id"] == book.book_id, field] = value

        # Save back to CSV
        csv_path = DATA_DIR / "books" / "books_data.csv"
        books_df.to_csv(csv_path, index=False)

        # Refresh in-memory DataFrame
        self._books = load_csv("books/books_data.csv")

        return book


