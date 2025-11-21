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
        filename: string;
        file_size_bytes: number;
        file_size_mb: number;
        text_preview: string | null;
    };
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
 * @returns Upload response with chunk count and metadata
 * @throws Error if upload fails
 */
export async function uploadResume(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/upload-resume`, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        const error: ErrorResponse = await response.json();
        throw new Error(error.detail || `Upload failed with status ${response.status}`);
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
 * @returns Success message and count of documents removed
 */
export async function clearResume(): Promise<{ success: boolean; message: string; documents_removed: number }> {
    const response = await fetch(`${API_BASE_URL}/api/resume`, {
        method: 'DELETE',
    });

    if (!response.ok) {
        throw new Error(`Clear request failed with status ${response.status}`);
    }

    return response.json();
}
