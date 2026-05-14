from http.client import HTTPException
from datetime import datetime

from app.dao.book_dao import BookDAO
from app.dao.orders_dao import OrderDAO
from app.dto.catalog_dto import BookDTO


class BookService:
    def __init__(self):
        self._book_dao = BookDAO()

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