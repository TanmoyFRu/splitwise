from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)


class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"
    id: Optional[int] = Field(default=None, primary_key=True)
    description: str
    total_amount: int
    deleted_at: Optional[datetime] = Field(default=None)


class Ledger(SQLModel, table=True):
    __tablename__ = "ledgers"
    id: Optional[int] = Field(default=None, primary_key=True)
    from_user_id: int = Field(foreign_key="users.id", index=True)
    to_user_id: int = Field(foreign_key="users.id", index=True)
    amount: int
    transaction_id: int = Field(foreign_key="transactions.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
