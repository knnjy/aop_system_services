from fastapi import HTTPException

from app.dao.account_dao import AccountDAO
from app.dao.student_dao import StudentDAO
from app.dto.login import LoginRequest, LoginResponse


class AuthService:
    def __init__(self) -> None:
        self._account_dao = AccountDAO()
        self._student_dao = StudentDAO()

    def login(self, request: LoginRequest) -> LoginResponse:
        account = self._account_dao.validate_credentials(request.username, request.password)
        if account is None:
            raise HTTPException(status_code=401, detail="Invalid username or password")

        student_profile = self._student_dao.get_profile_by_student_id(request.username)
        if student_profile is None:
            raise HTTPException(
                status_code=404,
                detail="Authenticated account found, but no matching student profile was located",
            )

        return LoginResponse(
            account_id=int(account["account_id"]),
            username=account["Username"],
            role=account["role"],
            student_profile=student_profile,
        )
