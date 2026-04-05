from app.database import SessionLocal, engine, Base
from app.models import User, Transaction
from app.auth import hash_password
from datetime import datetime, timedelta


def seed():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        admin = db.query(User).filter(User.username == "admin").first()

        if not admin:
            admin = User(
                username="admin",
                email="admin@example.com",
                hashed_password=hash_password("admin123"),
                role="admin"
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print("Admin user created")
        else:
            print("Admin already exists")

        sample_users = [
            {
                "username": "analyst1",
                "email": "analyst@example.com",
                "password": "123456",
                "role": "analyst"
            },
            {
                "username": "viewer1",
                "email": "viewer@example.com",
                "password": "123456",
                "role": "viewer"
            }
        ]

        for u in sample_users:
            exists = db.query(User).filter(User.username == u["username"]).first()
            if not exists:
                user = User(
                    username=u["username"],
                    email=u["email"],
                    hashed_password=hash_password(u["password"]),
                    role=u["role"]
                )
                db.add(user)
                print(f"User {u['username']} created")
            else:
                print(f"User {u['username']} already exists")

        db.commit()

        now = datetime.utcnow()

        transactions = [
            {"amount": 5000, "type": "income", "category": "salary", "days_ago": 10},
            {"amount": 2000, "type": "expense", "category": "food", "days_ago": 5},
            {"amount": 1500, "type": "expense", "category": "travel", "days_ago": 2},
            {"amount": 3000, "type": "income", "category": "freelance", "days_ago": 1}
        ]

        for t in transactions:
            txn = Transaction(
                amount=t["amount"],
                type=t["type"],
                category=t["category"],
                date=now - timedelta(days=t["days_ago"]),
                notes=f"Sample {t['category']} transaction",
                created_by=admin.id
            )
            db.add(txn)

        db.commit()
        print("Sample transactions added")
        print("Database seeding completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"Seeding failed: {e}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed()