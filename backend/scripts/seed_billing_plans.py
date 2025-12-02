"""
Seed billing plans into the database
Run this script to populate initial billing plans
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from database import DatabaseManager, BillingPlan
from config.settings import settings


def seed_billing_plans():
    """Create initial billing plans"""
    db_manager = DatabaseManager(settings.database_url)
    db = next(db_manager.get_session())
    
    try:
        # Check if plans already exist
        existing = db.query(BillingPlan).count()
        if existing > 0:
            print(f"✓ {existing} billing plans already exist")
            return
        
        plans = [
            BillingPlan(
                slug="free",
                name="Free",
                price_cents=0,
                interval="month",
                tokens_per_period=100,
                features={"max_applications": 5, "support": "community"}
            ),
            BillingPlan(
                slug="starter",
                name="Starter",
                price_cents=999,  # $9.99
                interval="month",
                tokens_per_period=500,
                features={"max_applications": 25, "support": "email", "priority_processing": False}
            ),
            BillingPlan(
                slug="pro",
                name="Pro",
                price_cents=2900,  # $29.00
                interval="month",
                tokens_per_period=2000,
                features={"max_applications": -1, "support": "priority", "priority_processing": True, "advanced_analytics": True}
            ),
            BillingPlan(
                slug="starter-annual",
                name="Starter Annual",
                price_cents=9990,  # $99.90 (save ~17%)
                interval="year",
                tokens_per_period=6000, # 500 * 12
                features={
                    "max_applications": 25, 
                    "support": "email", 
                    "priority_processing": False,
                    "annual_discount": True
                }
            ),
            BillingPlan(
                slug="pro-annual",
                name="Pro Annual",
                price_cents=29000,  # $290.00 (save ~17%)
                interval="year",
                tokens_per_period=24000,
                features={"max_applications": -1, "support": "priority", "priority_processing": True, "advanced_analytics": True, "annual_discount": True}
            )
        ]
        
        for plan in plans:
            db.add(plan)
        
        db.commit()
        print(f"✓ Created {len(plans)} billing plans")
        
        for plan in plans:
            print(f"  - {plan.name} ({plan.slug}): ${plan.price_cents/100:.2f}/{plan.interval}")
        
    except Exception as e:
        print(f"✗ Error seeding billing plans: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_billing_plans()
