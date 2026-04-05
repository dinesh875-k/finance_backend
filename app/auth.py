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


# Secret used to sign JWTs and in production this must come from environment/config, not source control.
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing setup as bcrypt is standard for user passwords and keeps raw passwords out of storage.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Reads bearer tokens from Authorization headers and fastAPI docs also use this token URL for the auth flow.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


# Called when a user is created or when a password is changed.
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# Called during login to compare the plain password with the stored hash.
def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# Builds the JWT sent back after login and the frontend stores this token and sends it on later protected requests.
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# Core auth dependency used by protected routes flow:
# 1. read bearer token
# 2. decode JWT
# 3. load current user from DB
# 4. reject disabled or missing accounts
# 5. return full user object to the route
# This DB lookup matters because a still-valid token should not bypass later account deactivation.
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

    # Keep invalid-token and inactive-account cases separate.
    # Missing/invalid identity is 401, known but disabled account is 403.
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    return user


# Simple reusable permission gate and routes wrap this around get_current_user so auth and role checks stay separate.
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