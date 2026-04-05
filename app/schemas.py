from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


# User Schemas 

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "viewer"

    @field_validator("role")
    @classmethod
    def validate_role(cls, value):
        allowed = ["viewer", "analyst", "admin"]
        if value.lower() not in allowed:
            raise ValueError(f"Role must be one of: {', '.join(allowed)}")
        return value.lower()

    @field_validator("username")
    @classmethod
    def validate_username(cls, value):
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

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str 


# Transaction Schemas 

class TransactionCreate(BaseModel):
    amount: float
    type: str
    category: str
    date: datetime
    notes: Optional[str] = None

    @field_validator("type")
    @classmethod
    def validate_type(cls, value):
        if value.lower() not in ["income", "expense"]:
            raise ValueError("Type must be either 'income' or 'expense'")
        return value.lower()

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value):
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
        if value is not None and value.lower() not in ["income", "expense"]:
            raise ValueError("Type must be either 'income' or 'expense'")
        return value.lower() if value else value

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value):
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