"""
Test script for billing details endpoint
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER_ID = "test_user_billing_demo"

def test_billing_details():
    """Test the billing details endpoint"""
    print("=" * 60)
    print("Testing Billing Details Endpoint")
    print("=" * 60)
    
    url = f"{BASE_URL}/api/billing/details"
    headers = {
        "x-user-id": TEST_USER_ID
    }
    
    print(f"\n📡 Making request to: {url}")
    print(f"👤 User ID: {TEST_USER_ID}")
    
    try:
        response = requests.get(url, headers=headers)
        
        print(f"\n✓ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n" + "=" * 60)
            print("SUBSCRIPTION INFO")
            print("=" * 60)
            if data.get("subscription"):
                sub = data["subscription"]
                print(f"Status: {sub['status']}")
                print(f"Plan: {sub['plan']['name']}")
                print(f"Price: ${sub['plan']['price_cents'] / 100:.2f}/{sub['plan']['interval']}")
                print(f"Tokens per period: {sub['plan']['tokens_per_period']}")
                print(f"Current period: {sub.get('current_period_start')} to {sub.get('current_period_end')}")
            else:
                print("No active subscription")
            
            print("\n" + "=" * 60)
            print("WALLET INFO")
            print("=" * 60)
            if data.get("wallet"):
                wallet = data["wallet"]
                print(f"Balance: {wallet['balance_tokens']} {wallet['currency']}")
                print(f"Last updated: {wallet.get('last_updated')}")
            else:
                print("No wallet found")
            
            print("\n" + "=" * 60)
            print(f"PAYMENT HISTORY ({len(data.get('payment_history', []))} records)")
            print("=" * 60)
            for payment in data.get("payment_history", [])[:5]:  # Show first 5
                print(f"[{payment['date']}] ${payment['amount_cents']/100:.2f} {payment['currency']}")
                print(f"  Status: {payment['status']}")
                print(f"  Description: {payment['description']}")
                print()
            
            print("\n" + "=" * 60)
            print(f"TRANSACTION HISTORY ({len(data.get('transaction_history', []))} records)")
            print("=" * 60)
            for tx in data.get("transaction_history", [])[:5]:  # Show first 5
                sign = "+" if tx['type'] == 'credit' else "-"
                print(f"[{tx['date']}] {sign}{tx['amount']} tokens")
                print(f"  Type: {tx['type']}")
                print(f"  Balance after: {tx['balance_after']}")
                print(f"  Description: {tx['description']}")
                print()
            
            print("\n" + "=" * 60)
            print(f"USAGE HISTORY ({len(data.get('usage_history', []))} records)")
            print("=" * 60)
            for usage in data.get("usage_history", [])[:5]:  # Show first 5
                print(f"[{usage['date']}] {usage['feature']}")
                print(f"  Tokens used: {usage['amount']}")
                if usage.get('cost_cents'):
                    print(f"  Cost: ${usage['cost_cents']/100:.2f}")
                print()
            
            print("\n" + "=" * 60)
            print("✅ TEST PASSED - All data retrieved successfully!")
            print("=" * 60)
            
            # Save full response to file
            with open("/tmp/billing_details_response.json", "w") as f:
                json.dump(data, f, indent=2, default=str)
            print(f"\n💾 Full response saved to: /tmp/billing_details_response.json")
            
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to the server.")
        print(f"Make sure the server is running at {BASE_URL}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_billing_details()
