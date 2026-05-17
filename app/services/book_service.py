from http.client import HTTPException
from datetime import datetime
from turtle import pd

from app.dao.book_dao import BookDAO
from app.dto.catalog_dto import BookDTO

class BookService:
    def __init__(self):
        self._book_dao = BookDAO()
        
    def list_books(self):
        result = self._book_dao.get_all()
        # Only return rows where is_deleted == "false"
        active_books = [book for book in result if book.is_deleted == "False"]
        return active_books

    def add_new_book(self, order_form: BookDTO):
        # Auto-generate book_id if not provided
        
        if not order_form.book_id:
            order_form.book_id = self._book_dao.get_next_book_id()
        else:
            # check if book_id already exists
            if self._book_dao.get_by_book_id(order_form.book_id):
                raise HTTPException(status_code=409, detail=f"Book with ID {order_form.book_id} already exists")
        
        # Always set timestamps to current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        order_form.date_added = current_date
        order_form.date_updated = current_date
        
        # Set default values if not provided
        if not order_form.availability:
            order_form.availability = "available"
        if order_form.is_deleted is None:
            order_form.is_deleted = False
        
        # Save the book to CSV
        saved_book = self._book_dao.save_book(order_form)

        return {
            "message": "Book added successfully",
            "book_id": saved_book.book_id,
            "title": saved_book.title,
            "subject_code": saved_book.subject_code
        }
    
    def book_stock_update(self):
        return self._book_dao.get_stock_by_subject_code()
    
    def soft_delete_book(self, book_id: str):
        book = self._book_dao.get_by_book_id(book_id)
        if not book: 
            return HTTPException(status_code=404, detail=f"Book with id {book_id} not found")
            
        book.date_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        book.is_deleted = "True"
        self._book_dao.update_book_flag(book)

        return {"message": f"Book {book_id} deleted successfully"}

    #Book filtering
    def filter_books(self, program_related=None, title=None, semester_available=None):
        books = self._book_dao.get_all()

        books = [b for b in books if b.is_deleted.strip().lower() == "false"]

        if program_related:
            books = [b for b in books if program_related.lower() in b.program_related.lower()]
        if title:
            books = [b for b in books if title.lower() in b.title.lower()]
        if semester_available is not None:
            books = [b for b in books if b.semester_available == int(semester_available)]

        return books
    
    def update_book(self, book_id: str, updated_data: dict):
        book = self._book_dao.get_by_book_id(book_id)
        if not book:
            raise HTTPException(status_code=404, detail=f"Book {book_id} not found")

        # Apply updates to DTO
        for column, value in updated_data.items():
            if hasattr(book, column) and column != "book_id":
                setattr(book, column, value)

        # Always refresh timestamp with date + time
        book.date_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Persist changes
        self._book_dao.update(book)

        return {"message": f"Book {book_id} updated successfully!"}