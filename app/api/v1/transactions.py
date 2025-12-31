from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.core.auth import get_current_active_user
from app.core.websocket import manager
from app.tasks.celery_tasks import process_large_transaction
import uuid

router = APIRouter()


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new transaction"""
    # Get user's account
    account = db.query(Account).filter(Account.user_id == current_user.id).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found. Please create an account first."
        )
    
    # Store old balance for notification
    old_balance = float(account.balance)
    
    # Generate unique reference number
    reference_number = f"TXN{uuid.uuid4().hex[:12].upper()}"
    
    # Create new transaction
    db_transaction = Transaction(
        account_id=account.id,
        transaction_type=transaction.transaction_type,
        amount=transaction.amount,
        description=transaction.description,
        reference_number=reference_number
    )
    
    db.add(db_transaction)
    
    # Update account balance based on transaction type
    if transaction.transaction_type == "deposit":
        account.balance += transaction.amount
    elif transaction.transaction_type == "withdrawal":
        if account.balance < transaction.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient funds"
            )
        account.balance -= transaction.amount
    
    db.commit()
    db.refresh(db_transaction)
    
    new_balance = float(account.balance)
    
    # Send real-time notification via WebSocket
    await manager.send_personal_message(
        {
            "type": "transaction",
            "event": "transaction_created",
            "transaction": {
                "id": db_transaction.id,
                "type": transaction.transaction_type,
                "amount": float(transaction.amount),
                "description": transaction.description,
                "reference_number": reference_number
            },
            "account": {
                "id": account.id,
                "old_balance": old_balance,
                "new_balance": new_balance,
                "balance_change": new_balance - old_balance,
                "currency": account.currency
            },
            "message": f"{transaction.transaction_type.capitalize()} of {account.currency} {transaction.amount} completed"
        },
        current_user.id
    )
    
    # Trigger Celery task for large transactions
    if transaction.amount > 10000:
        process_large_transaction.delay(db_transaction.id, str(transaction.amount))
        
        # Notify about large transaction processing
        await manager.send_personal_message(
            {
                "type": "notification",
                "event": "large_transaction_processing",
                "message": f"Large transaction of {account.currency} {transaction.amount} is being processed for compliance",
                "transaction_id": db_transaction.id
            },
            current_user.id
        )
    
    return db_transaction


@router.get("/", response_model=List[TransactionResponse])
def get_transactions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all transactions for current user's account"""
    # Get user's account
    account = db.query(Account).filter(Account.user_id == current_user.id).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    transactions = db.query(Transaction).filter(
        Transaction.account_id == account.id
    ).offset(skip).limit(limit).all()
    
    return transactions


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get transaction by ID"""
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    # Check if the transaction belongs to the current user's account
    account = db.query(Account).filter(Account.user_id == current_user.id).first()
    
    if not account or transaction.account_id != account.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this transaction"
        )
    
    return transaction
