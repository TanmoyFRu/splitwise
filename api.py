from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from schema import Balance, CreateTransaction, CreateUser
from service import *

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def root_endpoint():
    return """
        <!DOCTYPE html>
        <html>
        <head><title>Splitwise API</title></head>
        <body style="margin:0; height:100vh; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center;">
            <div>
                <p>
                    <a href="https://subh.me/">website</a> &middot;
                    <a href="https://www.linkedin.com/in/subhrashisdas/">linkedin</a> &middot;
                    <a href="https://github.com/subhrashisdas/">github</a>
                </p>
                <p>&copy; 2024 Subhrashis Das. All rights reserved.</p>
            </div>
        </body>
        </html>
    """


@router.post("/users/", response_model=User)
def create_user_endpoint_endpoint(user: CreateUser):
    try:
        return create_user(user.email)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/transactions/", response_model=TransactionResponse)
def create_transaction_endpoint(transaction: CreateTransaction):
    try:
        return create_transaction(transaction)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/transactions/{transaction_id}/", response_model=TransactionResponse)
def update_transaction_endpoint(transaction_id: int, transaction: CreateTransaction):
    try:
        return update_transaction(transaction_id, transaction)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/users/{user_id}/balance/", response_model=List[Balance])
def get_user_balance_endpoint(user_id: int) -> List[Balance]:
    return get_user_balance(user_id)


@router.post("/users/{user_id}/clear/")
def clear_user_balance_endpoint(user_id: int):
    try:
        clear_user_balance(user_id)
        return {}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
