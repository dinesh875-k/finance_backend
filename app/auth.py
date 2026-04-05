import os
from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User


# JWT signing settings and SECRET_KEY must come from environment/config in real deployments.
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing config and raw passwords should never be stored directly in the database.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Reads bearer token from Authorization header and FastAPI docs use tokenUrl to know which login endpoint issues tokens.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


# Used when creating a user or updating a password.
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# Used during login to compare the submitted password with the stored hash.
def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# Creates the JWT sent back after a successful login so the frontend includes this token on later protected requests.
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# Main auth dependency shared by protected route and runtime flow:
# - read bearer token
# - decode it
# - get username from the sub claim
# - load current user from DB
# - reject missing or inactive accounts
# - return the User model instance to the route/dependency chain
# The DB lookup matters because a user might still hold an unexpired token after being disabled.
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception

    # Keep auth failure and disabled-account failure separate so the missing/invalid identity is 401. Known but inactive account is 403.
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    return user


# Reusable role gate layered on top of get_current_user and This keeps authentication and authorization as separate steps.
class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)) -> User:
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )
        return user