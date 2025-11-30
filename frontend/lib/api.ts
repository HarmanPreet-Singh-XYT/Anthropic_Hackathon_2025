/**
 * API client for backend communication
 * Handles resume upload and backend interaction
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Response types matching backend Pydantic models
export interface UploadResponse {
    success: boolean;
    message: string;
    chunks_stored: number;
    metadata: {
        session_id: string;
        filename: string;
        file_size_bytes: number;
        file_size_mb: number;
        text_preview: string | null;
    };
}

export interface WorkflowStartResponse {
    session_id: string;
    status: string;
    message: string;
}

export interface WorkflowStatusResponse {
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

export interface HealthResponse {
    status: string;
    vector_store_ready: boolean;
    collection_stats: {
        count: number;
        collection_name: string;
        persist_directory: string;
    } | null;
}

export interface ResumeStatsResponse {
    success: boolean;
    count: number;
    collection_name: string;
    persist_directory: string;
}

export interface ErrorResponse {
    detail: string;
}

/**
 * Upload a resume PDF to the backend
 * @param file - PDF file to upload
 * @param userId - Logto User ID
 * @returns Upload response with chunk count and metadata
 * @throws Error if upload fails
 */
export async function uploadResume(file: File, userId: string): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/upload-resume`, {
        method: 'POST',
        headers: {
            'X-User-ID': userId,
        },
        body: formData,
    });

    if (!response.ok) {
        const error: ErrorResponse = await response.json();
        throw new Error(error.detail || `Upload failed with status ${response.status}`);
    }

    return response.json();
}

/**
 * Start the full workflow
 * @param scholarshipUrl - URL of the scholarship
 * @param resumeSessionId - Session ID from resume upload
 * @param userId - Logto User ID
 * @returns Workflow session ID
 */
export async function startWorkflow(scholarshipUrl: string, resumeSessionId: string, userId: string): Promise<WorkflowStartResponse> {
    const formData = new FormData();
    formData.append('scholarship_url', scholarshipUrl);
    formData.append('resume_session_id', resumeSessionId);

    const response = await fetch(`${API_BASE_URL}/api/workflow/start`, {
        method: 'POST',
        headers: {
            'X-User-ID': userId,
        },
        body: formData,
    });

    if (!response.ok) {
        const error: ErrorResponse = await response.json();
        throw new Error(error.detail || `Workflow start failed with status ${response.status}`);
    }

    return response.json();
}

/**
 * Check workflow status
 * @param sessionId - Workflow session ID
 * @param userId - Logto User ID
 * @returns Current status and results
 */
export async function getWorkflowStatus(sessionId: string, userId: string): Promise<WorkflowStatusResponse> {
    const response = await fetch(`${API_BASE_URL}/api/workflow/status/${sessionId}`, {
        headers: {
            'X-User-ID': userId,
        },
    });

    if (!response.ok) {
        throw new Error(`Status check failed with status ${response.status}`);
    }

    return response.json();
}

/**
 * Check backend health and vector store status
 * @returns Health check response
 */
export async function checkHealth(): Promise<HealthResponse> {
    const response = await fetch(`${API_BASE_URL}/api/health`);

    if (!response.ok) {
        throw new Error(`Health check failed with status ${response.status}`);
    }

    return response.json();
}

/**
 * Get ChromaDB collection statistics
 * @returns Resume stats including document count
 */
export async function getResumeStats(): Promise<ResumeStatsResponse> {
    const response = await fetch(`${API_BASE_URL}/api/resume-stats`);

    if (!response.ok) {
        throw new Error(`Stats request failed with status ${response.status}`);
    }

    return response.json();
}

/**
 * Clear all resume data from ChromaDB
 * @param userId - Logto User ID (optional, if backend requires it for specific user clear)
 * @returns Success message and count of documents removed
 */
export async function clearResume(userId?: string): Promise<{ success: boolean; message: string; documents_removed: number }> {
    const headers: HeadersInit = {};
    if (userId) {
        headers['X-User-ID'] = userId;
    }

    const response = await fetch(`${API_BASE_URL}/api/resume`, {
        method: 'DELETE',
        headers,
    });

    if (!response.ok) {
        throw new Error(`Clear request failed with status ${response.status}`);
    }

    return response.json();
}

// --- Dashboard API Interfaces ---

export interface UserInfo {
    id: string;
    email: string | null;
}

export interface WalletInfo {
    balance_tokens: number;
    currency: string;
    last_updated: string | null; // ISO Date
}

export interface PlanInfo {
    name: string;
    interval: string;
    price_cents: number;
    tokens_per_period: number;
    features: Record<string, any> | null;
}

export interface SubscriptionInfo {
    status: string;
    plan: PlanInfo;
    current_period_start: string | null;
    current_period_end: string | null;
}

export interface DashboardApplication {
    id: string;
    scholarship_url: string;
    status: string;
    match_score: number | null;
    had_interview: boolean;
    created_at: string;
}

export interface DashboardInterview {
    id: string;
    current_target: string | null;
    created_at: string;
    completed_at: string | null;
}

export interface DashboardWorkflow {
    id: string;
    scholarship_url: string;
    status: string;
    match_score: number | null;
    created_at: string;
    updated_at: string | null;
    completed_at: string | null;
    applications: DashboardApplication[];
    interview_session: DashboardInterview | null;
}

export interface DashboardResume {
    id: string;
    filename: string;
    file_size_bytes: number;
    created_at: string;
    text_preview: string | null;
    workflow_sessions: DashboardWorkflow[];
}

export interface UsageStats {
    queries_today: number;
    queries_month: number;
    tokens_used_today: number;
    tokens_used_month: number;
}

export interface ActivityItem {
    type: string;
    ref_id: string;
    description: string;
    timestamp: string;
    amount?: number;
}

export interface DashboardResponse {
    user: UserInfo;
    wallet: WalletInfo | null;
    subscription: SubscriptionInfo | null;
    resume_sessions: DashboardResume[];
    usage: UsageStats;
    recent_activity: ActivityItem[];
}

/**
 * Fetch dashboard data
 * @param userId - Logto User ID (sent via x-user-id header)
 * @returns Dashboard data including user info, wallet, subscription, resume sessions, usage stats, and recent activity
 */
export async function getDashboardData(userId: string): Promise<DashboardResponse> {
    const response = await fetch(`${API_BASE_URL}/api/dashboard`, {
        headers: {
            'X-User-ID': userId,
        },
    });

    if (!response.ok) {
        throw new Error(`Dashboard data fetch failed with status ${response.status}`);
    }

    return response.json();
}

// --- Stripe Payment API Interfaces ---

export interface BillingPlan {
    id: string;
    slug: string;
    name: string;
    price_cents: number;
    interval: string;
    tokens_per_period: number;
    features: Record<string, any> | null;
}

export interface BillingPlansResponse {
    plans: BillingPlan[];
}

export interface CheckoutSessionResponse {
    session_id: string;
    url: string;
}

export interface PortalSessionResponse {
    url: string;
}

export interface CancelSubscriptionResponse {
    success: boolean;
    message: string;
    period_end: string;
}

export interface BillingDetailsResponse {
    subscription: SubscriptionInfo | null;
    wallet: WalletInfo | null;
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

/**
 * Get available billing plans
 * @returns List of available subscription plans
 */
export async function getBillingPlans(): Promise<BillingPlansResponse> {
    const response = await fetch(`${API_BASE_URL}/api/billing/plans`);

    if (!response.ok) {
        throw new Error(`Failed to fetch billing plans with status ${response.status}`);
    }

    return response.json();
}

/**
 * Create a Stripe checkout session
 * @param userId - Logto User ID
 * @param planSlug - Plan identifier (e.g., "pro")
 * @param successUrl - URL to redirect after successful payment
 * @param cancelUrl - URL to redirect if user cancels
 * @returns Checkout session with redirect URL
 */
export async function createCheckoutSession(
    userId: string,
    planSlug: string,
    successUrl: string,
    cancelUrl: string
): Promise<CheckoutSessionResponse> {
    const formData = new FormData();
    formData.append('plan_slug', planSlug);
    formData.append('success_url', successUrl);
    formData.append('cancel_url', cancelUrl);

    const response = await fetch(`${API_BASE_URL}/api/stripe/create-checkout-session`, {
        method: 'POST',
        headers: {
            'x-user-id': userId,
        },
        body: formData,
    });

    if (!response.ok) {
        const error: ErrorResponse = await response.json();
        throw new Error(error.detail || `Checkout session creation failed with status ${response.status}`);
    }

    return response.json();
}

/**
 * Create a Stripe customer portal session
 * @param userId - Logto User ID
 * @param returnUrl - URL to redirect back to after portal
 * @returns Portal session with redirect URL
 */
export async function createPortalSession(
    userId: string,
    returnUrl: string
): Promise<PortalSessionResponse> {
    const formData = new FormData();
    formData.append('return_url', returnUrl);

    const response = await fetch(`${API_BASE_URL}/api/stripe/create-portal-session`, {
        method: 'POST',
        headers: {
            'x-user-id': userId,
        },
        body: formData,
    });

    if (!response.ok) {
        const error: ErrorResponse = await response.json();
        throw new Error(error.detail || `Portal session creation failed with status ${response.status}`);
    }

    return response.json();
}

/**
 * Cancel user's subscription (at period end)
 * @param userId - Logto User ID
 * @returns Cancellation confirmation with period end date
 */
export async function cancelSubscription(userId: string): Promise<CancelSubscriptionResponse> {
    const response = await fetch(`${API_BASE_URL}/api/subscription/cancel`, {
        method: 'POST',
        headers: {
            'x-user-id': userId,
        },
    });

    if (!response.ok) {
        const error: ErrorResponse = await response.json();
        throw new Error(error.detail || `Subscription cancellation failed with status ${response.status}`);
    }

    return response.json();
}

/**
 * Get billing details for a user
 * @param userId - Logto User ID
 * @returns Billing details including subscription, wallet, and history
 */
export async function getBillingDetails(userId: string): Promise<BillingDetailsResponse> {
    const response = await fetch(`${API_BASE_URL}/api/billing/details`, {
        headers: {
            'x-user-id': userId,
        },
    });

    if (!response.ok) {
        const error: ErrorResponse = await response.json();
        throw new Error(error.detail || `Billing details fetch failed with status ${response.status}`);
    }

    return response.json();
}

