import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Use SQLite for local development, Supabase in production
if os.getenv("VERCEL_ENV"):
    # Get Database URL from environment
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is required in production")
    
    # Supabase requires SSL
    SQLALCHEMY_DATABASE_URL = f"{DATABASE_URL}?sslmode=require"
else:
    # Local development using SQLite
    SQLALCHEMY_DATABASE_URL = "sqlite:///./physical_hyperlinks.db"

# Only use check_same_thread=False for SQLite
connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}

# Create engine with connection pooling for Supabase
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True  # Verify connection before using
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()