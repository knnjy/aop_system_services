from fastapi import HTTPException

from app.dao.account_dao import AccountDAO
from app.dao.student_dao import StudentDAO
from app.dto.auth_dto import LoginRequest, LoginResponse
from app.utils.auth_utils import (
    create_access_token
)

class AuthService:
    def __init__(self) -> None:
        self._account_dao = AccountDAO()
        self._student_dao = StudentDAO()

    def get_student_data(self, id:str):
        account_data = self._student_dao.get_profile_by_student_id(id)
        if account_data is None:
            raise HTTPException(status_code=404, detail="No matching student data located")
        
        return account_data
        
    def authenticate_user(self, request: LoginRequest):
        account = self._account_dao.validate_credentials(
            request.username,
            request.password
        )

        if account is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )

        student_profile = self.get_student_data(request.username)

        token_data = LoginResponse(
            account_id=int(account["account_id"]),
            username=account["Username"],
            role=account["role"],
            user_data=student_profile,
        )

        token = create_access_token(token_data.model_dump())

        return {
            "access_token": token,
            "token_type": "bearer"
        }
    

