# Billing and Token System Fixes

## Issues Fixed

### 1. Subscription Not Updating After Payment ✅

**Problem:**
When a user with a free plan purchased a paid subscription, the webhook created a duplicate subscription instead of updating the existing one. This caused:
- User still showing as "Free" plan
- Tokens not being granted
- Multiple active subscriptions in database

**Root Cause:**
The `_handle_checkout_completed` method in `stripe_service.py` always created a new `Subscription` record without checking for existing subscriptions.

**Solution:**
Updated the webhook handler to:
1. Check if user has an existing active subscription
2. If yes, update it with the new plan details
3. If no, create a new subscription
4. Always grant tokens and record transaction

**Code Changes:**
```python
# Check if user has existing subscription (e.g., free plan)
existing_sub = db.query(Subscription).filter(
    Subscription.user_id == user_id,
    Subscription.status == 'active'
).first()

if existing_sub:
    # Update existing subscription to paid plan
    existing_sub.plan_id = plan_id
    existing_sub.status = 'active'
    existing_sub.current_period_start = datetime.fromtimestamp(stripe_sub.current_period_start)
    existing_sub.current_period_end = datetime.fromtimestamp(stripe_sub.current_period_end)
    existing_sub.external_subscription_id = subscription_id
    subscription = existing_sub
else:
    # Create new subscription record
    subscription = Subscription(...)
    db.add(subscription)
```

**Testing:**
1. Create a user (gets free plan automatically)
2. Purchase a paid plan via Stripe checkout
3. Webhook should update the subscription, not create a duplicate
4. User should see new plan in dashboard
5. Tokens should be granted

---

### 2. Tokens Not Deducted When Starting Workflow ✅

**Problem:**
When users started a workflow via `/api/workflow/start`, tokens were not being deducted from their wallet. This meant:
- Users could run unlimited workflows regardless of token balance
- No usage tracking
- No transaction history for workflow usage

**Root Cause:**
The workflow start endpoint had no token checking or deduction logic.

**Solution:**
Added comprehensive token management to the workflow start endpoint:
1. Check user has sufficient tokens (50 tokens required)
2. Return 402 Payment Required if insufficient
3. Deduct tokens from wallet before starting workflow
4. Record wallet transaction
5. Record usage in usage_records table

**Code Changes:**
```python
# Check user has sufficient tokens
WORKFLOW_TOKEN_COST = 50  # Cost to run a workflow

if x_user_id:
    user = UserOperations.create_if_not_exists(db, x_user_id)
    wallet = db.query(UserWallet).filter(UserWallet.user_id == x_user_id).first()
    
    if not wallet or wallet.balance_tokens < WORKFLOW_TOKEN_COST:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Insufficient tokens. Required: {WORKFLOW_TOKEN_COST}, Available: {wallet.balance_tokens if wallet else 0}"
        )
    
    # Deduct tokens
    old_balance = wallet.balance_tokens
    wallet.balance_tokens -= WORKFLOW_TOKEN_COST
    wallet.updated_at = datetime.utcnow()

# After creating workflow session, record transaction and usage
transaction = WalletTransaction(
    user_id=x_user_id,
    amount=-WORKFLOW_TOKEN_COST,
    balance_after=wallet.balance_tokens,
    kind='deduction',
    reference_id=workflow_session_id,
    metadata_json={'resource_type': 'workflow', 'scholarship_url': scholarship_url}
)
db.add(transaction)

usage = UsageRecord(
    user_id=x_user_id,
    resource_type='workflow',
    resource_id=workflow_session_id,
    tokens_used=WORKFLOW_TOKEN_COST,
    metadata_json={'scholarship_url': scholarship_url}
)
db.add(usage)
```

**Testing:**
1. Check user's token balance
2. Start a workflow
3. Verify 50 tokens were deducted
4. Check transaction history shows deduction
5. Check usage history shows workflow usage
6. Try starting workflow with insufficient tokens (should fail with 402)

---

## Additional Improvements

### Enhanced Logging

Added detailed logging to both fixes for easier debugging:

**Stripe Webhook:**
```python
print(f"✓ [Webhook] Processing checkout for user {user_id}, plan {plan_id}")
print(f"✓ [Webhook] Updating existing subscription {existing_sub.id}")
print(f"✓ [Webhook] Granted {plan.tokens_per_period} tokens. Balance: {old_balance} → {wallet.balance_tokens}")
print(f"✓ [Webhook] Checkout completed successfully")
```

**Workflow Start:**
```python
print(f"💰 [Workflow] Deducted {WORKFLOW_TOKEN_COST} tokens from user {x_user_id}. Balance: {old_balance} → {wallet.balance_tokens}")
```

---

## Token Costs Reference

| Resource | Token Cost |
|----------|------------|
| Workflow (Full Application) | 50 tokens |
| Interview Session | TBD |
| Resume Upload | TBD |
| Essay Generation | TBD |

---

## Testing Checklist

### Subscription Update Test
- [ ] User starts with free plan (100 tokens)
- [ ] User purchases Pro plan ($29/month)
- [ ] Stripe webhook fires
- [ ] Subscription updates to Pro (not duplicate)
- [ ] User receives 2000 additional tokens
- [ ] Dashboard shows Pro plan
- [ ] Transaction history shows "Monthly allowance - Pro"

### Token Deduction Test
- [ ] User has 100 tokens
- [ ] User starts workflow
- [ ] Balance reduces to 50 tokens
- [ ] Transaction history shows "-50 tokens - Used for workflow"
- [ ] Usage history shows "Scholarship Application - 50 tokens"
- [ ] User with 40 tokens cannot start workflow (402 error)

### End-to-End Flow Test
1. New user signs up → Gets free plan with 100 tokens
2. User starts 2 workflows → 0 tokens remaining
3. User tries to start 3rd workflow → 402 Payment Required
4. User purchases Pro plan → Gets 2000 tokens
5. User can now start workflows again
6. Dashboard shows correct plan and token balance

---

## Database Schema Impact

### Tables Modified

**subscriptions:**
- `external_subscription_id` now gets populated on upgrade
- `plan_id` gets updated when upgrading from free to paid

**user_wallets:**
- `balance_tokens` decreases on workflow start
- `updated_at` updates on every transaction

**wallet_transactions:**
- New records for workflow token deductions
- `kind` = 'deduction'
- `amount` = negative value (e.g., -50)

**usage_records:**
- New records for each workflow started
- `resource_type` = 'workflow'
- `tokens_used` = 50

---

## Error Handling

### Insufficient Tokens (402)
```json
{
  "detail": "Insufficient tokens. Required: 50, Available: 30"
}
```

**Frontend should:**
1. Show error message to user
2. Display current token balance
3. Offer link to purchase more tokens or upgrade plan

### Webhook Errors
All webhook errors are now logged with detailed information for debugging.

---

## Next Steps

Consider implementing token costs for other resources:
- Interview sessions
- Resume uploads
- Essay generation
- Resume optimization

Each should follow the same pattern:
1. Check balance
2. Deduct tokens
3. Record transaction
4. Record usage
5. Perform action
