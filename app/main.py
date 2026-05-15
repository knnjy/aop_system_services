from fastapi import FastAPI
from app.controllers.auth_controller import router as auth_router
from app.controllers.uniform_catalog_controller import router as uniform_router
from app.controllers.book_catalog_controller import router as book_catalog_router
from app.controllers.order_controller import router as order_router
<<<<<<< HEAD

=======
>>>>>>> f82d83d (added soft delete cancel order endpoint)
# FastAPI App Instance
app = FastAPI(title="AOP System Services")

# Include Routers
app.include_router(auth_router)
app.include_router(uniform_router)
app.include_router(book_catalog_router)
app.include_router(order_router)
<<<<<<< HEAD

=======
>>>>>>> f82d83d (added soft delete cancel order endpoint)
@app.get("/")
def home():
    return {"details": "AOP API is Running"}
