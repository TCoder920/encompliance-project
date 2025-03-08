from typing import Dict, Optional, Union

import stripe
from fastapi import HTTPException
from loguru import logger

from app.core.config import settings


class StripeService:
    """
    Service for interacting with Stripe API
    """
    
    def __init__(self):
        stripe.api_key = settings.STRIPE_API_KEY
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET
        self.price_id_monthly = settings.STRIPE_PRICE_ID_MONTHLY
        self.price_id_yearly = settings.STRIPE_PRICE_ID_YEARLY
    
    async def create_checkout_session(
        self,
        user_id: int,
        user_email: str,
        subscription_type: str,
        success_url: str,
        cancel_url: str
    ) -> Dict[str, str]:
        """
        Create a Stripe checkout session for subscription
        """
        try:
            price_id = self.price_id_monthly if subscription_type == "monthly" else self.price_id_yearly
            
            # Create or retrieve customer
            customers = stripe.Customer.list(email=user_email, limit=1)
            if customers.data:
                customer = customers.data[0]
            else:
                customer = stripe.Customer.create(
                    email=user_email,
                    metadata={"user_id": str(user_id)}
                )
            
            # Create checkout session
            checkout_session = stripe.checkout.Session.create(
                customer=customer.id,
                payment_method_types=["card"],
                line_items=[
                    {
                        "price": price_id,
                        "quantity": 1,
                    },
                ],
                mode="subscription",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    "user_id": str(user_id),
                    "subscription_type": subscription_type
                }
            )
            
            return {
                "checkout_url": checkout_session.url,
                "session_id": checkout_session.id
            }
        
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")
    
    async def create_one_time_checkout(
        self,
        user_id: int,
        user_email: str,
        amount: int,  # Amount in cents
        description: str,
        success_url: str,
        cancel_url: str
    ) -> Dict[str, str]:
        """
        Create a Stripe checkout session for one-time payment
        """
        try:
            # Create or retrieve customer
            customers = stripe.Customer.list(email=user_email, limit=1)
            if customers.data:
                customer = customers.data[0]
            else:
                customer = stripe.Customer.create(
                    email=user_email,
                    metadata={"user_id": str(user_id)}
                )
            
            # Create checkout session
            checkout_session = stripe.checkout.Session.create(
                customer=customer.id,
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": "Encompliance.io Service",
                                "description": description,
                            },
                            "unit_amount": amount,
                        },
                        "quantity": 1,
                    },
                ],
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    "user_id": str(user_id),
                    "payment_type": "one_time"
                }
            )
            
            return {
                "checkout_url": checkout_session.url,
                "session_id": checkout_session.id
            }
        
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")
    
    async def cancel_subscription(self, subscription_id: str) -> Dict[str, Union[bool, str]]:
        """
        Cancel a Stripe subscription
        """
        try:
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
            
            return {
                "success": True,
                "subscription_id": subscription.id,
                "status": subscription.status,
                "cancel_at": subscription.cancel_at
            }
        
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")
    
    async def verify_webhook_signature(self, payload: bytes, signature: str) -> Dict:
        """
        Verify Stripe webhook signature
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            return event
        except (ValueError, stripe.error.SignatureVerificationError) as e:
            logger.error(f"Webhook signature verification failed: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Webhook error: {str(e)}")
    
    async def get_subscription_details(self, subscription_id: str) -> Dict:
        """
        Get details of a Stripe subscription
        """
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return subscription
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")


# Create a singleton instance
stripe_service = StripeService()
