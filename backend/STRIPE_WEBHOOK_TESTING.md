# Testing Stripe Webhooks Locally

## Problem
When testing Stripe webhooks locally, you're getting **400 Bad Request** errors because the webhook endpoint requires a valid `stripe-signature` header that only Stripe can generate.

## Solution: Use Stripe CLI

### 1. Install Stripe CLI

**macOS:**
```bash
brew install stripe/stripe-cli/stripe
```

**Other platforms:**
Visit https://stripe.com/docs/stripe-cli

### 2. Login to Stripe
```bash
stripe login
```

This will open your browser to authenticate with your Stripe account.

### 3. Forward Webhooks to Your Local Server

**Start your backend server:**
```bash
cd backend
uvicorn api:app --reload
```

**In a new terminal, start the Stripe CLI listener:**
```bash
stripe listen --forward-to localhost:8000/api/stripe/webhook
```

You'll see output like:
```
> Ready! Your webhook signing secret is whsec_xxxxxxxxxxxxx (^C to quit)
```

### 4. Update Your .env File

Copy the webhook signing secret from the Stripe CLI output and add it to your `.env` file:

```bash
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
```

**Important:** This is different from your production webhook secret. The CLI generates a temporary secret for local testing.

### 5. Trigger Test Events

**Option A: Use Stripe CLI to trigger events**
```bash
# Test checkout session completed
stripe trigger checkout.session.completed

# Test payment succeeded
stripe trigger payment_intent.succeeded

# Test subscription created
stripe trigger customer.subscription.created

# Test subscription updated
stripe trigger customer.subscription.updated

# Test subscription deleted
stripe trigger customer.subscription.deleted
```

**Option B: Use Stripe Dashboard**
1. Go to your Stripe Dashboard
2. Create a test checkout session or subscription
3. The webhook will be forwarded to your local server

### 6. Monitor Webhook Events

You'll see webhook events in three places:

**1. Stripe CLI output:**
```
2023-01-01 12:00:00   --> checkout.session.completed [evt_xxxxx]
2023-01-01 12:00:00   <-- [200] POST http://localhost:8000/api/stripe/webhook [evt_xxxxx]
```

**2. Your backend logs:**
```
✓ [Webhook] Processing event with signature
✓ [Webhook] Event type: checkout.session.completed
```

**3. Stripe Dashboard:**
- Go to Developers → Webhooks
- Click on your webhook endpoint
- View the event log

## Common Issues

### Issue 1: 400 Bad Request - Missing Signature
**Cause:** You're sending requests directly to the webhook endpoint without using Stripe CLI.

**Solution:** Always use Stripe CLI (`stripe listen`) for local testing. Don't send manual POST requests.

### Issue 2: Webhook Secret Not Set
**Error:** `No webhook secret configured`

**Solution:** Make sure `STRIPE_WEBHOOK_SECRET` is set in your `.env` file with the secret from `stripe listen`.

### Issue 3: Port Mismatch
**Error:** Connection refused

**Solution:** Make sure:
- Your backend is running on port 8000
- The `--forward-to` URL matches your server: `localhost:8000/api/stripe/webhook`

### Issue 4: Events Not Being Received
**Cause:** Stripe CLI not running or wrong endpoint

**Solution:**
1. Check that `stripe listen` is running
2. Verify the endpoint URL is correct
3. Check your backend logs for errors

## Testing Specific Scenarios

### Test Successful Subscription Creation
```bash
# 1. Start Stripe listener
stripe listen --forward-to localhost:8000/api/stripe/webhook

# 2. In another terminal, trigger the event
stripe trigger checkout.session.completed
```

### Test Subscription Cancellation
```bash
stripe trigger customer.subscription.deleted
```

### Test Payment Failure
```bash
stripe trigger invoice.payment_failed
```

### Test Subscription Update
```bash
stripe trigger customer.subscription.updated
```

## Production Webhook Setup

For production, you'll configure webhooks in the Stripe Dashboard:

1. Go to Developers → Webhooks
2. Click "Add endpoint"
3. Enter your production URL: `https://yourdomain.com/api/stripe/webhook`
4. Select events to listen to:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Copy the webhook signing secret
6. Add it to your production environment variables as `STRIPE_WEBHOOK_SECRET`

## Debugging Tips

### Enable Verbose Logging
The webhook endpoint now logs detailed information:
- Missing headers
- Available headers
- Payload size
- Event processing status
- Errors with stack traces

### Check Webhook Logs in Stripe Dashboard
1. Go to Developers → Webhooks
2. Click on your endpoint
3. View recent events and their responses

### Test with Real Checkout Flow
Instead of triggering events, test the full flow:

1. Start Stripe listener
2. Create a checkout session via your API
3. Complete the checkout in Stripe's test mode
4. Watch the webhook events flow through

```bash
# Get a checkout URL
curl -X POST http://localhost:8000/api/checkout/create \
  -H "x-user-id: test_user" \
  -H "Content-Type: application/json" \
  -d '{"plan_slug": "pro"}'

# Open the checkout URL in your browser
# Complete the test payment
# Watch the webhook events in Stripe CLI
```

## Quick Reference

| Command | Purpose |
|---------|---------|
| `stripe login` | Authenticate with Stripe |
| `stripe listen --forward-to localhost:8000/api/stripe/webhook` | Forward webhooks to local server |
| `stripe trigger <event>` | Trigger a test event |
| `stripe events list` | List recent events |
| `stripe events resend <event_id>` | Resend a specific event |

## Environment Variables

```bash
# .env file
STRIPE_SECRET_KEY=sk_test_xxxxxxxxxxxxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx  # From stripe listen
```

## Next Steps

1. ✅ Install Stripe CLI
2. ✅ Run `stripe listen`
3. ✅ Update `.env` with webhook secret
4. ✅ Trigger test events
5. ✅ Verify events are processed correctly
6. ✅ Check database for updated subscriptions/payments
