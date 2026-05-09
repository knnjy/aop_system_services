from fastapi import FastAPI

from app.controllers.auth_controller import router as auth_router

app = FastAPI(title="AOP System Services")
app.include_router(auth_router)

from app.controllers.book_controller import router as book_router
from app.controllers.uniform_controller import router as uniform_router

app.include_router(book_router)
app.include_router(uniform_router)