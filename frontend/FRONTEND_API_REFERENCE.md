# Frontend API Reference - Request/Response Formats

This document shows exactly how the frontend sends requests and expects responses from the backend.

---

## 1. Upload Resume

**Frontend Function:** `uploadResume(file: File, userId: string)`  
**Location:** [lib/api.ts:68-86](file:///Users/harmanpreetsingh/Public/Code/Anthropic_Hack/frontend/lib/api.ts#L68-L86)

### Request
```http
POST /api/upload-resume HTTP/1.1
X-User-ID: <logto-user-id>
Content-Type: multipart/form-data

FormData:
  file: <PDF File Binary>
```

### Expected Response (200 OK)
```typescript
{
  success: boolean;
  message: string;
  chunks_stored: number;
  metadata: {
    session_id: string;           // ← CRITICAL: Frontend stores this
    filename: string;
    file_size_bytes: number;
    file_size_mb: number;
    text_preview: string | null;
  };
}
```

### Usage in Frontend
```typescript
// app/start/page.tsx:182
const uploadData = await uploadResume(file, user.sub);
const resumeSessionId = uploadData.metadata.session_id;
localStorage.setItem('resume_session_id', resumeSessionId);
```

---

## 2. Start Workflow

**Frontend Function:** `startWorkflow(scholarshipUrl: string, resumeSessionId: string, userId: string)`  
**Location:** [lib/api.ts:95-114](file:///Users/harmanpreetsingh/Public/Code/Anthropic_Hack/frontend/lib/api.ts#L95-L114)

### Request
```http
POST /api/workflow/start HTTP/1.1
X-User-ID: <logto-user-id>
Content-Type: multipart/form-data

FormData:
  scholarship_url: <string>
  resume_session_id: <string>    // ← From upload response
```

### Expected Response (200 OK)
```typescript
{
  session_id: string;             // ← Workflow session ID
  status: string;
  message: string;
}
```

### Usage in Frontend
```typescript
// app/start/page.tsx:205
const { session_id: workflowSessionId } = await startWorkflow(url, resumeSessionId, user.sub);
// Frontend then polls this workflow session
```

---

## 3. Get Workflow Status

**Frontend Function:** `getWorkflowStatus(sessionId: string, userId: string)`  
**Location:** [lib/api.ts:122-134](file:///Users/harmanpreetsingh/Public/Code/Anthropic_Hack/frontend/lib/api.ts#L122-L134)

### Request
```http
GET /api/workflow/status/{sessionId} HTTP/1.1
X-User-ID: <logto-user-id>
```

### Expected Response (200 OK)
```typescript
{
  session_id: string;
  status: 'processing' | 'waiting_for_input' | 'complete' | 'error';
  result: {
    matchmaker_results?: Record<string, unknown>;
    essay_draft?: string;
    gaps?: unknown[];
    match_score?: number;
  } | null;
  error: string | null;
}
```

### Usage in Frontend
```typescript
// app/start/page.tsx:236 (polling loop)
const statusData = await getWorkflowStatus(workflowSessionId, user.sub);
if (statusData.status === 'complete' || statusData.status === 'waiting_for_input') {
  router.push(`/matchmaker?session=${workflowSessionId}`);
}
```

---

## 4. Get Dashboard Data

**Frontend Function:** `getDashboardData(userId: string)`  
**Location:** [lib/api.ts:282-294](file:///Users/harmanpreetsingh/Public/Code/Anthropic_Hack/frontend/lib/api.ts#L282-L294)

### Request
```http
GET /api/dashboard HTTP/1.1
X-User-ID: <logto-user-id>
```

### Expected Response (200 OK)
```typescript
{
  user: {
    id: string;
    email: string | null;
  };
  wallet: {
    balance_tokens: number;
    currency: string;
    last_updated: string | null;    // ISO Date
  } | null;
  subscription: {
    status: string;
    plan: {
      name: string;
      interval: string;
      price_cents: number;
      tokens_per_period: number;
      features: Record<string, any> | null;
    };
    current_period_start: string | null;
    current_period_end: string | null;
  } | null;
  resume_sessions: Array<{
    id: string;                      // ← Should match resume_session_id from upload
    filename: string;
    file_size_bytes: number;
    created_at: string;
    text_preview: string | null;
    workflow_sessions: Array<{       // ← Should contain workflows started with this resume
      id: string;                    // ← Should match workflow session_id
      scholarship_url: string;
      status: string;
      match_score: number | null;
      created_at: string;
      updated_at: string | null;
      completed_at: string | null;
      applications: Array<{
        id: string;
        session_id: string;
        scholarship_url: string;
        status: string;
        match_score: number | null;
        had_interview: boolean;
        created_at: string;
      }>;
      interview_session: {
        id: string;
        current_target: string | null;
        created_at: string;
        completed_at: string | null;
      } | null;
    }>;
  }>;
  usage: {
    queries_today: number;
    queries_month: number;
    tokens_used_today: number;
    tokens_used_month: number;
  };
  recent_activity: Array<{
    type: string;
    ref_id: string;
    description: string;
    timestamp: string;
    amount?: number;
  }>;
}
```

### Usage in Frontend
```typescript
// app/dashboard/page.tsx:109
const data = await getDashboardData(user.sub);
const resumeSessions = data.resume_sessions || [];  // ← ISSUE: This is empty

// Frontend expects to iterate over resume sessions
resumeSessions.forEach(resume => {
  resume.workflow_sessions.forEach(workflow => {
    // Display workflow data
  });
});
```

---

## 5. Get Billing Plans

**Frontend Function:** `getBillingPlans()`  
**Location:** [lib/api.ts:359-367](file:///Users/harmanpreetsingh/Public/Code/Anthropic_Hack/frontend/lib/api.ts#L359-L367)

### Request
```http
GET /api/billing/plans HTTP/1.1
```

### Expected Response (200 OK)
```typescript
{
  plans: Array<{
    id: string;
    slug: string;
    name: string;
    price_cents: number;
    interval: string;
    tokens_per_period: number;
    features: Record<string, any> | null;
  }>;
}
```

---

## 6. Create Checkout Session

**Frontend Function:** `createCheckoutSession(userId: string, planSlug: string, successUrl: string, cancelUrl: string)`  
**Location:** [lib/api.ts:377-402](file:///Users/harmanpreetsingh/Public/Code/Anthropic_Hack/frontend/lib/api.ts#L377-L402)

### Request
```http
POST /api/stripe/create-checkout-session HTTP/1.1
X-User-ID: <logto-user-id>
Content-Type: multipart/form-data

FormData:
  plan_slug: <string>              // e.g., "pro"
  success_url: <string>            // e.g., "http://localhost:3000/dashboard?checkout=success"
  cancel_url: <string>             // e.g., "http://localhost:3000/pricing?checkout=canceled"
```

### Expected Response (200 OK)
```typescript
{
  session_id: string;
  url: string;                     // ← Frontend redirects user here
}
```

### Usage in Frontend
```typescript
// app/pricing/page.tsx
const checkout = await createCheckoutSession(userId, "pro", successUrl, cancelUrl);
window.location.href = checkout.url;  // Redirect to Stripe
```

---

## 7. Create Portal Session

**Frontend Function:** `createPortalSession(userId: string, returnUrl: string)`  
**Location:** [lib/api.ts:410-431](file:///Users/harmanpreetsingh/Public/Code/Anthropic_Hack/frontend/lib/api.ts#L410-L431)

### Request
```http
POST /api/stripe/create-portal-session HTTP/1.1
X-User-ID: <logto-user-id>
Content-Type: multipart/form-data

FormData:
  return_url: <string>             // e.g., "http://localhost:3000/dashboard"
```

### Expected Response (200 OK)
```typescript
{
  url: string;                     // ← Frontend redirects user here
}
```

---

## 8. Cancel Subscription

**Frontend Function:** `cancelSubscription(userId: string)`  
**Location:** [lib/api.ts:438-452](file:///Users/harmanpreetsingh/Public/Code/Anthropic_Hack/frontend/lib/api.ts#L438-L452)

### Request
```http
POST /api/subscription/cancel HTTP/1.1
X-User-ID: <logto-user-id>
```

### Expected Response (200 OK)
```typescript
{
  success: boolean;
  message: string;
  period_end: string;              // When subscription ends
}
```

---

## 9. Get Billing Details

**Frontend Function:** `getBillingDetails(userId: string)`  
**Location:** [lib/api.ts:459-472](file:///Users/harmanpreetsingh/Public/Code/Anthropic_Hack/frontend/lib/api.ts#L459-L472)

### Request
```http
GET /api/billing/details HTTP/1.1
X-User-ID: <logto-user-id>
```

### Expected Response (200 OK)
```typescript
{
  subscription: {
    status: string;
    plan: {
      name: string;
      interval: string;
      price_cents: number;
      tokens_per_period: number;
      features: Record<string, any> | null;
    };
    current_period_start: string | null;
    current_period_end: string | null;
  } | null;
  wallet: {
    balance_tokens: number;
    currency: string;
    last_updated: string | null;
  } | null;
  payment_history: Array<{
    id: string;
    amount_cents: number;
    currency: string;
    status: string;
    date: string;
    description: string;
  }>;
  transaction_history: Array<{
    id: string;
    amount: number;
    type: string;
    balance_after: number;
    description: string;
    date: string;
  }>;
  usage_history: Array<{
    id: string;
    feature: string;
    amount: number;
    cost_cents: number;
    date: string;
  }>;
}
```

---

## 10. Health Check

**Frontend Function:** `checkHealth()`  
**Location:** [lib/api.ts:140-148](file:///Users/harmanpreetsingh/Public/Code/Anthropic_Hack/frontend/lib/api.ts#L140-L148)

### Request
```http
GET /api/health HTTP/1.1
```

### Expected Response (200 OK)
```typescript
{
  status: string;
  vector_store_ready: boolean;
  collection_stats: {
    count: number;
    collection_name: string;
    persist_directory: string;
  } | null;
}
```

---

## 11. Get Resume Stats

**Frontend Function:** `getResumeStats()`  
**Location:** [lib/api.ts:154-162](file:///Users/harmanpreetsingh/Public/Code/Anthropic_Hack/frontend/lib/api.ts#L154-L162)

### Request
```http
GET /api/resume-stats HTTP/1.1
```

### Expected Response (200 OK)
```typescript
{
  success: boolean;
  count: number;
  collection_name: string;
  persist_directory: string;
}
```

---

## 12. Clear Resume

**Frontend Function:** `clearResume(userId?: string)`  
**Location:** [lib/api.ts:169-185](file:///Users/harmanpreetsingh/Public/Code/Anthropic_Hack/frontend/lib/api.ts#L169-L185)

### Request
```http
DELETE /api/resume HTTP/1.1
X-User-ID: <logto-user-id>       // Optional
```

### Expected Response (200 OK)
```typescript
{
  success: boolean;
  message: string;
  documents_removed: number;
}
```

---

## Error Handling

All endpoints may return error responses:

### Error Response (4xx/5xx)
```typescript
{
  detail: string;                  // Error message
}
```

### Frontend Error Handling Pattern
```typescript
try {
  const data = await apiFunction(...);
  // Handle success
} catch (error) {
  // Frontend expects error.message to contain the error detail
  console.error('API error:', error.message);
  setError(error instanceof Error ? error.message : 'Failed to process request');
}
```

---

## Critical Data Flow for Resume Sessions

### The Issue
Resume sessions are not appearing in dashboard because of this flow:

1. **Upload Resume** → Backend creates resume session with `user_id` from `X-User-ID` header
2. **Start Workflow** → Backend creates workflow session linked to resume session
3. **Get Dashboard** → Backend queries resume sessions by `user_id` from `X-User-ID` header

### What to Check on Backend

1. **Resume Upload Endpoint** (`POST /api/upload-resume`)
   - ✅ Does it extract `user_id` from `X-User-ID` header?
   - ✅ Does it store `user_id` in the resume session record?
   - ✅ Does it return the correct `session_id` in response?

2. **Workflow Start Endpoint** (`POST /api/workflow/start`)
   - ✅ Does it extract `user_id` from `X-User-ID` header?
   - ✅ Does it link the workflow session to the resume session?
   - ✅ Does it verify the resume session belongs to the user?

3. **Dashboard Endpoint** (`GET /api/dashboard`)
   - ✅ Does it extract `user_id` from `X-User-ID` header?
   - ✅ Does it query resume sessions WHERE `user_id = <extracted-user-id>`?
   - ✅ Does it include nested workflow sessions in the response?

### Expected Database State After Upload + Workflow

```sql
-- Resume Sessions Table
resume_sessions:
  id: "abc-123"
  user_id: "user_xyz"              -- ← From X-User-ID header
  filename: "resume.pdf"
  created_at: "2025-11-30T..."

-- Workflow Sessions Table
workflow_sessions:
  id: "def-456"
  resume_session_id: "abc-123"     -- ← Links to resume
  user_id: "user_xyz"              -- ← From X-User-ID header
  scholarship_url: "https://..."
  status: "complete"
```

### Dashboard Query Should Return

```typescript
{
  resume_sessions: [
    {
      id: "abc-123",
      filename: "resume.pdf",
      workflow_sessions: [
        {
          id: "def-456",
          scholarship_url: "https://...",
          status: "complete",
          // ... other fields
        }
      ]
    }
  ]
}
```

---

## Header Consistency

**ALL endpoints now use:** `X-User-ID` (uppercase)

Previously inconsistent endpoints (now fixed):
- ✅ `uploadResume()` - Changed from `x-user-id` to `X-User-ID`
- ✅ `createCheckoutSession()` - Changed from `x-user-id` to `X-User-ID`
- ✅ `createPortalSession()` - Changed from `x-user-id` to `X-User-ID`
- ✅ `cancelSubscription()` - Changed from `x-user-id` to `X-User-ID`
- ✅ `getBillingDetails()` - Changed from `x-user-id` to `X-User-ID`
