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
    
    # Parse and modify the connection URL to force IPv4
    # Example: postgresql://user:pass@db.xxx.supabase.co:5432/postgres
    if "supabase" in DATABASE_URL:
        # Add required parameters for Supabase
        DATABASE_URL = f"{DATABASE_URL}?sslmode=require&host_rewrite=true"
    
    SQLALCHEMY_DATABASE_URL = DATABASE_URL
else:
    # Local development using SQLite
    SQLALCHEMY_DATABASE_URL = "sqlite:///./physical_hyperlinks.db"

# Connection arguments
connect_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False
elif "supabase" in SQLALCHEMY_DATABASE_URL:
    connect_args.update({
        "connect_timeout": 60,  # 60 seconds timeout
    })

# Create engine with optimized settings for serverless
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,  # Enable connection health checks
    pool_size=1,  # Minimize connections for serverless
    max_overflow=0  # Disable overflow connections
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()