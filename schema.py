from typing import List, Literal, Optional

from pydantic import BaseModel, EmailStr, conint, model_validator

from model import Ledger


class UserSplit(BaseModel):
    user_id: conint(ge=1)
    value: Optional[conint(ge=1)] = None


class Balance(BaseModel):
    user_id: conint(ge=1)
    total_amount: int


class CreateTransaction(BaseModel):
    description: str
    total_amount: conint(ge=1)
    split_type: Literal["even", "uneven"]
    computation_type: Literal["percentage", "amount"]
    from_users: List[UserSplit]
    to_users: List[UserSplit]

    @model_validator(mode="after")
    def validate_transaction(cls, instance):
        total_amount = instance.total_amount
        split_type = instance.split_type
        computation_type = instance.computation_type
        from_users = instance.from_users
        to_users = instance.to_users

        if not len(from_users):
            raise ValueError("from_users cannot be empty.")
        if not len(to_users):
            raise ValueError("to_users cannot be empty.")

        if split_type == "uneven":
            if computation_type == "amount":
                cls.validate_amounts(total_amount, from_users, to_users)
            elif computation_type == "percentage":
                cls.validate_percentages(from_users, to_users)

        return instance

    @staticmethod
    def validate_amounts(
        total_amount: int,
        from_users: List[UserSplit],
        to_users: List[UserSplit],
    ):
        sum_from_users = sum(user.value for user in from_users)
        sum_to_users = sum(user.value for user in to_users)

        if total_amount != sum_from_users:
            raise ValueError("Total amount mismatch in from_users.")
        if total_amount != sum_to_users:
            raise ValueError("Total amount mismatch in to_users.")

    @staticmethod
    def validate_percentages(from_users: List[UserSplit], to_users: List[UserSplit]):
        sum_from_users = sum(user.value for user in from_users)
        sum_to_users = sum(user.value for user in to_users)

        if sum_from_users != 100:
            raise ValueError("Sum of from_users percentages must be 100.")
        if sum_to_users != 100:
            raise ValueError("Sum of to_users percentages must be 100.")


class TransactionResponse(BaseModel):
    description: str
    total_amount: conint(ge=1)
    id: conint(ge=1)
    ledgers: List[Ledger]


class CreateUser(BaseModel):
    email: EmailStr
