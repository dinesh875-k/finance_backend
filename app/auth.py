from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User

# Used to sign and verify JWT tokens.
# In a real deployment this should come from environment variables,
# not be hardcoded in source.
SECRET_KEY = "zoevyn@finance123456"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context.bcrypt is standard here since passwords should never be stored directly.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# FastAPI will read bearer token from Authorization header.
# tokenUrl points Swagger/OpenAPI login flow to /users/login.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def hash_password(password: str) -> str:
    # Runs during registration or password reset and The DB stores only the hash, never the raw password.
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    # Runs during login and Compares the incoming password with the stored bcrypt hash.
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict) -> str:
    # Creates the JWT that the frontend sends back on later requests which is used for authentication in a real-time finance app:
    # login -> token issued -> token attached to protected API calls.
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# This dependency runs before protected routes and It acts like the gatekeeper for endpoints that need an authenticated user.
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        # Decode token and extract identity from the "sub" claim, If token is expired, tampered with, or malformed it raises JWTError and the request is rejected.
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        if username is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # Once token is valid, pull the current user from DB then DB lookup matters because the token alone may still be valid and even if the account was later disabled.
    user = db.query(User).filter(User.username == username).first()

    # This line currently mixes two cases together:
    # 1. user does not exist
    # 2. user exists but is inactive
    # which basically checks inactive users return 401 here instead of 403.
    if user is None or not user.is_active:
        raise credentials_exception

    # Redundant check. At this point user is already confirmed not None.
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    # This block is also unreachable because inactive users were already rejected above.
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )

    # If this returns successfully, downstream route handlers receive the fully loaded User object and can use role, id, or active status.
    return user


class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)):
        # This is the second layer after authentication.
        # First we confirm who the user is, then we confirm whether that user is allowed to touch this route.
        # Example in a real-time finance system:
        # - viewer can inspect dashboards
        # - analyst can work with operational data
        # - admin can manage users and access control
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        return user