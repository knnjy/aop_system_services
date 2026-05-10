from fastapi import FastAPI

# Import Routers
from app.controllers.book_controller import router as book_router
from app.controllers.uniform_controller import router as uniform_router

# FastAPI App Instance
app = FastAPI(
    title="AOP System Services",
    version="1.0.0",
    description="Catalog Management Service Parts Distribution"
)

# Include Routers
app.include_router(book_router)
app.include_router(uniform_router)

@app.get("/")
def root():
    return {
        "endpoints": [
            "/api/books/update-book/{book_id}",       # Update Books
            "/api/uniforms/delete-uniform/{uniform_id}"  # Delete Uniform Data
        ]
    }

