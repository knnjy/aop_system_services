from app.dao.student_dao import StudentDAO
from fastapi import APIRouter

from app.dto.login import LoginRequest, LoginResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth")
_auth_service = AuthService()

@router.get("/")
def home():
    return {"details": "API is Running"}

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest) -> LoginResponse:
    return _auth_service.login(request)

_acount_dao = StudentDAO()
@router.get("/get-student-data/{id}")
def get_data(id: str):
    response = _auth_service.get_student_data(id)
    return response