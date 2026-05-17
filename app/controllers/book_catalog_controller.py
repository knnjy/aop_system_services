from app.dto.catalog_dto import BookDTO
from app.services.book_service import BookService
from fastapi import APIRouter
import pandas as pd
from datetime import datetime
from pydantic import BaseModel
from app.dao.book_dao import BookDAO

router = APIRouter(prefix="/api/books")

_book_service = BookService()

@router.get("/filter-books")
def filter_books_route(program_related: str = None, title: str = None, semester_available: int = None):
    return _book_service.filter_books(program_related, title, semester_available)

# Soft delete book on books_data
@router.delete("/delete-book/{book_id}")
def delete_book(book_id: str):
    return _book_service.soft_delete_book(book_id)

@router.get("/list-books")
def list_books():
    return _book_service.list_books()

@router.post("/add-book")
def add_book(book: BookDTO):
    return _book_service.add_new_book(book)

@router.get("/get-book-stock")
def get_stock():
    return _book_service.book_stock_update()

@router.put("/update-book/{book_id}")
def update_book(book_id: str, updated_data: dict):
    return _book_service.update_book(book_id=book_id, updated_data=updated_data)