from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse, Token
from app.auth import hash_password, verify_password, create_access_token, RoleChecker
from app.schemas import UserRoleUpdate, UserStatusUpdate, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    # Registration is protected here, which means only an admin can create accounts. That usually fits internal tools, dashboards, or staff-managed finance systems.
    existing = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()

    # Stops duplicate identity records before insert and This matters because users are later resolved by username during auth.
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already registered"
        )

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role=user_data.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Login starts by locating the username in DB and in Real-time systems typically do this on every fresh sign-in then return a token for subsequent stateless API access.
    user = db.query(User).filter(User.username == form_data.username).first()

    # Reject invalid username/password combination.
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Account can exist but still be blocked from using the system.
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )

    # Token includes subject and role That allows downstream auth layers to identify the user quickly.
    token = create_access_token(data={"sub": user.username, "role": user.role})

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(RoleChecker(["viewer", "analyst", "admin"]))):
    # Returns the authenticated user's own profile which is useful for frontend bootstrapping after login: role-aware UI, profile chips, access-sensitive screens, etc.
    return current_user


@router.get("/", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    # Admin-only user directory and ordered newest first so recent account activity/creation is easier to inspect.
    return db.query(User).order_by(User.created_at.desc()).all()


@router.patch("/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    # Used by admin control panels to shift permissions in production.
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.role = payload.role
    db.commit()
    db.refresh(user)
    return user


@router.patch("/{user_id}/status", response_model=UserResponse)
def update_user_status(
    user_id: int,
    payload: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    # Soft activation/deactivation flow is Better than deleting accounts because historical ownership, audit trails, and finance records may still depend on this user.
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_active = payload.is_active
    db.commit()
    db.refresh(user)
    return user