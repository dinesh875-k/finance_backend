from pydantic import BaseModel, field_validator, EmailStr
from typing import Optional
from datetime import datetime
from typing import Literal


# User-side request/response shapes These schemas control what the API accepts and what it returns so basically In a real-time project, this gives the frontend a stable contract.

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "viewer"

    @field_validator("role")
    @classmethod
    def validate_role(cls, value):
        # Keeps role assignment inside expected system roles which Prevents random values from being written into auth logic.
        allowed = ["viewer", "analyst", "admin"]
        if value.lower() not in allowed:
            raise ValueError(f"Role must be one of: {', '.join(allowed)}")
        return value.lower()

    @field_validator("username")
    @classmethod
    def validate_username(cls, value):
        # Basic username floor which Stops empty or too-short usernames from reaching DB layer.
        if len(value) < 3:
            raise ValueError("Username must be at least 3 characters")
        return value


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

    # Lets Pydantic read data straight from SQLAlchemy model objects.
    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


# Admin-only update payloads and These are used when changing role or status from management endpoints.
class UserRoleUpdate(BaseModel):
    role: Literal["viewer", "analyst", "admin"]


class UserStatusUpdate(BaseModel):
    is_active: bool


class UserListResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Transaction schemas.
# These define the payload shape for financial records flowing between frontend, API layer, and database.
class TransactionCreate(BaseModel):
    amount: float
    type: str
    category: str
    date: datetime
    notes: Optional[str] = None

    @field_validator("type")
    @classmethod
    def validate_type(cls, value):
        # Keeps transaction direction normalized and useful for analytics, aggregation, and dashboard summaries.
        if value.lower() not in ["income", "expense"]:
            raise ValueError("Type must be either 'income' or 'expense'")
        return value.lower()

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value):
        # Rejects non-positive values before they hit business logic and Rounded here so downstream storage and reporting stay consistent.
        if value <= 0:
            raise ValueError("Amount must be greater than zero")
        return round(value, 2)


class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    type: Optional[str] = None
    category: Optional[str] = None
    date: Optional[datetime] = None
    notes: Optional[str] = None

    @field_validator("type")
    @classmethod
    def validate_type(cls, value):
        # PATCH schema, so fields may be omitted and alidation only runs when the field is actually sent.
        if value is not None and value.lower() not in ["income", "expense"]:
            raise ValueError("Type must be either 'income' or 'expense'")
        return value.lower() if value else value

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value):
        # Same idea here for partial updates so current logic works for normal positive values but `if value` is weaker than `if value is not None`.
        if value is not None and value <= 0:
            raise ValueError("Amount must be greater than zero")
        return round(value, 2) if value else value


class TransactionResponse(BaseModel):
    id: int
    amount: float
    type: str
    category: str
    date: datetime
    notes: Optional[str]
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}



class RecentActivityResponse(BaseModel):
    id: int
    amount: float
    type: str
    category: str
    date: datetime
    notes: str | None
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("/recent-activity", response_model=list[RecentActivityResponse])
def get_recent_activity(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["analyst", "admin"]))
):
    return (
        db.query(Transaction)
        .order_by(Transaction.date.desc(), Transaction.created_at.desc())
        .limit(limit)
        .all()
    )