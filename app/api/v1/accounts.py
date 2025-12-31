from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.account import Account
from app.schemas.account import AccountCreate, AccountResponse
from app.core.auth import get_current_active_user
from app.core.websocket import manager
import uuid

router = APIRouter()


@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    account: AccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new account for the current user"""
    # Check if user already has an account
    existing_account = db.query(Account).filter(Account.user_id == current_user.id).first()
    
    if existing_account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has an account"
        )
    
    # Generate unique account number
    account_number = f"ACC{uuid.uuid4().hex[:10].upper()}"
    
    # Create new account
    db_account = Account(
        user_id=current_user.id,
        account_number=account_number,
        account_type=account.account_type,
        currency=account.currency
    )
    
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    
    # Send real-time notification via WebSocket
    await manager.send_personal_message(
        {
            "type": "account",
            "event": "account_created",
            "account": {
                "id": db_account.id,
                "account_number": account_number,
                "account_type": account.account_type,
                "balance": float(db_account.balance),
                "currency": account.currency
            },
            "message": f"Your {account.account_type} account has been created successfully!"
        },
        current_user.id
    )
    
    return db_account


@router.get("/me", response_model=AccountResponse)
def get_my_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's account"""
    account = db.query(Account).filter(Account.user_id == current_user.id).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found. Please create an account first."
        )
    
    return account


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get account by ID"""
    account = db.query(Account).filter(Account.id == account_id).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    # Check if the account belongs to the current user
    if account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this account"
        )
    
    return account
