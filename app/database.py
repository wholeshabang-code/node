import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Use SQLite for local development, external database for production
if os.getenv("VERCEL_ENV"):
    # Format DATABASE_URL for production database
    # You'll need to set this in Vercel environment variables
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
else:
    # Local development using SQLite
    SQLALCHEMY_DATABASE_URL = "sqlite:///./physical_hyperlinks.db"

connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()