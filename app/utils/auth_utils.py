# app/utils/auth_utils.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, Depends
import bcrypt
from fastapi.security import OAuth2PasswordBearer

# --- Configuration ---
SECRET_KEY = "supersecretkey" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 2

# --- Password Hashing ---
def hash_password(password: str) -> str:
    """Hash a plain text password."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(password: str, hashed: str) -> bool:
    """Check if a password matches its hashed version."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

# --- JWT Token Management ---
def create_access_token(data: dict) -> str:
    """Generate a JWT access token with an expiration time."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="NOT_USED")
 
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
 
        username: str = payload.get("sub")
        roles: list = payload.get("roles", [])
 
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token, no subject")
 
        return {"username": username, "roles": roles}
 
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
 
 
def require_roles(*required_roles):
    def role_checker(current_user=Depends(get_current_user)):
        user_roles = current_user["roles"]
 
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to access this resource."
            )
        return current_user
 
    return role_checker