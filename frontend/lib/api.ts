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

export interface Application {
    id: string;
    workflow_session_id: string;
    scholarship_url: string;
    status: "complete" | "error" | string; // Allow other statuses
    match_score: number | null;
    had_interview: boolean;
    created_at: string;
}

export interface Resume {
    id: string;
    filename: string;
    created_at: string;
    file_size_bytes: number;
}

export interface ActiveWorkflow {
    id: string;
    status: "processing" | "waiting_for_input" | "processing_resume" | string;
    scholarship_url: string;
    created_at: string;
    updated_at: string | null;
}

export interface DashboardResponse {
    user_id: string | null;
    stats: {
        total_applications: number;
        total_interviews: number;
        average_match_score: number;
        active_workflows_count: number;
    };
    applications: Application[];
    resumes: Resume[];
    active_workflows: ActiveWorkflow[];
}

/**
 * Fetch dashboard data
 * @param userId - Logto User ID
 * @returns Dashboard data including stats, applications, etc.
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
