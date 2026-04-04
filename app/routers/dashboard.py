from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models import Transaction, User
from app.auth import RoleChecker

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["viewer", "analyst", "admin"])),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    #Returns total income, total expenses, and net balance  

    base_query = db.query(Transaction)
    if start_date:
        base_query = base_query.filter(Transaction.date >= start_date)
    if end_date:
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
        "transaction_count": base_query.count()
    }


@router.get("/category-breakdown")
def get_category_breakdown(
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["analyst", "admin"])),
    type: Optional[str] = Query(None, description="Filter by income or expense")
):
    # Group totals by category. Analysts and admins only — viewers see the summary.
    query = db.query(
        Transaction.category,
        Transaction.type,
        func.sum(Transaction.amount).label("total"),
        func.count(Transaction.id).label("count")
    )

    if type:
        query = query.filter(Transaction.type == type)

    results = query.group_by(Transaction.category, Transaction.type).all()

    return [
        {
            "category": r.category,
            "type": r.type,
            "total": round(r.total, 2),
            "count": r.count
        }
        for r in results
    ]


@router.get("/monthly-trends")
def get_monthly_trends(
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["analyst", "admin"]))
):
    # Monthly income vs expense trends.

    results = db.query(
        func.strftime("%Y-%m", Transaction.date).label("month"),
        Transaction.type,
        func.sum(Transaction.amount).label("total")
    ).group_by("month", Transaction.type).order_by("month").all()

    return [
        {
            "month": r.month,
            "type": r.type,
            "total": round(r.total, 2)
        }
        for r in results
    ]