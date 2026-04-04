from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./finance.db"
#connecting to the database
engine= create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

#creating a session for handling database operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#creating a base class for our models to inherit from and define the structure of our database tables
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()