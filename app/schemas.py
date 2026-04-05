from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, field_validator


# Request body for admin-created users. This is what the API accepts when a new account is created.
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Literal["viewer", "analyst", "admin"] = "viewer"

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        # Trim whitespace first so accidental spaces do not create bad usernames.
        value = value.strip()
        if len(value) < 3:
            raise ValueError("Username must be at least 3 characters")
        return value


# Basic user payload returned to authenticated users and used for /users/me and similar profile-style endpoints.
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime

    # Allows Pydantic to serialize SQLAlchemy model instances directly.
    model_config = {"from_attributes": True}


# Admin-facing user response and Kept separate so admin endpoints can evolve independently if needed.
class UserAdminResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# JWT token returned after successful login.
class Token(BaseModel):
    access_token: str
    token_type: str


# Payload used when an admin changes a user's role.
class UserRoleUpdate(BaseModel):
    role: Literal["viewer", "analyst", "admin"]


# Payload used when an admin activates or deactivates a user.
class UserStatusUpdate(BaseModel):
    is_active: bool


# Request body for creating a transaction and This is the shape the frontend sends when a new finance record is added.
class TransactionCreate(BaseModel):
    amount: float
    type: Literal["income", "expense"]
    category: str
    date: datetime
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value: float) -> float:
        # Reject zero or negative amounts before they reach the DB layer.
        if value <= 0:
            raise ValueError("Amount must be greater than zero")
        # Round once here so the rest of the app works with a stable numeric value.
        return round(value, 2)


# PATCH-style update schema as all fields are optional because the client may update only one part of a record.
class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    type: Optional[Literal["income", "expense"]] = None
    category: Optional[str] = None
    date: Optional[datetime] = None
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value: Optional[float]) -> Optional[float]:
        # Only validate when the field is actually provided in the PATCH payload.
        if value is not None and value <= 0:
            raise ValueError("Amount must be greater than zero")
        return round(value, 2) if value is not None else value


# Full transaction response returned by the API.
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


# Lightweight response for the dashboard activity feed.
class RecentActivityResponse(BaseModel):
    id: int
    amount: float
    type: str
    category: str
    date: datetime
    notes: Optional[str]
    created_by: int
    created_at: datetime

    model_config = {"from_attributes": True}


# Summary card response for dashboard totals.
class DashboardSummaryResponse(BaseModel):
    total_income: float
    total_expenses: float
    net_balance: float
    transaction_count: int


# Response for grouped category totals used in charts/tables.
class CategoryBreakdownResponse(BaseModel):
    category: str
    type: str
    total: float
    count: int


# Response for month-by-month chart data.
class MonthlyTrendResponse(BaseModel):
    month: str
    type: str
    total: float