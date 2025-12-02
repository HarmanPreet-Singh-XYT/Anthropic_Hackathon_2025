# Billing & Subscription System Documentation

## Overview
## Overview
This document describes the complete billing and subscription system, including security measures to prevent pricing manipulation.

**Note:** New users are automatically assigned the "Free" subscription plan upon account creation, which includes an initial token grant.


## Security Measures

### 1. Server-Side Plan Validation
All billing plans are stored in the database and validated server-side. The client **cannot** manipulate pricing.

**How it works:**
- Plans are predefined and seeded into the database on server startup
- When a checkout session is created, the server validates the `plan_slug` against the database
- The actual price is fetched from the database, not from the client request
- This prevents users from tampering with prices in the frontend

### 2. Automatic Plan Seeding
On server startup, the system automatically seeds billing plans if they don't exist.

**Predefined Plans:**
```python
plans = [
    {
        "slug": "free",
        "name": "Free",
        "price_cents": 0,
        "interval": "month",
        "tokens_per_period": 100,
        "features": {"max_applications": 5, "support": "community"}
    },
    {
        "slug": "starter",
        "name": "Starter",
        "price_cents": 999,  # $9.99
        "interval": "month",
        "tokens_per_period": 500,
        "features": {"max_applications": 25, "support": "email"}
    },
    {
        "slug": "pro",
        "name": "Pro",
        "price_cents": 2900,  # $29.00
        "interval": "month",
        "tokens_per_period": 2000,
        "features": {"max_applications": -1, "support": "priority"}
    },
    {
        "slug": "pro-annual",
        "name": "Pro Annual",
        "price_cents": 29000,  # $290.00
        "interval": "year",
        "tokens_per_period": 24000,
        "features": {"annual_discount": true}
    }
]
```

## API Endpoints

### 1. Get Billing Plans
Fetch all available subscription plans from the database.

**Endpoint:** `GET /api/billing/plans`

**Response:**
```json
{
  "plans": [
    {
      "id": "uuid",
      "slug": "pro",
      "name": "Pro",
      "price_cents": 2900,
      "interval": "month",
      "tokens_per_period": 2000,
      "features": {...}
    }
  ]
}
```

**Frontend Usage:**
```javascript
const response = await fetch('/api/billing/plans');
const { plans } = await response.json();
// Display plans to user
```

---

### 2. Create Checkout Session
Create a Stripe checkout session. **Server validates the plan slug.**

**Endpoint:** `POST /api/stripe/create-checkout-session`

**Headers:**
- `x-user-id`: User ID (required)

**Form Data:**
- `plan_slug`: The slug of the plan (e.g., "pro")
- `success_url`: Redirect URL on success
- `cancel_url`: Redirect URL on cancel

**Server-Side Validation:**
```python
# Server validates plan_slug exists in database
_validate_plan_slug(db, plan_slug)

# Server fetches actual price from database
plan = db.query(BillingPlan).filter(BillingPlan.slug == plan_slug).first()

# Stripe session is created with database price, not client price
```

**Response:**
```json
{
  "session_id": "cs_test_...",
  "url": "https://checkout.stripe.com/..."
}
```

**Frontend Usage:**
```javascript
const formData = new FormData();
formData.append('plan_slug', 'pro');  // Only send slug, not price
formData.append('success_url', 'https://myapp.com/success');
formData.append('cancel_url', 'https://myapp.com/cancel');

const response = await fetch('/api/stripe/create-checkout-session', {
  method: 'POST',
  headers: {
    'x-user-id': userId
  },
  body: formData
});

const { url } = await response.json();
window.location.href = url;  // Redirect to Stripe
```

---

### 3. Create Portal Session
Create a Stripe customer portal session for managing subscriptions.

**Endpoint:** `POST /api/stripe/create-portal-session`

**Headers:**
- `x-user-id`: User ID (required)

**Form Data:**
- `return_url`: URL to return to after portal session

**Response:**
```json
{
  "url": "https://billing.stripe.com/..."
}
```

