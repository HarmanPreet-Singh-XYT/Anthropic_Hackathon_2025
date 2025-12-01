# Billing Details API - Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND REQUEST                             │
│                                                                      │
│  GET /api/billing/details                                           │
│  Headers: { x-user-id: "user_123" }                                 │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      API ENDPOINT (api.py)                           │
│                                                                      │
│  1. Validate user_id header                                         │
│  2. Get/Create user & wallet                                        │
│  3. Fetch subscription info                                         │
│  4. Fetch payment history                                           │
│  5. Fetch transaction history                                       │
│  6. Fetch usage history                                             │
│  7. Format & return response                                        │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    DATABASE OPERATIONS                               │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ UserOperations.create_if_not_exists(db, user_id)             │  │
│  │   → Returns User with wallet & subscriptions                 │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Query SubscriptionPayment                                     │  │
│  │   → Filter by subscription_id                                │  │
│  │   → Order by created_at DESC                                 │  │
│  │   → Limit 20                                                 │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ WalletTransactionOperations.get_recent(db, user_id, 30)     │  │
│  │   → Filter by user_id                                        │  │
│  │   → Order by created_at DESC                                 │  │
│  │   → Limit 30                                                 │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ UsageRecordOperations.get_recent(db, user_id, 30)           │  │
│  │   → Filter by user_id                                        │  │
│  │   → Order by created_at DESC                                 │  │
│  │   → Limit 30                                                 │  │
│  └──────────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    DATABASE TABLES QUERIED                           │
│                                                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────────┐  │
│  │     users        │  │  user_wallets    │  │  subscriptions  │  │
│  ├──────────────────┤  ├──────────────────┤  ├─────────────────┤  │
│  │ id (PK)          │  │ user_id (PK/FK)  │  │ id (PK)         │  │
│  │ email            │  │ balance_tokens   │  │ user_id (FK)    │  │
│  │ created_at       │  │ currency         │  │ plan_id (FK)    │  │
│  └──────────────────┘  │ updated_at       │  │ status          │  │
│                        └──────────────────┘  │ current_period  │  │
│                                              └─────────────────┘  │
│                                                                      │
│  ┌──────────────────────────┐  ┌──────────────────────────────┐   │
│  │  subscription_payments   │  │   wallet_transactions        │   │
│  ├──────────────────────────┤  ├──────────────────────────────┤   │
│  │ id (PK)                  │  │ id (PK)                      │   │
│  │ subscription_id (FK)     │  │ user_id (FK)                 │   │
│  │ amount_cents             │  │ amount                       │   │
│  │ currency                 │  │ balance_after                │   │
│  │ status                   │  │ kind                         │   │
│  │ external_payment_id      │  │ reference_id                 │   │
│  │ created_at               │  │ metadata_json                │   │
│  └──────────────────────────┘  │ created_at                   │   │
│                                └──────────────────────────────┘   │
│                                                                      │
│  ┌──────────────────────────┐                                      │
│  │     usage_records        │                                      │
│  ├──────────────────────────┤                                      │
│  │ id (PK)                  │                                      │
│  │ user_id (FK)             │                                      │
│  │ resource_type            │                                      │
│  │ resource_id              │                                      │
│  │ tokens_used              │                                      │
│  │ cost_cents               │                                      │
│  │ metadata_json            │                                      │
│  │ created_at               │                                      │
│  └──────────────────────────┘                                      │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      RESPONSE FORMATTING                             │
│                                                                      │
│  Payment History:                                                   │
│    - Map SubscriptionPayment → PaymentHistoryItem                  │
│    - Add plan name to description                                  │
│    - Format status with emoji                                      │
│                                                                      │
│  Transaction History:                                               │
│    - Map WalletTransaction → TransactionHistoryItem                │
│    - Determine type (credit/debit) from kind                       │
│    - Generate smart descriptions from metadata                     │
│    - Show absolute amounts                                         │
│                                                                      │
│  Usage History:                                                     │
│    - Map UsageRecord → UsageHistoryItem                            │
│    - Translate resource_type to user-friendly names                │
│    - Format token amounts                                          │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         JSON RESPONSE                                │
│                                                                      │
│  {                                                                  │
│    "subscription": { ... },                                         │
│    "wallet": { ... },                                               │
│    "payment_history": [                                             │
│      {                                                              │
│        "id": "pay_123",                                             │
│        "amount_cents": 2900,                                        │
│        "currency": "USD",                                           │
│        "status": "succeeded",                                       │
│        "date": "2023-01-01T00:00:00",                               │
│        "description": "Payment for Pro subscription"                │
│      }                                                              │
│    ],                                                               │
│    "transaction_history": [                                         │
│      {                                                              │
│        "id": "tx_789",                                              │
│        "amount": 2000,                                              │
│        "type": "credit",                                            │
│        "balance_after": 2500,                                       │
│        "description": "Monthly allowance - Pro",                    │
│        "date": "2023-01-01T00:00:00"                                │
│      }                                                              │
│    ],                                                               │
│    "usage_history": [                                               │
│      {                                                              │
│        "id": "usage_678",                                           │
│        "feature": "Scholarship Application",                        │
│        "amount": 50,                                                │
│        "cost_cents": null,                                          │
│        "date": "2023-01-10T14:30:00"                                │
│      }                                                              │
│    ]                                                                │
│  }                                                                  │
└─────────────────────────────────────────────────────────────────────┘


TRANSACTION KIND MAPPING:
═════════════════════════

┌──────────────┬──────────┬────────────────────────────────────────┐
│ Kind         │ Type     │ Description Example                    │
├──────────────┼──────────┼────────────────────────────────────────┤
│ grant        │ credit   │ "Welcome bonus - Pro"                  │
│              │          │ "Monthly allowance - Pro"              │
│              │          │ "Token grant"                          │
├──────────────┼──────────┼────────────────────────────────────────┤
│ purchase     │ credit   │ "Token purchase"                       │
├──────────────┼──────────┼────────────────────────────────────────┤
│ bonus        │ credit   │ "Bonus tokens"                         │
├──────────────┼──────────┼────────────────────────────────────────┤
│ deduction    │ debit    │ "Used for workflow"                    │
│              │          │ "Token usage - service"                │
└──────────────┴──────────┴────────────────────────────────────────┘


RESOURCE TYPE MAPPING:
══════════════════════

┌──────────────────┬────────────────────────────────┐
│ resource_type    │ User-Friendly Feature Name     │
├──────────────────┼────────────────────────────────┤
│ workflow         │ Scholarship Application        │
│ interview        │ Interview Session              │
│ resume_upload    │ Resume Processing              │
│ essay_generation │ Essay Generation               │
│ (other)          │ (shown as-is)                  │
└──────────────────┴────────────────────────────────┘
```
