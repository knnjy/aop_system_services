from typing import Any, Dict

from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    account_id: int
    username: str
    role: str
    student_profile: Dict[str, Any]