---

### 4. Cancel Subscription
Cancel the user's active subscription at the end of the billing period.

**Endpoint:** `POST /api/subscription/cancel`

**Headers:**
- `x-user-id`: User ID (required)

**Response:**
```json
{
  "status": "canceled",
  "message": "Subscription will be canceled at the end of the period"
}
```

---

### 5. Get Billing Details
Fetch comprehensive billing information including payment history, transaction history, and usage history.

**Endpoint:** `GET /api/billing/details`

**Headers:**
- `x-user-id`: User ID (required)

**Response:**
```json
{
  "subscription": {
    "status": "active",
    "plan": {
      "name": "Pro",
      "interval": "month",
      "price_cents": 2900,
      "tokens_per_period": 2000,
      "features": {
        "max_applications": -1,
        "support": "priority",
        "priority_processing": true,
        "advanced_analytics": true
      }
    },
    "current_period_start": "2023-01-01T00:00:00",
    "current_period_end": "2023-02-01T00:00:00"
  },
  "wallet": {
    "balance_tokens": 1500,
    "currency": "TOK",
    "last_updated": "2023-01-15T10:30:00"
  },
  "payment_history": [
    {
      "id": "pay_123abc",
      "amount_cents": 2900,
      "currency": "USD",
      "status": "succeeded",
      "date": "2023-01-01T00:00:00",
      "description": "Payment for Pro subscription"
    },
    {
      "id": "pay_456def",
      "amount_cents": 2900,
      "currency": "USD",
      "status": "succeeded",
      "date": "2022-12-01T00:00:00",
      "description": "Payment for Pro subscription"
    }
  ],
  "transaction_history": [
    {
      "id": "tx_789ghi",
      "amount": 2000,
      "type": "credit",
      "balance_after": 2500,
      "description": "Monthly allowance - Pro",
      "date": "2023-01-01T00:00:00"
    },
    {
      "id": "tx_012jkl",
      "amount": 50,
      "type": "debit",
      "balance_after": 500,
      "description": "Used for workflow",
      "date": "2023-01-10T14:30:00"
    },
    {
      "id": "tx_345mno",
      "amount": 2000,
      "type": "credit",
      "balance_after": 2000,
      "description": "Welcome bonus - Pro",
      "date": "2022-12-01T00:00:00"
    }
  ],
  "usage_history": [
    {
      "id": "usage_678pqr",
      "feature": "Scholarship Application",
      "amount": 50,
      "cost_cents": null,
      "date": "2023-01-10T14:30:00"
    },
    {
      "id": "usage_901stu",
      "feature": "Interview Session",
      "amount": 30,
      "cost_cents": null,
      "date": "2023-01-10T15:00:00"
    },
    {
      "id": "usage_234vwx",
      "feature": "Resume Processing",
      "amount": 10,
      "cost_cents": null,
      "date": "2023-01-09T09:00:00"
    },
    {
      "id": "usage_567yza",
      "feature": "Essay Generation",
      "amount": 40,
      "cost_cents": null,
      "date": "2023-01-08T16:45:00"
    }
  ]
}
```

**Payment History Details:**
- Shows all subscription payments (succeeded and failed)
- Includes payment amount, currency, status, and date
- Descriptions indicate which plan the payment was for
- Sorted by date (most recent first)
- Limited to last 20 payments

**Transaction History Details:**
- Shows all wallet token transactions
- **Types:**
  - `credit`: Tokens added (grant, purchase, bonus)
  - `debit`: Tokens deducted (usage)
- **Descriptions:**
  - "Welcome bonus - [Plan]": Initial tokens when subscribing
  - "Monthly allowance - [Plan]": Recurring tokens from subscription
  - "Token grant": Other token grants
  - "Token purchase": Direct token purchases
  - "Bonus tokens": Promotional bonuses
  - "Used for [resource_type]": Token deductions for services
- Shows balance after each transaction
- Sorted by date (most recent first)
- Limited to last 30 transactions

