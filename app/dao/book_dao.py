from typing import List, Optional

import pandas as pd

from app.utils.csv_loader import load_csv
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
