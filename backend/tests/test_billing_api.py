"""
Tests for the billing API endpoint
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys
from unittest.mock import MagicMock, patch
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api import app, get_db

client = TestClient(app)

# Mock DB dependency
def override_get_db():
    try:
        yield MagicMock()
    finally:
        pass

app.dependency_overrides[get_db] = override_get_db

@patch("api.WalletTransactionOperations")
@patch("api.UsageRecordOperations")
@patch("api.UserOperations")
def test_billing_details_success(
    mock_user_ops,
    mock_usage_ops,
    mock_wallet_ops
):
    """Test billing details endpoint with mocked data"""
    
    user_id = "test-user-billing"
    
    # Mock User & Wallet
    mock_user = MagicMock()
    mock_user.id = user_id
    mock_user.email = "test@billing.com"
    mock_user.wallet.balance_tokens = 1000
    mock_user.wallet.currency = "TOK"
    mock_user.wallet.updated_at = datetime.utcnow()
    
    # Mock Subscription
    mock_sub = MagicMock()
    mock_sub.id = "sub_123"
    mock_sub.status = "active"
    mock_sub.plan.name = "Pro Plan"
    mock_sub.plan.interval = "month"
    mock_sub.plan.price_cents = 2900
    mock_sub.plan.tokens_per_period = 5000
    mock_sub.plan.features = {"feature_a": True}
    mock_sub.current_period_start = datetime.utcnow()
    mock_sub.current_period_end = datetime.utcnow()
    mock_user.subscriptions = [mock_sub]
    
    mock_user_ops.create_if_not_exists.return_value = mock_user
    
    # Mock Transactions
    mock_tx = MagicMock()
    mock_tx.id = "tx_1"
    mock_tx.kind = "grant"
    mock_tx.amount = 5000
    mock_tx.balance_after = 5000
    mock_tx.created_at = datetime.utcnow()
    mock_wallet_ops.get_recent.return_value = [mock_tx]
    
    # Mock Usage
    mock_usage = MagicMock()
    mock_usage.id = "usage_1"
    mock_usage.feature_name = "resume_parse"
    mock_usage.tokens_used = 100
    mock_usage.cost_cents = 0
    mock_usage.created_at = datetime.utcnow()
    mock_usage_ops.get_recent.return_value = [mock_usage]
    
    # Mock DB query for payments
    # We need to mock the chain: db.query(SubscriptionPayment).filter(...).order_by(...).limit(...).all()
    # Since we are mocking get_db globally, the 'db' argument in the endpoint is a MagicMock.
    # However, the endpoint does:
    # sub_payments = db.query(SubscriptionPayment).filter(...).order_by(...).limit(...).all()
    
    # We need to configure the mock db to return payments
    # This is a bit tricky with MagicMock chaining, but let's try.
    
    # The endpoint calls db.query(SubscriptionPayment)
    # We can't easily distinguish which model is passed to query() with simple MagicMock
    # unless we inspect arguments.
    # But for simplicity, we can make the query chain return a list of mock payments.
    
    mock_payment = MagicMock()
    mock_payment.id = "pay_1"
    mock_payment.amount_cents = 2900
    mock_payment.currency = "USD"
    mock_payment.status = "succeeded"
    mock_payment.created_at = datetime.utcnow()
    
    # Setup the mock chain
    # db.query().filter().order_by().limit().all() -> [mock_payment]
    with patch("api.get_db", override_get_db):
        # We need to access the mock db instance that will be injected
        # Since we use dependency_overrides, we can't easily access the specific instance 
        # unless we control the generator.
        
        # Alternative: We can mock the db session in the test function if we didn't use dependency_overrides,
        # but dependency_overrides is the standard way.
        
        # Let's rely on the fact that MagicMock returns MagicMocks by default.
        # We just need to make sure the final .all() returns our list.
        
        # However, the endpoint calls db.query(SubscriptionPayment) AND db.query(Subscription) (implicitly via relationships? No, explicit query in loop)
        # Wait, the endpoint uses `user.subscriptions` which is a relationship, so it's accessed via the mock_user object.
        # But for payments:
        # sub_payments = db.query(SubscriptionPayment).filter(...).order_by(...).limit(...).all()
        
        # We can try to patch the db session passed to the endpoint.
        pass

    # To properly mock the db query for payments, we can use a side_effect on db.query
    # But since we are using dependency_overrides with a fresh MagicMock each time, 
    # we need to configure THAT mock.
    
    # Let's define the override to return a configured mock
    mock_db = MagicMock()
    
    # Configure query chain
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_order_by = mock_filter.order_by.return_value
    mock_limit = mock_order_by.limit.return_value
    mock_limit.all.return_value = [mock_payment]
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    response = client.get("/api/billing/details", headers={"x-user-id": user_id})
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify structure
    assert data["wallet"]["balance_tokens"] == 1000
    assert data["subscription"]["status"] == "active"
    assert data["subscription"]["plan"]["name"] == "Pro Plan"
    
    assert len(data["payment_history"]) == 1
    assert data["payment_history"][0]["id"] == "pay_1"
    
    assert len(data["transaction_history"]) == 1
    assert data["transaction_history"][0]["id"] == "tx_1"
    
    assert len(data["usage_history"]) == 1
    assert data["usage_history"][0]["id"] == "usage_1"

def test_billing_details_no_auth():
    """Test billing details without user ID"""
    response = client.get("/api/billing/details")
    assert response.status_code == 401
