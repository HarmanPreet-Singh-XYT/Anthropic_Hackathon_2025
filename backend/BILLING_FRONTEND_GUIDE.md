# Billing Details API - Frontend Quick Reference

## Endpoint

```
GET /api/billing/details
```

## Headers

```javascript
{
  'x-user-id': 'user_id_here'  // Required
}
```

## Response TypeScript Interfaces

```typescript
interface BillingDetailsResponse {
  subscription: SubscriptionInfo | null;
  wallet: WalletInfo | null;
  payment_history: PaymentHistoryItem[];
  transaction_history: TransactionHistoryItem[];
  usage_history: UsageHistoryItem[];
}

interface SubscriptionInfo {
  status: string;  // "active", "canceled", "past_due"
  plan: PlanInfo;
  current_period_start: string | null;  // ISO 8601 datetime
  current_period_end: string | null;    // ISO 8601 datetime
}

interface PlanInfo {
  name: string;                    // "Free", "Starter", "Pro", "Pro Annual"
  interval: string;                // "month" or "year"
  price_cents: number;             // Price in cents (e.g., 2900 = $29.00)
  tokens_per_period: number;       // Tokens granted per billing period
  features: Record<string, any>;   // Plan features
}

interface WalletInfo {
  balance_tokens: number;          // Current token balance
  currency: string;                // "TOK"
  last_updated: string | null;     // ISO 8601 datetime
}

interface PaymentHistoryItem {
  id: string;                      // Payment ID
  amount_cents: number;            // Amount in cents
  currency: string;                // "USD"
  status: string;                  // "succeeded", "failed", "pending"
  date: string;                    // ISO 8601 datetime
  description: string;             // Human-readable description
}

interface TransactionHistoryItem {
  id: string;                      // Transaction ID
  amount: number;                  // Token amount (absolute value)
  type: 'credit' | 'debit';        // Transaction type
  balance_after: number;           // Balance after transaction
  description: string;             // Human-readable description
  date: string;                    // ISO 8601 datetime
}

interface UsageHistoryItem {
  id: string;                      // Usage record ID
  feature: string;                 // Feature name
  amount: number;                  // Tokens consumed
  cost_cents: number | null;       // Optional cost in cents
  date: string;                    // ISO 8601 datetime
}
```

## Usage Examples

### React Hook Example

```typescript
import { useState, useEffect } from 'react';

interface UseBillingDetailsResult {
  data: BillingDetailsResponse | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useBillingDetails(userId: string): UseBillingDetailsResult {
  const [data, setData] = useState<BillingDetailsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchBillingDetails = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/billing/details', {
        headers: {
          'x-user-id': userId
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (userId) {
      fetchBillingDetails();
    }
  }, [userId]);

  return { data, loading, error, refetch: fetchBillingDetails };
}
```

### Component Example

```typescript
import React from 'react';
import { useBillingDetails } from './hooks/useBillingDetails';

export function BillingDashboard({ userId }: { userId: string }) {
  const { data, loading, error } = useBillingDetails(userId);

  if (loading) return <div>Loading billing details...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!data) return <div>No billing data available</div>;

  return (
    <div className="billing-dashboard">
      {/* Subscription Section */}
      <section className="subscription-info">
        <h2>Current Subscription</h2>
        {data.subscription ? (
          <div>
            <p>Plan: {data.subscription.plan.name}</p>
            <p>Status: {data.subscription.status}</p>
            <p>Price: ${data.subscription.plan.price_cents / 100}/{data.subscription.plan.interval}</p>
            <p>Tokens: {data.subscription.plan.tokens_per_period} per {data.subscription.plan.interval}</p>
          </div>
        ) : (
          <p>No active subscription</p>
        )}
      </section>

      {/* Wallet Section */}
      <section className="wallet-info">
        <h2>Token Balance</h2>
        {data.wallet && (
          <div>
            <p className="balance">{data.wallet.balance_tokens} {data.wallet.currency}</p>
            <p className="updated">Last updated: {new Date(data.wallet.last_updated).toLocaleString()}</p>
          </div>
        )}
      </section>

      {/* Payment History */}
      <section className="payment-history">
        <h2>Payment History</h2>
        {data.payment_history.length > 0 ? (
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Description</th>
                <th>Amount</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {data.payment_history.map(payment => (
                <tr key={payment.id}>
                  <td>{new Date(payment.date).toLocaleDateString()}</td>
                  <td>{payment.description}</td>
                  <td>${(payment.amount_cents / 100).toFixed(2)}</td>
                  <td className={`status-${payment.status}`}>{payment.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>No payment history</p>
        )}
      </section>

      {/* Transaction History */}
      <section className="transaction-history">
        <h2>Token Transactions</h2>
        {data.transaction_history.length > 0 ? (
          <div className="transaction-list">
            {data.transaction_history.map(tx => (
              <div key={tx.id} className={`transaction transaction-${tx.type}`}>
                <div className="transaction-date">
                  {new Date(tx.date).toLocaleDateString()}
                </div>
                <div className="transaction-description">{tx.description}</div>
                <div className="transaction-amount">
                  {tx.type === 'credit' ? '+' : '-'}{tx.amount} tokens
                </div>
                <div className="transaction-balance">
                  Balance: {tx.balance_after}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p>No transaction history</p>
        )}
      </section>

      {/* Usage History */}
      <section className="usage-history">
        <h2>Usage History</h2>
        {data.usage_history.length > 0 ? (
          <div className="usage-list">
            {data.usage_history.map(usage => (
              <div key={usage.id} className="usage-item">
                <div className="usage-date">
                  {new Date(usage.date).toLocaleDateString()}
                </div>
                <div className="usage-feature">{usage.feature}</div>
                <div className="usage-amount">{usage.amount} tokens</div>
                {usage.cost_cents && (
                  <div className="usage-cost">
                    ${(usage.cost_cents / 100).toFixed(2)}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p>No usage history</p>
        )}
      </section>
    </div>
  );
}
```

