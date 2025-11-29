ScholarFit AI - Frontend API Documentation
Authentication & Session Management
The backend uses a stateless session model associated with a User ID. All API requests that involve user data must include the X-User-ID header.

Headers
Header	Required	Description
X-User-ID	Yes*	The unique user ID from Logto. Required for all endpoints below to associate data with the user.
> Note: While the backend might technically allow requests without it (for backward compatibility or public endpoints), the frontend MUST send it for all authenticated user actions to ensure data persistence and retrieval.

API Endpoints
1. Upload Resume
Uploads a PDF resume, processes it, and creates a resume session.

Endpoint: POST /api/upload-resume
Headers: X-User-ID: <user_id>
Content-Type: multipart/form-data
Body:
file: The PDF file (binary).
Response (200 OK):

{
  "success": true,
  "message": "Resume processed successfully",
  "chunks_stored": 15,
  "metadata": {
    "session_id": "uuid-string",  // <--- Store this RESUME_SESSION_ID
    "filename": "resume.pdf",
    "file_size_bytes": 102400,
    "file_size_mb": 0.1,
    "text_preview": "..."
  }
}
2. Start Scout Workflow (Quick Scan)
Starts the initial "Scout" agent to analyze a scholarship URL.

Endpoint: POST /api/scout/start
Headers: X-User-ID: <user_id>
Content-Type: application/x-www-form-urlencoded
Body:
scholarship_url: String (URL)
Response (200 OK):

{
  "session_id": "uuid-string", // <--- Workflow Session ID
  "status": "processing",
  "message": "Scout workflow started"
}
3. Start Full Workflow
Starts the main analysis workflow (Matchmaker -> Essay Draft etc.).

Endpoint: POST /api/workflow/start
Headers: X-User-ID: <user_id>
Content-Type: multipart/form-data
Body:
scholarship_url: String (URL)
resume_session_id: String (The ID returned from /api/upload-resume)
resume_path: (Optional) "session_based" (default if using session ID)
Response (200 OK):

{
  "session_id": "uuid-string", // <--- Workflow Session ID
  "status": "processing",
  "message": "Workflow started"
}
4. Check Workflow Status
Poll this endpoint to get the results of the workflow.

Endpoint: GET /api/workflow/status/{session_id}
Headers: X-User-ID: <user_id>
Response (200 OK):

{
  "session_id": "uuid-string",
  "status": "processing" | "waiting_for_input" | "complete" | "error",
  "result": {
    "matchmaker_results": { ... },
    "essay_draft": "...",
    "gaps": [ ... ], // If status is "waiting_for_input", check these gaps
    "match_score": 0.85
  },
  "error": null
}
5. Resume Workflow (After Interview)
If the workflow status is waiting_for_input (meaning an interview was needed), call this after collecting the user's "bridge story".

Endpoint: POST /api/workflow/resume
Headers: X-User-ID: <user_id>
Content-Type: application/x-www-form-urlencoded
Body:
session_id: String (The Workflow Session ID)
bridge_story: String (The user's answer/story)
Response (200 OK):

{
  "session_id": "uuid-string",
  "status": "processing_resume",
  "message": "Workflow resumed"
}
6. Get Application History
Retrieve past applications for a specific resume (and user).

Endpoint: GET /api/applications/history/{resume_session_id}
Headers: X-User-ID: <user_id>
Response (200 OK):

{
  "success": true,
  "resume_session_id": "...",
  "applications": [
    {
      "workflow_session_id": "...",
      "scholarship_url": "...",
      "status": "complete",
      "match_score": 0.9,
      "had_interview": false,
      "created_at": "ISO-8601-Date"
    }
  ],
  "count": 1
}
Frontend Integration Flow
Login: User logs in via Logto on frontend. Frontend receives 
user_id
.
Upload: User uploads resume.
Frontend calls POST /api/upload-resume with X-User-ID.
Frontend stores resume_session_id.
Apply: User enters scholarship URL.
Frontend calls POST /api/workflow/start with scholarship_url, resume_session_id, and X-User-ID.
Frontend receives workflow_session_id.
Poll: Frontend polls GET /api/workflow/status/{workflow_session_id}.
If 
status
 becomes waiting_for_input: Show Interview UI.
If 
status
 becomes 
complete
: Show Results (Essay, Strategy, etc.).
Interview (Optional): If interview needed:
User chats/answers questions.
Frontend calls POST /api/workflow/resume with bridge_story and X-User-ID.
Go back to Poll step.