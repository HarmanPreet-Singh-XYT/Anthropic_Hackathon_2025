"""
Stripe integration service for subscription and payment management
"""

import stripe
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from config.settings import settings
from workflows.database import (
    User, UserWallet, Subscription, BillingPlan, 
    SubscriptionPayment, WalletTransaction
)

# Initialize Stripe
stripe.api_key = settings.stripe_secret_key


class StripeService:
    """Service for managing Stripe operations"""
    
    @staticmethod
    def create_customer(user_id: str, email: Optional[str] = None) -> str:
        """
        Create a Stripe customer
        
        Args:
            user_id: Internal user ID
            email: User email
            
        Returns:
            Stripe customer ID
        """
        customer = stripe.Customer.create(
            metadata={"user_id": user_id},
            email=email
        )
        return customer.id
    
    @staticmethod
    def create_checkout_session(
        db: Session,
        user_id: str,
        plan_slug: str,
        success_url: str,
        cancel_url: str
    ) -> Dict[str, Any]:
        """
        Create a Stripe checkout session for subscription
        
        Args:
            db: Database session
            user_id: User ID
            plan_slug: Billing plan slug
            success_url: Redirect URL on success
            cancel_url: Redirect URL on cancel
            
        Returns:
            Checkout session data
        """
        from workflows.db_operations import UserOperations
        
        # Get or create user
        user = UserOperations.create_if_not_exists(db, user_id)
        
        # Get billing plan
        plan = db.query(BillingPlan).filter(BillingPlan.slug == plan_slug).first()
        if not plan:
            raise ValueError(f"Plan {plan_slug} not found")
        
        # Create or get Stripe customer
        customer_id = StripeService._get_or_create_customer(db, user)
        
        # Create checkout session
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': plan.price_cents,
                    'recurring': {
                        'interval': plan.interval
                    },
                    'product_data': {
                        'name': plan.name,
                        'description': f"{plan.tokens_per_period} tokens per {plan.interval}"
                    }
                },
                'quantity': 1
            }],
            mode='subscription',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'user_id': user_id,
                'plan_id': plan.id
            }
        )
        
        return {
            'session_id': session.id,
            'url': session.url
        }
    
    @staticmethod
    def create_portal_session(db: Session, user_id: str, return_url: str) -> str:
        """
        Create a Stripe customer portal session
        
        Args:
            db: Database session
            user_id: User ID
            return_url: Return URL after portal session
            
        Returns:
            Portal session URL
        """
        from workflows.db_operations import UserOperations
        
        user = UserOperations.get(db, user_id)
        if not user:
            raise ValueError("User not found")
        
        customer_id = StripeService._get_or_create_customer(db, user)
        
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url
        )
        
        return session.url
    
    @staticmethod
    def handle_webhook_event(db: Session, payload: bytes, sig_header: str) -> Dict[str, Any]:
        """
        Handle Stripe webhook events
        
        Args:
            db: Database session
            payload: Raw webhook payload
            sig_header: Stripe signature header
            
        Returns:
            Event processing result
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.stripe_webhook_secret
            )
        except ValueError:
            raise ValueError("Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise ValueError("Invalid signature")
        
        # Handle different event types
        if event['type'] == 'checkout.session.completed':
            return StripeService._handle_checkout_completed(db, event['data']['object'])
        elif event['type'] == 'customer.subscription.updated':
            return StripeService._handle_subscription_updated(db, event['data']['object'])
        elif event['type'] == 'customer.subscription.deleted':
            return StripeService._handle_subscription_deleted(db, event['data']['object'])
        elif event['type'] == 'invoice.payment_succeeded':
            return StripeService._handle_payment_succeeded(db, event['data']['object'])
        elif event['type'] == 'invoice.payment_failed':
            return StripeService._handle_payment_failed(db, event['data']['object'])
        
        return {'status': 'ignored', 'type': event['type']}
    
    @staticmethod
    def _get_or_create_customer(db: Session, user: User) -> str:
        """Get existing Stripe customer ID or create new one"""
        # Check if user has active subscription with customer ID
        active_sub = db.query(Subscription).filter(
            Subscription.user_id == user.id,
            Subscription.external_subscription_id.isnot(None)
        ).first()
        
        if active_sub:
            # Get customer from subscription
            stripe_sub = stripe.Subscription.retrieve(active_sub.external_subscription_id)
            return stripe_sub.customer
        
        # Create new customer
        return StripeService.create_customer(user.id, user.email)
    
    @staticmethod
    def _handle_checkout_completed(db: Session, session: Dict[str, Any]) -> Dict[str, Any]:
        """Handle successful checkout"""
        user_id = session['metadata']['user_id']
        plan_id = session['metadata']['plan_id']
        
        # Get subscription from Stripe
        subscription_id = session['subscription']
        stripe_sub = stripe.Subscription.retrieve(subscription_id)
        
        # Create subscription record
        subscription = Subscription(
            user_id=user_id,
            plan_id=plan_id,
            status='active',
            current_period_start=datetime.fromtimestamp(stripe_sub.current_period_start),
            current_period_end=datetime.fromtimestamp(stripe_sub.current_period_end),
            external_subscription_id=subscription_id
        )
        db.add(subscription)
        
        # Grant tokens
        plan = db.query(BillingPlan).filter(BillingPlan.id == plan_id).first()
        if plan:
            wallet = db.query(UserWallet).filter(UserWallet.user_id == user_id).first()
            if wallet:
                old_balance = wallet.balance_tokens
                wallet.balance_tokens += plan.tokens_per_period
                wallet.updated_at = datetime.utcnow()
                
                # Record transaction
                transaction = WalletTransaction(
                    user_id=user_id,
                    amount=plan.tokens_per_period,
                    balance_after=wallet.balance_tokens,
                    kind='grant',
                    reference_id=subscription_id,
                    metadata_json={'source': 'subscription_start', 'plan': plan.name}
                )
                db.add(transaction)
        
        db.commit()
        
        return {'status': 'success', 'subscription_id': subscription_id}
    
    @staticmethod
    def _handle_subscription_updated(db: Session, stripe_sub: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription update"""
        subscription = db.query(Subscription).filter(
            Subscription.external_subscription_id == stripe_sub['id']
        ).first()
        
        if subscription:
            subscription.status = stripe_sub['status']
            subscription.current_period_start = datetime.fromtimestamp(stripe_sub['current_period_start'])
            subscription.current_period_end = datetime.fromtimestamp(stripe_sub['current_period_end'])
            subscription.cancel_at_period_end = stripe_sub.get('cancel_at_period_end', False)
            db.commit()
            
            return {'status': 'updated', 'subscription_id': stripe_sub['id']}
        
        return {'status': 'not_found'}
    
    @staticmethod
    def _handle_subscription_deleted(db: Session, stripe_sub: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription cancellation"""
        subscription = db.query(Subscription).filter(
            Subscription.external_subscription_id == stripe_sub['id']
        ).first()
        
        if subscription:
            subscription.status = 'canceled'
            db.commit()
            
            return {'status': 'canceled', 'subscription_id': stripe_sub['id']}
        
        return {'status': 'not_found'}
    
    @staticmethod
    def _handle_payment_succeeded(db: Session, invoice: Dict[str, Any]) -> Dict[str, Any]:
        """Handle successful payment"""
        subscription_id = invoice.get('subscription')
        
        if subscription_id:
            subscription = db.query(Subscription).filter(
                Subscription.external_subscription_id == subscription_id
            ).first()
            
            if subscription:
                # Record payment
                payment = SubscriptionPayment(
                    subscription_id=subscription.id,
                    amount_cents=invoice['amount_paid'],
                    currency=invoice['currency'].upper(),
                    status='succeeded',
                    external_payment_id=invoice['payment_intent']
                )
                db.add(payment)
                
                # Grant tokens for renewal
                plan = db.query(BillingPlan).filter(BillingPlan.id == subscription.plan_id).first()
                if plan:
                    wallet = db.query(UserWallet).filter(UserWallet.user_id == subscription.user_id).first()
                    if wallet:
                        wallet.balance_tokens += plan.tokens_per_period
                        wallet.updated_at = datetime.utcnow()
                        
                        # Record transaction
                        transaction = WalletTransaction(
                            user_id=subscription.user_id,
                            amount=plan.tokens_per_period,
                            balance_after=wallet.balance_tokens,
                            kind='grant',
                            reference_id=subscription_id,
                            metadata_json={'source': 'subscription_renewal', 'plan': plan.name}
                        )
                        db.add(transaction)
                
                db.commit()
                
                return {'status': 'success', 'payment_id': invoice['payment_intent']}
        
        return {'status': 'not_applicable'}
    
    @staticmethod
    def _handle_payment_failed(db: Session, invoice: Dict[str, Any]) -> Dict[str, Any]:
        """Handle failed payment"""
        subscription_id = invoice.get('subscription')
        
        if subscription_id:
            subscription = db.query(Subscription).filter(
                Subscription.external_subscription_id == subscription_id
            ).first()
            
            if subscription:
                # Update subscription status
                subscription.status = 'past_due'
                
                # Record failed payment
                payment = SubscriptionPayment(
                    subscription_id=subscription.id,
                    amount_cents=invoice['amount_due'],
                    currency=invoice['currency'].upper(),
                    status='failed',
                    external_payment_id=invoice.get('payment_intent')
                )
                db.add(payment)
                db.commit()
                
                return {'status': 'failed', 'subscription_id': subscription_id}
        
        return {'status': 'not_applicable'}
