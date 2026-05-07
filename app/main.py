from fastapi import FastAPI

from app.controllers.auth_controller import router as auth_router

app = FastAPI(title="AOP System Services")
app.include_router(auth_router)
