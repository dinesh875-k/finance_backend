from datetime import UTC, datetime, timedelta

from sqlalchemy import or_

from app.auth import hash_password
from app.database import Base, SessionLocal, engine
from app.models import Transaction, User


# Dev seed script to populate the database with an admin user and some sample transactions. This is helpful for local development and testing so you have a known account to log in with and some data to work with on the dashboard right away.
# Purpose:
# - make sure the schema exists for local runs
# - create baseline users for login and role testing
# - create sample transactions so dashboard routes have data immediately
# This is for local/demo bootstrap, not production provisioning.
def seed() -> None:
    # Convenient for local startup and in migration-based deployments, schema creation should happen through migrations instead.
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Create the admin first because sample transactions below use this account as owner.
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@example.com",
                hashed_password=hash_password("admin123"),
                role="admin",
                is_active=True,
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print("Created admin user")
        else:
            print("Admin user already exists")

        # Seed a couple of non-admin accounts so role-based routes can be tested quickly.
        sample_users = [
            {
                "username": "analyst1",
                "email": "analyst@example.com",
                "password": "123456",
                "role": "analyst",
            },
            {
                "username": "viewer1",
                "email": "viewer@example.com",
                "password": "123456",
                "role": "viewer",
            },
        ]

        for user_data in sample_users:
            # Check both username and email so the seed stays safe with unique constraints.
            existing_user = db.query(User).filter(
                or_(
                    User.username == user_data["username"],
                    User.email == user_data["email"],
                )
            ).first()

            if existing_user:
                print(f"User {user_data['username']} already exists")
                continue

            user = User(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=hash_password(user_data["password"]),
                role=user_data["role"],
                is_active=True,
            )
            db.add(user)
            print(f"Created user {user_data['username']}")

        db.commit()

        # Refresh admin in case it was just created earlier in this run.
        db.refresh(admin)

        now = datetime.now(UTC)
        sample_transactions = [
            {
                "amount": 5000,
                "type": "income",
                "category": "salary",
                "days_ago": 10,
                "notes": "seed: monthly salary",
            },
            {
                "amount": 2000,
                "type": "expense",
                "category": "food",
                "days_ago": 5,
                "notes": "seed: grocery and dining",
            },
            {
                "amount": 1500,
                "type": "expense",
                "category": "travel",
                "days_ago": 2,
                "notes": "seed: local travel",
            },
            {
                "amount": 3000,
                "type": "income",
                "category": "freelance",
                "days_ago": 1,
                "notes": "seed: freelance payout",
            },
        ]

        # Seed transactions individually instead of relying on a total-count check and that way one existing transaction does not block the whole seed set.
        for txn_data in sample_transactions:
            txn_date = now - timedelta(days=txn_data["days_ago"])

            existing_txn = db.query(Transaction).filter(
                Transaction.created_by == admin.id,
                Transaction.amount == txn_data["amount"],
                Transaction.type == txn_data["type"],
                Transaction.category == txn_data["category"],
                Transaction.date == txn_date,
                Transaction.notes == txn_data["notes"],
            ).first()

            if existing_txn:
                print(f"Transaction already exists for {txn_data['category']}")
                continue

            txn = Transaction(
                amount=txn_data["amount"],
                type=txn_data["type"],
                category=txn_data["category"],
                date=txn_date,
                notes=txn_data["notes"],
                created_by=admin.id,
            )
            db.add(txn)
            print(f"Created transaction for {txn_data['category']}")

        db.commit()
        print("Database seeding completed successfully")

    except Exception as exc:
        db.rollback()
        print(f"Seeding failed: {exc}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed()