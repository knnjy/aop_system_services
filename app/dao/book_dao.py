from typing import List, Optional
from pathlib import Path

import pandas as pd

from app.utils.csv_loader import load_csv, DATA_DIR
from app.dto.catalog_dto import BookDTO



class BookDAO:
    def __init__(self) -> None:
        self._books = load_csv("books/books_data.csv")

    def get_all(self) -> List[BookDTO]:
        """Fetch all books"""
        books = []
        for _, row in self._books.iterrows():
            book = self._build_book_dto(row)
            books.append(book)
        return books

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
        matches = self._books[self._books["Program Related"] == program]
        books = []
        for _, row in matches.iterrows():
            book = self._build_book_dto(row)
            books.append(book)
        return books

    def get_available_books(self) -> List[BookDTO]:
        """Fetch only available books that are not deleted"""
        available = self._books[
            (self._books["availability"] == "available") & 
            (self._books["is_deleted"] == False)
        ]
        books = []
        for _, row in available.iterrows():
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
            "Title": [book.title],
            "Price": [str(book.price)],
            "stock_quantity": [str(book.stock_quantity)],
            "semester_available": [str(book.semester_available)],
            "date_added": [book.date_added],
            "date_updated": [book.date_updated],
            "Program Related": [book.program_related],
            "availability": [book.availability],
            "is_deleted": [str(book.is_deleted)],
        })
        self._books = pd.concat([self._books, new_row], ignore_index=True)
        
        # Save to CSV
        csv_path = DATA_DIR / "books" / "books_data.csv"
        self._books.to_csv(csv_path, index=False)
        
        return book

    def _build_book_dto(self, book_row: pd.Series) -> BookDTO:
        """Convert a book row to BookDTO"""
        return BookDTO(
            book_id=int(book_row["book_id"]),
            subject_code=str(book_row["subject_code"]),
            title=str(book_row["Title"]),
            price=float(book_row["Price"]),
            stock_quantity=int(book_row["stock_quantity"]),
            semester_available=int(book_row["semester_available"]),
            date_added=str(book_row["date_added"]),
            date_updated=str(book_row["date_updated"]),
            program_related=str(book_row["Program Related"]),
            availability=str(book_row["availability"]),
            is_deleted=bool(book_row["is_deleted"]),
        )
    def get_stock_by_subject_code(self) -> dict:
        """Return stock quantities grouped by subject_code"""
        if self._books.empty:
            return {}
        
        grouped = self._books.groupby("subject_code")["stock_quantity"].sum()
        return grouped.to_dict()
    
    # Load books with is_deleted check
    def load_books(self) -> pd.DataFrame:
        """Load books from CSV with is_deleted column check"""
        # Replace the missing global variable with a direct local string path
        target_path = "data/books/books_data.csv"
        
        df = pd.read_csv(target_path)
        if "is_deleted" not in df.columns:
            df["is_deleted"] = False
        return df

    # Filter books by program, title, and semester
    def filter_books(self, program_related=None, title=None, semester_available=None) -> List[dict]:
        """Load CSV directly, filter, and return a list of plain dicts (no DTO mapping)."""
        import pandas as pd

        target_path = "data/books/books_data.csv"
        try:
            df = pd.read_csv(target_path)
        except Exception:
            return []

        # Filter out deleted rows if column exists
        if "is_deleted" in df.columns:
            df = df[df["is_deleted"].astype(str).str.lower().str.strip() != "true"]

        # Apply dynamic filters
        if program_related:
            df = df[df["Program Related"].astype(str).str.contains(str(program_related).strip(), case=False, na=False, regex=False)]

        if title:
            df = df[df["Title"].astype(str).str.contains(str(title).strip(), case=False, na=False, regex=False)]

        if semester_available is not None:
            df["semester_available"] = pd.to_numeric(df["semester_available"], errors="coerce")
            df = df[df["semester_available"] == int(semester_available)]

        output_books = []
        for _, row in df.iterrows():
            output_books.append({
                "book_id": str(row.get("book_id", "")),
                "subject_code": str(row.get("subject_code", "")),
                "Title": str(row.get("Title", "")),
                "Price": float(row.get("Price", 0)) if pd.notna(row.get("Price")) else 0.0,
                "stock_quantity": int(row.get("stock_quantity", 0)) if pd.notna(row.get("stock_quantity")) else 0,
                "semester_available": int(row.get("semester_available", 0)) if pd.notna(row.get("semester_available")) else 0,
                "date_added": str(row.get("date_added", "")),
                "date_updated": str(row.get("date_updated", "")),
                "Program Related": str(row.get("Program Related", "")),
                "availability": str(row.get("availability", ""))
            })

        return output_books
    