from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    account_number = Column(String(50), unique=True, index=True, nullable=False)
    account_type = Column(String(50), nullable=False)  # e.g., 'savings', 'checking'
    balance = Column(Numeric(15, 2), default=0.00)
    currency = Column(String(3), default="USD")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="account")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")
