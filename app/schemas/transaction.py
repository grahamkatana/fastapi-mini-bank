from pydantic import BaseModel, ConfigDict
from datetime import datetime
from decimal import Decimal
from typing import Optional
from app.models.transaction import TransactionType


class TransactionCreate(BaseModel):
    transaction_type: TransactionType
    amount: Decimal
    description: Optional[str] = None


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    account_id: int
    transaction_type: TransactionType
    amount: Decimal
    description: Optional[str] = None
    reference_number: str
    created_at: datetime