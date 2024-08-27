from datetime import datetime
from typing import List

from sqlmodel import Session, text

from core import engine
from model import Transaction, User
from schema import Balance, CreateTransaction, TransactionResponse, UserSplit
from util import convert_transaction_to_ledger


def create_user(user_email: str) -> dict:
    new_user = User(email=user_email)
    with Session(engine) as session:
        try:
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            return {"id": new_user.id, "email": new_user.email}
        except Exception:
            session.rollback()
            raise ValueError("Email already registered")


def get_user_balance(user_id: int) -> List[Balance]:
    with Session(engine) as session:
        query = text(
            """
            SELECT
                user_id,
                SUM(total_amount) AS total_amount
            FROM (
                SELECT
                    l.to_user_id AS user_id,
                    l.amount AS total_amount
                FROM ledgers l
                INNER JOIN transactions t ON l.transaction_id = t.id
                WHERE t.deleted_at IS NULL
                  AND l.from_user_id = :user_id
                UNION ALL
                SELECT
                    l.from_user_id AS user_id,
                    -l.amount AS total_amount
                FROM ledgers l
                INNER JOIN transactions t ON l.transaction_id = t.id
                WHERE t.deleted_at IS NULL
                  AND l.to_user_id = :user_id
            ) subquery
            GROUP BY user_id
            HAVING SUM(total_amount) != 0;
        """
        )
        result = session.execute(query, {"user_id": user_id})
        balance_rows = result.fetchall()
        return [
            Balance(user_id=row.user_id, total_amount=row.total_amount)
            for row in balance_rows
        ]


def clear_user_balance(user_id: int) -> None:
    balances = get_user_balance(user_id)

    for balance in balances:
        if balance.total_amount > 0:
            create_transaction(
                CreateTransaction(
                    description="Clearing Balance",
                    total_amount=balance.total_amount,
                    split_type="uneven",
                    computation_type="amount",
                    from_users=[
                        UserSplit(user_id=balance.user_id, value=balance.total_amount)
                    ],
                    to_users=[UserSplit(user_id=user_id, value=balance.total_amount)],
                )
            )
        elif balance.total_amount < 0:
            create_transaction(
                CreateTransaction(
                    description="Clearing Balance",
                    total_amount=-balance.total_amount,
                    split_type="uneven",
                    computation_type="amount",
                    from_users=[
                        UserSplit(user_id=user_id, value=-balance.total_amount)
                    ],
                    to_users=[
                        UserSplit(user_id=balance.user_id, value=-balance.total_amount)
                    ],
                )
            )


def update_transaction(
    transaction_id: int,
    transaction: CreateTransaction,
) -> TransactionResponse:
    with Session(engine) as session:
        old_transaction = session.get(Transaction, transaction_id)
        if not old_transaction:
            raise ValueError("Transaction not found")

        if old_transaction.deleted_at is not None:
            raise ValueError("Transaction already deleted")

        old_transaction.deleted_at = datetime.utcnow()
        session.add(old_transaction)
        session.commit()

        return create_transaction(transaction)


def create_transaction(
    transaction: CreateTransaction,
) -> TransactionResponse:
    ledger_entries = convert_transaction_to_ledger(transaction)

    with Session(engine) as session:
        transaction = Transaction(
            description=transaction.description,
            total_amount=transaction.total_amount,
        )
        session.add(transaction)
        session.commit()
        session.refresh(transaction)

        for entry in ledger_entries:
            entry.transaction_id = transaction.id
            session.add(entry)

        session.commit()

        for ledger_entry in ledger_entries:
            session.refresh(ledger_entry)

        return TransactionResponse(
            id=transaction.id,
            description=transaction.description,
            total_amount=transaction.total_amount,
            ledgers=ledger_entries,
        )
