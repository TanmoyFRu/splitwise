from typing import List

from .model import Ledger
from .schema import CreateTransaction, UserSplit


def convert_percentage_to_amount(
    transaction_split: CreateTransaction,
) -> CreateTransaction:
    total_amount = transaction_split.total_amount

    from_users = convert_uneven_percentage_to_amount(
        transaction_split.from_users, total_amount
    )
    to_users = convert_uneven_percentage_to_amount(
        transaction_split.to_users, total_amount
    )

    return CreateTransaction(
        description=transaction_split.description,
        total_amount=total_amount,
        split_type="uneven",
        computation_type="amount",
        from_users=from_users,
        to_users=to_users,
    )


def compute_transaction_to_ledger(
    transaction_split: CreateTransaction,
) -> List[Ledger]:
    ledger_entries = []

    from_users = list(transaction_split.from_users)
    to_users = list(transaction_split.to_users)

    while from_users and to_users:
        from_user = from_users[0]
        from_amount = from_user.value

        to_user = to_users[0]
        to_amount = to_user.value

        if from_amount >= to_amount:
            ledger_amount = to_amount
        else:
            ledger_amount = from_amount

        from_amount -= ledger_amount
        to_amount -= ledger_amount

        ledger_entry = Ledger(
            from_user_id=from_user.user_id,
            to_user_id=to_user.user_id,
            amount=ledger_amount,
        )
        ledger_entries.append(ledger_entry)

        from_user.value = from_amount
        to_user.value = to_amount

        if from_amount == 0:
            from_users.pop(0)

        if to_amount == 0:
            to_users.pop(0)

    return ledger_entries


def convert_even_to_uneven_users(
    users: List[UserSplit], total_amount: int
) -> List[UserSplit]:
    num_users = len(users)
    even_amount = total_amount // num_users

    uneven_users = [
        UserSplit(user_id=user.user_id, value=even_amount) for user in users
    ]

    residual_amount = total_amount - even_amount * num_users
    if residual_amount > 0:
        uneven_users[-1].value += residual_amount

    return uneven_users


def convert_uneven_percentage_to_amount(
    users: List[UserSplit], total_amount: int
) -> List[UserSplit]:
    uneven_users = []
    for user in users:
        proportion = user.value
        amount = total_amount * proportion / 100
        uneven_users.append(UserSplit(user_id=user.user_id, value=amount))

    total_assigned_amount = sum(user.value for user in uneven_users)

    residual_amount = total_amount - total_assigned_amount
    if residual_amount > 0:
        uneven_users[-1].value += residual_amount

    return uneven_users


def convert_even_to_uneven(
    transaction: CreateTransaction,
) -> CreateTransaction:
    from_users = convert_even_to_uneven_users(
        transaction.from_users, transaction.total_amount
    )
    to_users = convert_even_to_uneven_users(
        transaction.to_users, transaction.total_amount
    )

    return CreateTransaction(
        description=transaction.description,
        total_amount=transaction.total_amount,
        split_type="uneven",
        computation_type=transaction.computation_type,
        from_users=from_users,
        to_users=to_users,
    )


def convert_percentage_to_amount(
    transaction_split: CreateTransaction,
) -> CreateTransaction:
    total_amount = transaction_split.total_amount

    from_users = convert_uneven_percentage_to_amount(
        transaction_split.from_users, total_amount
    )
    to_users = convert_uneven_percentage_to_amount(
        transaction_split.to_users, total_amount
    )

    return CreateTransaction(
        description=transaction_split.description,
        total_amount=total_amount,
        split_type="uneven",
        computation_type="amount",
        from_users=from_users,
        to_users=to_users,
    )


def compute_transaction_to_ledger(
    transaction_split: CreateTransaction,
) -> List[Ledger]:
    ledger_entries = []
    from_users = list(transaction_split.from_users)
    to_users = list(transaction_split.to_users)

    while from_users or to_users:
        from_user = from_users[0]
        from_amount = from_user.value

        to_user = to_users[0]
        to_amount = to_user.value

        if from_amount >= to_amount:
            ledger_amount = to_amount
        else:
            ledger_amount = from_amount

        from_amount -= ledger_amount
        to_amount -= ledger_amount

        ledger_entry = Ledger(
            from_user_id=from_user.user_id,
            to_user_id=to_user.user_id,
            amount=ledger_amount,
        )
        ledger_entries.append(ledger_entry)

        from_user.value = from_amount
        to_user.value = to_amount

        if from_amount == 0:
            from_users.pop(0)

        if to_amount == 0:
            to_users.pop(0)

    return ledger_entries


def convert_transaction_to_ledger(transaction: CreateTransaction) -> List[Ledger]:
    if transaction.split_type == "even":
        return compute_transaction_to_ledger(convert_even_to_uneven(transaction))
    elif transaction.split_type == "uneven":
        if transaction.computation_type == "amount":
            return compute_transaction_to_ledger(transaction)
        elif transaction.computation_type == "percentage":
            return compute_transaction_to_ledger(
                convert_percentage_to_amount(transaction)
            )
