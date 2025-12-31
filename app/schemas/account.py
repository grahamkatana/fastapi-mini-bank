from pydantic import BaseModel, ConfigDict
from datetime import datetime
from decimal import Decimal


class AccountCreate(BaseModel):
    account_type: str
    currency: str = "USD"


class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    account_number: str
    account_type: str
    balance: Decimal
    currency: str
    created_at: datetime
