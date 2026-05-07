from fastapi import APIRouter

from app.dto.login import LoginRequest, LoginResponse
from app.services.auth_service import AuthService

router = APIRouter()
_auth_service = AuthService()

@router.get("/")
def home():
    return {"details": "API is Running"}

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest) -> LoginResponse:
    return _auth_service.login(request)
