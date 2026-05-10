from email.header import Header
from http.client import HTTPException

from app.utils.auth_utils import verify_token
from fastapi import APIRouter

from app.dto.auth_dto import LoginRequest, LoginResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["Auth"])
_auth_service = AuthService()


@router.post("/login")
def login(request: LoginRequest):
    return _auth_service.authenticate_user(request)

@router.get("/get-student-data/{id}")
def get_data(id: str):
    response = _auth_service.get_student_data(id)
    return response

@router.get("/protected")
def protected(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = authorization.split(" ")[1]
    user_data = verify_token(token)
    return {"message": "Access granted", "user": user_data}

