from fastapi import FastAPI

from app.controllers.auth_controller import router as auth_router
from app.controllers.book_controller import router as book_router
from app.controllers.uniform_controller import router as uniform_router
from app.controllers.book_catalog_controller import router as book_catalog_router
# FastAPI App Instance
app = FastAPI(title="AOP System Services")

# Include Routers
app.include_router(auth_router)
app.include_router(book_router)
app.include_router(uniform_router)
app.include_router(book_catalog_router)
@app.get("/")
def home():
    return {"details": "AOP API is Running"}
