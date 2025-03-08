from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.session import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    stripe_payment_id = Column(String, unique=True, index=True, nullable=False)
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="usd")
    status = Column(String, nullable=False)  # succeeded, pending, failed
    payment_method = Column(String, nullable=True)  # credit_card, paypal, etc.
    payment_type = Column(String, nullable=False)  # one_time, subscription
    subscription_plan = Column(String, nullable=True)  # monthly, yearly
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    user = relationship("User", back_populates="payments")