**Usage History Details:**
- Shows resource consumption records
- **Features:**
  - "Scholarship Application": Full workflow execution
  - "Interview Session": Interview interactions
  - "Resume Processing": Resume upload and analysis
  - "Essay Generation": Essay writing service
- Shows tokens consumed per feature
- Optional cost in cents (for pay-per-use features)
- Sorted by date (most recent first)
- Limited to last 30 usage records

**Frontend Usage:**
```javascript
const response = await fetch('/api/billing/details', {
  headers: {
    'x-user-id': userId
  }
});

const data = await response.json();

// Display subscription info
console.log(`Plan: ${data.subscription.plan.name}`);
console.log(`Tokens: ${data.wallet.balance_tokens}`);

// Show payment history
data.payment_history.forEach(payment => {
  console.log(`${payment.date}: ${payment.description} - $${payment.amount_cents / 100}`);
});

// Show transaction history
data.transaction_history.forEach(tx => {
  const sign = tx.type === 'credit' ? '+' : '-';
  console.log(`${tx.date}: ${sign}${tx.amount} tokens - ${tx.description}`);
});

// Show usage history
data.usage_history.forEach(usage => {
  console.log(`${usage.date}: ${usage.feature} used ${usage.amount} tokens`);
});
```

---

### 6. Stripe Webhook
Endpoint for Stripe to send webhook events (subscription updates, payments, etc.).

**Endpoint:** `POST /api/stripe/webhook`

**Headers:**
- `stripe-signature`: Stripe signature (required)

**Body:** Raw JSON from Stripe

**Handled Events:**
- `checkout.session.completed` - New subscription created
- `customer.subscription.updated` - Subscription status changed
- `customer.subscription.deleted` - Subscription canceled
- `invoice.payment_succeeded` - Payment successful
- `invoice.payment_failed` - Payment failed

---

## Complete Flow

### Frontend Flow
```
1. User visits pricing page
   ↓
2. Frontend fetches plans: GET /api/billing/plans
   ↓
3. User selects a plan (e.g., "pro")
   ↓
4. Frontend sends only plan_slug to backend
   POST /api/stripe/create-checkout-session
   Body: { plan_slug: "pro" }  ← No price sent!
   ↓
5. Backend validates plan_slug and fetches price from database
   ↓
6. Backend creates Stripe session with database price
   ↓
7. User is redirected to Stripe checkout
   ↓
8. User completes payment
   ↓
9. Stripe sends webhook to backend
   ↓
10. Backend creates subscription and grants tokens
```

### Security Guarantees
✅ **Client cannot manipulate prices** - Only plan slug is sent, price comes from database  
✅ **Server-side validation** - Plan slug is validated before creating checkout  
✅ **Automatic seeding** - Plans are seeded on startup  
✅ **Webhook verification** - Stripe webhooks are verified with signature  
✅ **Database as source of truth** - All pricing comes from database  

---

## Manual Plan Seeding

If you need to manually seed plans (e.g., after database reset):

```bash
cd backend
python scripts/seed_billing_plans.py
```

---

## Environment Variables

Required Stripe configuration in `.env`:

```bash
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

---

## Testing

To test the billing flow:

1. **Get plans:**
   ```bash
   curl http://localhost:8000/api/billing/plans
   ```

2. **Create checkout (will validate plan):**
   ```bash
   curl -X POST http://localhost:8000/api/stripe/create-checkout-session \
     -H "x-user-id: test-user" \
     -F "plan_slug=pro" \
     -F "success_url=http://localhost:3000/success" \
     -F "cancel_url=http://localhost:3000/cancel"
   ```

3. **Test invalid plan (should fail):**
   ```bash
   curl -X POST http://localhost:8000/api/stripe/create-checkout-session \
     -H "x-user-id: test-user" \
     -F "plan_slug=fake-plan" \
     -F "success_url=http://localhost:3000/success" \
     -F "cancel_url=http://localhost:3000/cancel"
   ```
   Expected: `400 Bad Request - Invalid plan slug`