### Vanilla JavaScript Example

```javascript
async function fetchBillingDetails(userId) {
  try {
    const response = await fetch('/api/billing/details', {
      headers: {
        'x-user-id': userId
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching billing details:', error);
    throw error;
  }
}

// Usage
fetchBillingDetails('user_123')
  .then(data => {
    console.log('Subscription:', data.subscription);
    console.log('Wallet:', data.wallet);
    console.log('Payments:', data.payment_history);
    console.log('Transactions:', data.transaction_history);
    console.log('Usage:', data.usage_history);
  })
  .catch(error => {
    console.error('Failed to load billing details:', error);
  });
```

## Common Use Cases

### 1. Display Current Plan and Balance

```typescript
function PlanSummary({ data }: { data: BillingDetailsResponse }) {
  const plan = data.subscription?.plan;
  const balance = data.wallet?.balance_tokens ?? 0;

  return (
    <div>
      <h3>{plan ? plan.name : 'Free'} Plan</h3>
      <p>{balance} tokens remaining</p>
    </div>
  );
}
```

### 2. Show Recent Payments

```typescript
function RecentPayments({ payments }: { payments: PaymentHistoryItem[] }) {
  const recent = payments.slice(0, 5);
  
  return (
    <ul>
      {recent.map(payment => (
        <li key={payment.id}>
          {payment.description} - ${(payment.amount_cents / 100).toFixed(2)}
          <span className={payment.status}>{payment.status}</span>
        </li>
      ))}
    </ul>
  );
}
```

### 3. Calculate Token Usage Stats

```typescript
function calculateUsageStats(usageHistory: UsageHistoryItem[]) {
  const totalTokens = usageHistory.reduce((sum, item) => sum + item.amount, 0);
  
  const byFeature = usageHistory.reduce((acc, item) => {
    acc[item.feature] = (acc[item.feature] || 0) + item.amount;
    return acc;
  }, {} as Record<string, number>);

  return { totalTokens, byFeature };
}
```

### 4. Format Transaction Timeline

```typescript
function TransactionTimeline({ transactions }: { transactions: TransactionHistoryItem[] }) {
  return (
    <div className="timeline">
      {transactions.map(tx => (
        <div key={tx.id} className={`timeline-item ${tx.type}`}>
          <time>{new Date(tx.date).toLocaleString()}</time>
          <p>{tx.description}</p>
          <span className="amount">
            {tx.type === 'credit' ? '+' : '-'}{tx.amount}
          </span>
          <span className="balance">Balance: {tx.balance_after}</span>
        </div>
      ))}
    </div>
  );
}
```

## Error Handling

```typescript
try {
  const response = await fetch('/api/billing/details', {
    headers: { 'x-user-id': userId }
  });

  if (response.status === 401) {
    // User not authenticated
    console.error('User ID required');
  } else if (response.status === 500) {
    // Server error
    const error = await response.json();
    console.error('Server error:', error.detail);
  } else if (!response.ok) {
    // Other errors
    console.error('Request failed:', response.status);
  } else {
    const data = await response.json();
    // Process data
  }
} catch (error) {
  // Network error
  console.error('Network error:', error);
}
```

## Tips

1. **Cache the data**: Billing details don't change frequently, consider caching for 5-10 minutes
2. **Pagination**: The API limits results (20 payments, 30 transactions, 30 usage records)
3. **Date formatting**: All dates are in ISO 8601 format, use `new Date()` to parse
4. **Currency conversion**: Amounts in cents need to be divided by 100 for display
5. **Null checks**: Always check for null values in subscription and wallet
6. **Token balance**: Can be 0 or negative if user has overspent
7. **Transaction types**: Use the `type` field to determine if tokens were added or removed
