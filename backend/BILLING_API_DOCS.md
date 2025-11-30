# Billing & Subscription System Documentation

## Overview
This document describes the complete billing and subscription system, including security measures to prevent pricing manipulation.

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
Fetch comprehensive billing information.

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
      "tokens_per_period": 2000
    },
    "current_period_start": "2023-01-01T00:00:00",
    "current_period_end": "2023-02-01T00:00:00"
  },
  "wallet": {
    "balance_tokens": 1000,
    "currency": "TOK",
    "last_updated": "2023-01-01T00:00:00"
  },
  "payment_history": [...],
  "transaction_history": [...],
  "usage_history": [...]
}
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
