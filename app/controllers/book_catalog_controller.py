# from fastapi import APIRouter

# router = APIRouter(prefix="/api/books")

# # Get all the list of book on book_data
# @router.get("/list-books")
# def list_books():
#     return {}

# # Filter book by Program_related, Title, & semester available
# @router.get("/filter-books")
# def filter_books():
#     return {}

# # Add new book data on books_data
# @router.post("add-book")
# def add_book():
#     return {}

# # Update book data on books_data
# @router.post("update-book/{book_code}")
# def update_book():
#     return {}

# # Soft delete book on books_data
# @router.delete("delete-book/{book_code}")
# def delete_book():
#     return {}


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

