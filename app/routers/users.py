from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import RoleChecker, create_access_token, hash_password, verify_password
from app.database import get_db
from app.models import User
from app.schemas import (
    Token,
    UserAdminResponse,
    UserCreate,
    UserResponse,
    UserRoleUpdate,
    UserStatusUpdate,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"])),
):
    # This endpoint is admin-only and That makes sense for an internal system where accounts are provisioned by staff.
    existing = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()

    # Block duplicate usernames/emails before insert.
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already registered",
        )

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role=user_data.role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # Login flow:
    # 1. find user by username
    # 2. verify password hash
    # 3. reject inactive accounts
    # 4. issue JWT for later requests
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    token = create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(RoleChecker(["viewer", "analyst", "admin"])),
):
    # Returns the authenticated user's own profile and the frontend usually calls this after login to build role-aware UI.
    return current_user


@router.get("/", response_model=list[UserAdminResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"])),
):
    # Admin directory endpoint and sorted newest first so recent account changes are easier to inspect.
    return db.query(User).order_by(User.created_at.desc()).all()


@router.patch("/{user_id}/role", response_model=UserAdminResponse)
def update_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"])),
):
    # Used by admin controls to change who can view, analyze, or manage the system.
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Protect the system from ending up with zero active admins.
    active_admin_count = db.query(User).filter(
        User.role == "admin",
        User.is_active.is_(True),
    ).count()

    if user.role == "admin" and payload.role != "admin" and active_admin_count == 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove the last active admin",
        )

    user.role = payload.role
    db.commit()
    db.refresh(user)
    return user


@router.patch("/{user_id}/status", response_model=UserAdminResponse)
def update_user_status(
    user_id: int,
    payload: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"])),
):
    # Soft deactivate instead of deleting the account and this keeps historical ownership and audit references intact.
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Same safety rule here: do not allow the last active admin to be disabled.
    active_admin_count = db.query(User).filter(
        User.role == "admin",
        User.is_active.is_(True),
    ).count()

    if user.role == "admin" and user.is_active and not payload.is_active and active_admin_count == 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate the last active admin",
        )

    user.is_active = payload.is_active
    db.commit()
    db.refresh(user)
    return user