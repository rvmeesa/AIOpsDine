# db/connection.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DB_URL", "sqlite:///./restaurant.db")
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency to get a new DB session.
    Used inside FastAPI endpoints later.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
