from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import RoleChecker
from app.database import get_db
from app.models import Transaction, User
from app.schemas import (
    CategoryBreakdownResponse,
    DashboardSummaryResponse,
    MonthlyTrendResponse,
    RecentActivityResponse,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["viewer", "analyst", "admin"])),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
):
    # Dashboard card endpoint and The frontend uses this for totals like income, expenses, balance, and record count.
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date cannot be greater than end_date",
        )

    base_query = db.query(Transaction)

    # Apply optional date filters so the same endpoint can power global, monthly, or custom-range views.
    if start_date is not None:
        base_query = base_query.filter(Transaction.date >= start_date)
    if end_date is not None:
        base_query = base_query.filter(Transaction.date <= end_date)

    total_income = base_query.filter(Transaction.type == "income").with_entities(
        func.coalesce(func.sum(Transaction.amount), 0)
    ).scalar()

    total_expenses = base_query.filter(Transaction.type == "expense").with_entities(
        func.coalesce(func.sum(Transaction.amount), 0)
    ).scalar()

    return {
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "net_balance": round(total_income - total_expenses, 2),
        "transaction_count": base_query.count(),
    }


@router.get("/recent-activity", response_model=list[RecentActivityResponse])
def get_recent_activity(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["analyst", "admin"])),
):
    # Feed endpoint for the latest transaction records and useful for dashboard tables or an activity stream widget.
    return (
        db.query(Transaction)
        .order_by(Transaction.date.desc(), Transaction.created_at.desc())
        .limit(limit)
        .all()
    )


@router.get("/category-breakdown", response_model=list[CategoryBreakdownResponse])
def get_category_breakdown(
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["analyst", "admin"])),
    transaction_type: Optional[str] = Query(None, description="Filter by income or expense"),
):
    # Aggregates transactions by category and type and also this is the dataset behind pie charts, grouped bars, and summary tables.
    query = db.query(
        Transaction.category,
        Transaction.type,
        func.sum(Transaction.amount).label("total"),
        func.count(Transaction.id).label("count"),
    )

    if transaction_type is not None:
        if transaction_type not in {"income", "expense"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="transaction_type must be either 'income' or 'expense'",
            )
        query = query.filter(Transaction.type == transaction_type)

    results = query.group_by(Transaction.category, Transaction.type).all()

    return [
        {
            "category": row.category,
            "type": row.type,
            "total": round(row.total, 2),
            "count": row.count,
        }
        for row in results
    ]


@router.get("/monthly-trends", response_model=list[MonthlyTrendResponse])
def get_monthly_trends(
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["analyst", "admin"])),
):
    # Monthly rollup for trend charts and current implementation uses SQLite-style strftime, so it is DB-dialect specific.
    results = (
        db.query(
            func.strftime("%Y-%m", Transaction.date).label("month"),
            Transaction.type,
            func.sum(Transaction.amount).label("total"),
        )
        .group_by("month", Transaction.type)
        .order_by("month")
        .all()
    )

    return [
        {
            "month": row.month,
            "type": row.type,
            "total": round(row.total, 2),
        }
        for row in results
    ]