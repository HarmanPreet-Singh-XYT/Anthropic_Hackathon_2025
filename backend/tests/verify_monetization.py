import sys
import os
import uuid
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from database import DatabaseManager, User, UserWallet, WalletTransaction, BillingPlan, Subscription, SubscriptionPayment
from config.settings import settings

def verify_monetization():
    print("🚀 Verifying Monetization Models...")
    
    # Initialize DB
    db_manager = DatabaseManager(settings.database_url)
    db = next(db_manager.get_session())
    
    try:
        # 1. Create User
        user_id = f"test_user_{uuid.uuid4()}"
        user = User(
            id=user_id,
            email=f"{user_id}@example.com"
        )
        db.add(user)
        db.commit()
        print(f"✅ Created User: {user.id}")
        
        # 2. Create Wallet
        wallet = UserWallet(
            user_id=user_id,
            balance_tokens=1000
        )
        db.add(wallet)
        db.commit()
        print(f"✅ Created Wallet for User: {wallet.user_id}, Balance: {wallet.balance_tokens}")
        
        # 3. Create Transaction
        tx = WalletTransaction(
            user_id=user_id,
            amount=-100,
            balance_after=900,
            kind="deduction",
            reference_id="test_ref"
        )
        db.add(tx)
        
        # Update wallet balance
        wallet.balance_tokens = 900
        db.commit()
        print(f"✅ Created Transaction: {tx.id}, New Balance: {wallet.balance_tokens}")
        
        # 4. Create Billing Plan
        plan_id = f"plan_{uuid.uuid4()}"
        plan = BillingPlan(
            id=plan_id,
            slug=f"pro_plan_{uuid.uuid4()}",
            name="Pro Plan",
            price_cents=2900,
            interval="month",
            tokens_per_period=5000
        )
        db.add(plan)
        db.commit()
        print(f"✅ Created Billing Plan: {plan.name} ({plan.slug})")
        
        # 5. Create Subscription
        sub = Subscription(
            user_id=user_id,
            plan_id=plan.id,
            status="active",
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow()
        )
        db.add(sub)
        db.commit()
        print(f"✅ Created Subscription: {sub.id} for User {sub.user_id}")
        
        # 6. Create Payment
        payment = SubscriptionPayment(
            subscription_id=sub.id,
            amount_cents=2900,
            status="succeeded",
            external_payment_id="pay_123"
        )
        db.add(payment)
        db.commit()
        print(f"✅ Created Payment: {payment.id} for Subscription {payment.subscription_id}")
        
        print("\n🎉 Verification Successful!")
        
    except Exception as e:
        print(f"\n❌ Verification Failed: {e}")
        db.rollback()
        raise
    finally:
        # Cleanup (optional)
        # db.delete(payment)
        # db.delete(sub)
        # db.delete(plan)
        # db.delete(tx)
        # db.delete(wallet)
        # db.delete(user)
        # db.commit()
        db.close()

if __name__ == "__main__":
    verify_monetization()
