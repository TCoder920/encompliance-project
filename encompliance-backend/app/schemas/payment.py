from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# Shared properties
class PaymentBase(BaseModel):
    amount: float
    currency: str = "usd"
    payment_type: str  # one_time, subscription
    subscription_plan: Optional[str] = None  # monthly, yearly
    description: Optional[str] = None


# Properties to receive via API on creation
class PaymentCreate(PaymentBase):
    pass


# Properties to receive via API on update
class PaymentUpdate(BaseModel):
    status: Optional[str] = None
    stripe_subscription_id: Optional[str] = None


# Properties shared by models stored in DB
class PaymentInDBBase(PaymentBase):
    id: int
    stripe_payment_id: str
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    status: str
    payment_method: Optional[str] = None
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Properties to return via API
class Payment(PaymentInDBBase):
    pass


# Properties stored in DB
class PaymentInDB(PaymentInDBBase):
    pass


# Stripe checkout session response
class StripeCheckoutResponse(BaseModel):
    checkout_url: str
    session_id: str


# Stripe webhook event
class StripeWebhookEvent(BaseModel):
    event_type: str
    data: dict
