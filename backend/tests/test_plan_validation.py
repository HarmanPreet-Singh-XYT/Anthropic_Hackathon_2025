"""
Test script to verify billing plan validation
"""

import sys
import os
sys.path.append(os.getcwd())

from database import DatabaseManager, BillingPlan
from config.settings import settings

def test_plan_validation():
    print("🧪 Testing Billing Plan Validation...")
    
    # Initialize DB
    db_manager = DatabaseManager(settings.database_url)
    db = next(db_manager.get_session())
    
    try:
        # 1. Check if plans exist
        plans = db.query(BillingPlan).all()
        print(f"\n✓ Found {len(plans)} billing plans in database:")
        
        for plan in plans:
            print(f"  - {plan.name} ({plan.slug}): ${plan.price_cents/100:.2f}/{plan.interval}")
        
        # 2. Test valid plan slug
        valid_slug = "pro"
        plan = db.query(BillingPlan).filter(BillingPlan.slug == valid_slug).first()
        if plan:
            print(f"\n✓ Valid plan slug '{valid_slug}' found:")
            print(f"  Name: {plan.name}")
            print(f"  Price: ${plan.price_cents/100:.2f}")
            print(f"  Tokens: {plan.tokens_per_period}")
        else:
            print(f"\n✗ Valid plan slug '{valid_slug}' NOT found (this is bad!)")
        
        # 3. Test invalid plan slug
        invalid_slug = "fake-plan-999"
        plan = db.query(BillingPlan).filter(BillingPlan.slug == invalid_slug).first()
        if plan:
            print(f"\n✗ Invalid plan slug '{invalid_slug}' found (this is bad!)")
        else:
            print(f"\n✓ Invalid plan slug '{invalid_slug}' correctly rejected")
        
        print("\n🎉 Validation Test Complete!")
        
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_plan_validation()
