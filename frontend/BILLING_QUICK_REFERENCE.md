# Quick Reference: Subscription & Billing Features

## 🎯 What's New

### New Subscription Page (`/subscription`)
A comprehensive billing management interface where users can:
- View their current plan and subscription status
- Check token balance and usage
- Review payment history
- Track transaction history (credits/debits)
- Monitor feature usage
- Manage or cancel their subscription

### Enhanced Dashboard (`/dashboard`)
- **New "View Billing" button** - Quick access to subscription page
- **New "Manage" button** - Opens Stripe Customer Portal
- Better visual layout for account management

### Enhanced Pricing Page (`/pricing`)
- **Active subscription banner** - Shows current plan when user is subscribed
- **Direct link to subscription management** - Easy access to billing details
- Prevents accidental re-subscription to current plan

## 🔑 Key Features

### 1. Subscription Overview
```
Location: /subscription (Overview tab)
```
- Current plan details (name, price, interval)
- Token balance with monthly allowance
- Next billing date
- Subscription status
- Recent transaction history

### 2. Payment History
```
Location: /subscription (Payment History tab)
```
- Complete payment record
- Status indicators (succeeded/failed/pending)
- Invoice links
- Sortable table view

### 3. Usage Tracking
```
Location: /subscription (Usage History tab)
```
- Feature-by-feature breakdown
- Token consumption per feature
- Timestamps for all usage
- Cost tracking

### 4. Subscription Management
```
Actions available:
```
- **Manage Subscription** → Opens Stripe Customer Portal
  - Update payment method
  - View invoices
  - Change billing details
  
- **View All Plans** → Redirects to pricing page
  - Compare plans
  - Upgrade/downgrade
  
- **Cancel Subscription** → Cancel at period end
  - Confirmation dialog
  - Retains access until period end

## 🚀 User Flows

### View Billing Details
```
Dashboard → Click "View Billing" → Subscription Page
```

### Manage Payment Method
```
Dashboard/Subscription → Click "Manage" → Stripe Portal → Update Card
```

### Upgrade Plan
```
Pricing Page → Select New Plan → Stripe Checkout → Success → Dashboard
```

### Cancel Subscription
```
Subscription Page → Scroll to Danger Zone → Cancel → Confirm
```

### Check Usage
```
Subscription Page → Click "Usage History" tab → View breakdown
```

## 🎨 UI Components

### Transaction Cards
- **Green cards** = Credits (money in, tokens added)
- **Red cards** = Debits (tokens used)
- Shows: Description, timestamp, amount, balance after

### Status Badges
- **Green with ✓** = Succeeded/Active
- **Red with ✗** = Failed/Canceled
- **Yellow with ⏱** = Pending

### Plan Card (Top of subscription page)
- Purple gradient background
- Large price display
- Three info boxes: Tokens, Billing, Status
- Action buttons at bottom

## 📊 Data Displayed

### Transaction Types
**Credits (Green):**
- Welcome bonus - [Plan]
- Monthly allowance - [Plan]
- Token grant
- Token purchase
- Bonus tokens

**Debits (Red):**
- Used for [feature_name]
- Scholarship Application
- Interview Session
- Resume Processing
- Essay Generation

### Payment Statuses
- **Succeeded** ✓ - Payment processed successfully
- **Failed** ✗ - Payment declined or error
- **Pending** ⏱ - Payment processing

## 🔒 Security

### Authentication
- All pages require login
- Automatic redirect to sign-in if not authenticated
- User ID from Logto used for all API calls

### Server-Side Validation
- Plan prices fetched from database
- Cannot manipulate pricing client-side
- Stripe webhook verification
- User ID verification on all endpoints

## 🛠️ API Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/billing/plans` | GET | Fetch available plans |
| `/api/billing/details` | GET | Get user's billing info |
| `/api/stripe/create-checkout-session` | POST | Start plan upgrade |
| `/api/stripe/create-portal-session` | POST | Open Stripe portal |
| `/api/subscription/cancel` | POST | Cancel subscription |

## 💡 Tips for Users

1. **Check your token balance regularly** - Visible on dashboard and subscription page
2. **Review usage history** - Understand which features consume the most tokens
3. **Use Stripe Portal for payment updates** - Secure, PCI-compliant payment management
4. **Cancel before renewal** - Cancellation takes effect at period end
5. **Export payment history** - Use for expense tracking (feature coming soon)

## 🐛 Troubleshooting

### "Failed to load billing data"
- Check internet connection
- Verify authentication (try logging out and back in)
- Contact support if persists

### Stripe Portal won't open
- Ensure popup blocker is disabled
- Try different browser
- Check if you have an active subscription

### Payment not showing
- Wait a few minutes for webhook processing
- Refresh the page
- Check Stripe dashboard directly

## 📱 Mobile Responsive

All pages are fully responsive:
- Tables scroll horizontally on mobile
- Cards stack vertically
- Buttons resize appropriately
- Touch-friendly tap targets

## 🎯 Next Features (Roadmap)

- [ ] Export payment history to CSV/PDF
- [ ] Usage analytics charts
- [ ] Token consumption trends
- [ ] Low balance notifications
- [ ] Auto-reload tokens
- [ ] Spending limits
- [ ] Custom billing alerts

---

**Need Help?** Contact support or visit the documentation at `/support`
