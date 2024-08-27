import os

from sqlmodel import create_engine

DATABASE_URL = (
    os.getenv("POSTGRES_URL") or os.getenv("DATABASE_URL") or "sqlite:///./splitwise.db"
)

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://")

engine = create_engine(DATABASE_URL, echo=True)
