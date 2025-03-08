from datetime import datetime, timedelta
from typing import Any, Dict, List

from fastapi import APIRouter, Body, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.models.payment import Payment
from app.models.user import User
from app.schemas.payment import (
    Payment as PaymentSchema,
    StripeCheckoutResponse,
    StripeWebhookEvent,
)
from app.services.stripe_service import stripe_service
from app.utils.deps import get_current_active_user, get_db

router = APIRouter()


@router.post("/create-checkout-session", response_model=StripeCheckoutResponse)
async def create_checkout_session(
    subscription_type: str = Body(...),  # monthly or yearly
    success_url: str = Body(...),
    cancel_url: str = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create a Stripe checkout session for subscription
    """
    if subscription_type not in ["monthly", "yearly"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid subscription type",
        )
    
    # Create checkout session
    checkout_session = await stripe_service.create_checkout_session(
        user_id=current_user.id,
        user_email=current_user.email,
        subscription_type=subscription_type,
        success_url=success_url,
        cancel_url=cancel_url,
    )
    
    return checkout_session


@router.post("/create-one-time-checkout", response_model=StripeCheckoutResponse)
async def create_one_time_checkout(
    amount: int = Body(...),  # Amount in cents
    description: str = Body(...),
    success_url: str = Body(...),
    cancel_url: str = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create a Stripe checkout session for one-time payment
    """
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be greater than 0",
        )
    
    # Create checkout session
    checkout_session = await stripe_service.create_one_time_checkout(
        user_id=current_user.id,
        user_email=current_user.email,
        amount=amount,
        description=description,
        success_url=success_url,
        cancel_url=cancel_url,
    )
    
    return checkout_session


@router.post("/webhook", response_model=Dict[str, str])
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None),
    db: Session = Depends(get_db),
) -> Any:
    """
    Handle Stripe webhook events
    """
    # Get request body
    payload = await request.body()
    
    # Verify webhook signature
    try:
        event = await stripe_service.verify_webhook_signature(payload, stripe_signature)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Webhook signature verification failed: {str(e)}",
        )
    
    # Handle different event types
    event_type = event["type"]
    
    if event_type == "checkout.session.completed":
        # Get session data
        session = event["data"]["object"]
        
        # Get user ID from metadata
        user_id = int(session["metadata"]["user_id"])
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return {"status": "error", "message": "User not found"}
        
        # Create payment record
        payment_type = session["metadata"].get("payment_type", "subscription")
        subscription_type = session["metadata"].get("subscription_type")
        
        payment = Payment(
            stripe_payment_id=session["id"],
            stripe_customer_id=session["customer"],
            stripe_subscription_id=session.get("subscription"),
            amount=session["amount_total"] / 100,  # Convert from cents
            currency=session["currency"],
            status="succeeded",
            payment_method="card",
            payment_type=payment_type,
            subscription_plan=subscription_type,
            description=f"{payment_type.capitalize()} payment",
            user_id=user_id,
        )
        db.add(payment)
        
        # Update user subscription status if it's a subscription
        if payment_type == "subscription":
            user.subscription_status = "paid"
            
            # Set subscription end date
            if subscription_type == "monthly":
                user.subscription_end_date = datetime.utcnow() + timedelta(days=30)
            else:  # yearly
                user.subscription_end_date = datetime.utcnow() + timedelta(days=365)
        
        db.commit()
    
    elif event_type == "invoice.payment_succeeded":
        # Handle subscription renewal
        invoice = event["data"]["object"]
        subscription_id = invoice.get("subscription")
        
        if subscription_id:
            # Find the user with this subscription
            payment = db.query(Payment).filter(
                Payment.stripe_subscription_id == subscription_id
            ).first()
            
            if payment:
                user = db.query(User).filter(User.id == payment.user_id).first()
                
                if user:
                    # Update subscription end date
                    if payment.subscription_plan == "monthly":
                        user.subscription_end_date = datetime.utcnow() + timedelta(days=30)
                    else:  # yearly
                        user.subscription_end_date = datetime.utcnow() + timedelta(days=365)
                    
                    # Create new payment record
                    new_payment = Payment(
                        stripe_payment_id=invoice["id"],
                        stripe_customer_id=invoice["customer"],
                        stripe_subscription_id=subscription_id,
                        amount=invoice["amount_paid"] / 100,  # Convert from cents
                        currency=invoice["currency"],
                        status="succeeded",
                        payment_method="card",
                        payment_type="subscription",
                        subscription_plan=payment.subscription_plan,
                        description="Subscription renewal",
                        user_id=user.id,
                    )
                    db.add(new_payment)
                    db.commit()
    
    elif event_type == "customer.subscription.deleted":
        # Handle subscription cancellation
        subscription = event["data"]["object"]
        subscription_id = subscription["id"]
        
        # Find the user with this subscription
        payment = db.query(Payment).filter(
            Payment.stripe_subscription_id == subscription_id
        ).first()
        
        if payment:
            user = db.query(User).filter(User.id == payment.user_id).first()
            
            if user:
                # Update user subscription status
                user.subscription_status = "free"
                db.commit()
    
    return {"status": "success"}


@router.get("/subscription", response_model=Dict[str, Any])
async def get_subscription_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get current user's subscription status
    """
    # Get the latest subscription payment
    payment = db.query(Payment).filter(
        Payment.user_id == current_user.id,
        Payment.payment_type == "subscription",
    ).order_by(Payment.created_at.desc()).first()
    
    if not payment or not payment.stripe_subscription_id:
        return {
            "status": current_user.subscription_status,
            "end_date": current_user.subscription_end_date,
            "has_active_subscription": False,
        }
    
    try:
        # Get subscription details from Stripe
        subscription = await stripe_service.get_subscription_details(
            payment.stripe_subscription_id
        )
        
        return {
            "status": current_user.subscription_status,
            "end_date": current_user.subscription_end_date,
            "has_active_subscription": subscription["status"] == "active",
            "subscription_id": payment.stripe_subscription_id,
            "plan": payment.subscription_plan,
            "cancel_at_period_end": subscription.get("cancel_at_period_end", False),
        }
    except Exception as e:
        return {
            "status": current_user.subscription_status,
            "end_date": current_user.subscription_end_date,
            "has_active_subscription": False,
            "error": str(e),
        }


@router.post("/cancel-subscription", response_model=Dict[str, Any])
async def cancel_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Cancel current user's subscription
    """
    # Get the latest subscription payment
    payment = db.query(Payment).filter(
        Payment.user_id == current_user.id,
        Payment.payment_type == "subscription",
    ).order_by(Payment.created_at.desc()).first()
    
    if not payment or not payment.stripe_subscription_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found",
        )
    
    try:
        # Cancel subscription in Stripe
        result = await stripe_service.cancel_subscription(payment.stripe_subscription_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error canceling subscription: {str(e)}",
        )


@router.get("/history", response_model=List[PaymentSchema])
async def get_payment_history(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get payment history for the current user
    """
    payments = db.query(Payment).filter(
        Payment.user_id == current_user.id
    ).order_by(Payment.created_at.desc()).offset(skip).limit(limit).all()
    
    return payments
