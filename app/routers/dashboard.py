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
    # Summary endpoint for top-level dashboard cards.
    # This is the kind of route the frontend can call on page load to populate total income, total expense, net balance, and count and optional date filters let the UI switch between overall view, monthly range, custom range, or reporting windows.

    base_query = db.query(Transaction)
    if start_date:
        base_query = base_query.filter(Transaction.date >= start_date)
    if end_date:
        base_query = base_query.filter(Transaction.date <= end_date)

    # Split the same base dataset into income and expense totals and coalesce avoids None when no matching rows exist.
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


@router.get("/recent-activity")
def get_recent_activity(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["analyst", "admin"]))
):
    # Feed endpoint for latest transaction activity which is useful for dashboard tables, activity streams, or audit-style recent lists and ordered first by business date, then by record creation time so latest relevant finance events appear first.
    records = (
        db.query(Transaction)
        .order_by(Transaction.date.desc(), Transaction.created_at.desc())
        .limit(limit)
        .all()
    )

    # Manual shaping keeps response small and avoids leaking unwanted ORM fields.
    return [
        {
            "id": txn.id,
            "amount": round(txn.amount, 2),
            "type": txn.type,
            "category": txn.category,
            "date": txn.date,
            "notes": txn.notes,
            "created_by": txn.created_by,
            "created_at": txn.created_at
        }
        for txn in records
    ]


@router.get("/category-breakdown")
def get_category_breakdown(
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["analyst", "admin"])),
    type: Optional[str] = Query(None, description="Filter by income or expense")
):
    # Breakdown endpoint for pie charts, grouped tables, and spend/income analysis so that analysts/admins get access because this is a more detailed cut of the data than the simple viewer summary.
    query = db.query(
        Transaction.category,
        Transaction.type,
        func.sum(Transaction.amount).label("total"),
        func.count(Transaction.id).label("count")
    )

    if type:
        # Narrow results to one side of the ledger when the UI requests it.
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
    # Trend endpoint for charts which groups records by month and transaction type so the frontend can render, income vs expense movement across time which current current query uses strftime and  works well on SQLite.
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