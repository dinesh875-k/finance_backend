from fastapi import FastAPI

from app.database import engine, Base
from app.routers import users, transactions, dashboard

app = FastAPI(title="Finance Management API")

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(users.router)
app.include_router(transactions.router)
app.include_router(dashboard.router)

@app.get("/")
def root():
    return {"message": "Finance API is running "}