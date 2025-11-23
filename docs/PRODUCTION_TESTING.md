# Production Testing Guide

Complete guide to test the session-based workflow and verify it's working correctly.

---

## 1. Starting the Servers

### Backend
```bash
cd /Users/elliot18/Desktop/Home/Projects/Anthropic_Hack/backend
python3 -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output**:
```
✓ Vector store initialized: /path/to/chroma_db
✓ Collection stats: 0 documents
✓ LLM Client initialized
✓ Agents initialized
✓ Workflow orchestrator ready
INFO: Uvicorn running on http://0.0.0.0:8000
```

### Frontend
```bash
cd /Users/elliot18/Desktop/Home/Projects/Anthropic_Hack/frontend
npm run dev
```

**Expected Output**:
```
▲ Next.js 16.0.3 (Turbopack)
- Local: http://localhost:3000
✓ Ready in [time]
```

---

## 2. Manual Testing Checklist

### Test 1: Single User Upload and Workflow

**Steps**:
1. Open browser: `http://localhost:3000`
2. Click "Start" or navigate to `/start`
3. Upload a PDF resume (test file should be < 5MB)
4. Enter scholarship URL (e.g., `https://www.scholarships.com/test`)
5. Click "Analyze" button

**What to Watch in Backend Logs**:
```
🆔 [API] Generated session_id: [uuid] for resume upload
📝 [ProfilerAgent] Storing resume for session: [uuid]
✓ [ProfilerAgent] Stored X chunks for session: [uuid]
✓ [API] Resume processed successfully for session: [uuid]

🆔 [API] Starting workflow with resume session: [uuid]
🚀 Starting Scholarship Workflow
   Session: [uuid]
   URL: [your-url]

🔵 NODE: Scout Agent
🔵 NODE: Decoder Agent
🔵 NODE: Matchmaker Agent
🔄 [Workflow] Matching for session: [uuid]
🔍 [MatchmakerAgent] Querying vector DB for session: [uuid]
  → [Keyword] (weight: X%): match score = Y [session: uuid]
```

**✓ Success Criteria**:
- Session ID appears in logs
- Resume chunks stored (count should match your PDF)
- Matchmaker queries filtered by session ID
- Frontend navigates to `/matchmaker` page

---

### Test 2: Session Isolation (Multi-User Simulation)

**Steps**:
1. Open TWO browser windows (or incognito + normal)
2. **Window 1**: Upload `resume_A.pdf` (e.g., community leader)
3. **Window 2**: Upload `resume_B.pdf` (e.g., tech professional)
4. Start workflows for both with same scholarship URL

**What to Watch in Backend Logs**:
```
# Window 1
🆔 [API] Generated session_id: abc-123-xxx
📝 [ProfilerAgent] Storing resume for session: abc-123-xxx
🔍 [MatchmakerAgent] Querying vector DB for session: abc-123-xxx
  → Leadership: match score = 0.85 [session: abc-123-xxx]

# Window 2  
🆔 [API] Generated session_id: def-456-yyy
📝 [ProfilerAgent] Storing resume for session: def-456-yyy
🔍 [MatchmakerAgent] Querying vector DB for session: def-456-yyy
  → Technical Skills: match score = 0.90 [session: def-456-yyy]
```

**✓ Success Criteria**:
- Two distinct session IDs generated
- Each workflow queries ONLY its own session
- Match results are different (appropriate to each resume)
- No cross-contamination in results

---

### Test 3: Session Cleanup

**Test the cleanup endpoint**:
```bash
# Get a session_id from previous test (check frontend localStorage or backend logs)
SESSION_ID="abc-123-xxx"

# Delete that session's data
curl -X DELETE http://localhost:8000/api/resume/session/$SESSION_ID

# Expected response:
{
  "success": true,
  "documents_deleted": 15,
  "session_id": "abc-123-xxx"
}
```

**Verify cleanup worked**:
```bash
# Check collection stats
curl http://localhost:8000/api/resume-stats

# Expected: count should be reduced
{
  "success": true,
  "count": 0,  # or reduced number
  "collection_name": "resumes"
}
```

**✓ Success Criteria**:
- DELETE returns correct count of deleted documents
- Stats reflect the reduction
- Other sessions unaffected

---

## 3. Browser DevTools Inspection

### Frontend Verification

**Open Browser DevTools** (F12) → Console tab

**During upload, you should see**:
```
[StartPage] Step 1: Uploading resume...
[StartPage] Resume uploaded, session_id: abc-123-xxx
[StartPage] Stored 15 chunks
[StartPage] Step 2: Starting workflow...
[StartPage] Workflow started
  Resume session: abc-123-xxx
  Workflow session: def-456-yyy
[StartPage] Poll #1: processing
[StartPage] Poll #5: waiting_for_input
[StartPage] Navigating to matchmaker...
```

**Check localStorage**:
1. DevTools → Application tab → Local Storage → `http://localhost:3000`
2. Look for key: `resume_session_id`
3. Value should match the session ID from logs

---

## 4. Automated E2E Test

Run the comprehensive test suite:

```bash
cd /Users/elliot18/Desktop/Home/Projects/Anthropic_Hack/backend
python3 test_e2e_session_workflow.py
```

**Expected Output**:
```
================================================================================
E2E TEST SUITE - SESSION-BASED WORKFLOW
================================================================================

TEST 1: HAPPY PATH (High Match Score, No Interview)
  ✅ PASSED

TEST 2: INTERVIEW PATH (Low Match Score, Gaps Detected)
  ✅ PASSED

TEST 3: MULTI-USER SESSION ISOLATION
  ✅ PASSED

================================================================================
TEST SUMMARY
================================================================================
  Happy Path: ✅ PASSED
  Interview Path: ✅ PASSED
  Multi-User Isolation: ✅ PASSED
================================================================================

🎉 ALL TESTS PASSED - System is production ready!
```

---

## 5. Critical Check Points

### ✓ Session Isolation Verification

**How to confirm it's working**:

1. **Look for session_id in every log line during Matchmaker phase**:
   ```
   🔍 [MatchmakerAgent] Querying vector DB for session: [uuid]
   → Keyword: ... [session: uuid]  ← Session ID should appear here
   ```

2. **Verify query filtering**:
   - Backend logs should show `query_with_filter` being called
   - Filter dict should include `{"session_id": "..."}`

3. **Check ChromaDB metadata**:
   ```bash
   # In Python console:
   from utils.vector_store import VectorStore
   vs = VectorStore("resumes", "./data/chroma_db")
   docs = vs.collection.get(limit=5)
   print(docs["metadatas"])
   
   # Expected output:
   [
     {'source': 'resume', 'chunk_index': 0, 'session_id': 'abc-123'},
     {'source': 'resume', 'chunk_index': 1, 'session_id': 'abc-123'},
     ...
   ]
   ```

---

## 6. Common Issues and Fixes

### Issue: "Resume file is required" error

**Cause**: File not selected or upload failed  
**Fix**: Ensure PDF is selected, check file size < 5MB

### Issue: Workflow timeout

**Cause**: Scout/Decoder/Matchmaker taking too long  
**Fix**: Check API keys, network connection, increase timeout in frontend

### Issue: Wrong match results

**Cause**: Session ID not passed correctly  
**Fix**: Check backend logs for session ID consistency

### Issue: "Session not found" error

**Cause**: Workflow session ID doesn't exist  
**Fix**: Ensure workflow was successfully started, check `workflow_sessions` dict

---

## 7. Production Monitoring Checklist

Once deployed, monitor these metrics:

### Daily Checks
- [ ] Session creation rate (should be stable)
- [ ] ChromaDB document count (should grow steadily)
- [ ] Error rate in logs (should be <1%)
- [ ] Average workflow completion time (should be <60s)

### Weekly Checks
- [ ] Database size (implement cleanup if growing too fast)
- [ ] Memory usage (ChromaDB in-memory cache)
- [ ] API response times
- [ ] User feedback on match accuracy

### Session Cleanup Strategy
```bash
# Example: Delete sessions older than 7 days
# Create a cron job or scheduled script

# Get all sessions
# Filter by creation timestamp (if you add that metadata)
# Delete old sessions using the DELETE endpoint
```

---

## 8. Quick Smoke Test

**30-Second Verification**:

```bash
# 1. Backend health check
curl http://localhost:8000/api/resume-stats

# 2. Upload test resume
curl -X POST http://localhost:8000/api/upload-resume \
  -F "file=@/path/to/test_resume.pdf"
# Note the session_id from response

# 3. Check it was stored
curl http://localhost:8000/api/resume-stats
# Count should increase

# 4. Start workflow (use session_id from step 2)
curl -X POST http://localhost:8000/api/workflow/start \
  -F "scholarship_url=https://test.com/scholarship" \
  -F "resume_session_id=YOUR_SESSION_ID"

# 5. Monitor logs for session isolation
# Look for "Querying vector DB for session: YOUR_SESSION_ID"
```

---

## 9. Success Indicators

**✅ System is working correctly if**:

1. ✓ Each upload generates unique `session_id`
2. ✓ Session ID appears in all Matchmaker logs
3. ✓ Multiple simultaneous users get different session IDs
4. ✓ Match results are appropriate to each resume
5. ✓ Cleanup endpoint deletes correct sessions only
6. ✓ E2E tests pass with 100% success rate
7. ✓ No errors in backend logs during normal operation
8. ✓ Frontend navigates smoothly through workflow

**❌ Red flags**:
- Session ID missing from Matchmaker logs
- Same match results for different resumes
- "Session not found" errors
- Cleanup deleting wrong sessions
- E2E test failures

---

## 10. Final Production Deployment

Before deploying to production:

1. **Environment Variables**:
   ```bash
   # Backend .env
   OPENAI_API_KEY=your_production_key
   GOOGLE_CSE_ID=your_cse_id
   GOOGLE_API_KEY=your_google_key
   
   # Frontend .env.production
   NEXT_PUBLIC_API_URL=https://your-api-domain.com
   ```

2. **Build Frontend**:
   ```bash
   cd frontend
   npm run build
   npm start  # Production server
   ```

3. **Run Backend in Production Mode**:
   ```bash
   cd backend
   python3 -m uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
   ```

4. **Run E2E Tests One Last Time**:
   ```bash
   python3 test_e2e_session_workflow.py
   ```

5. **Monitor Logs for First Hour**:
   - Watch for session IDs
   - Verify no cross-contamination
   - Check error rates

---

**You're production-ready when all 3 E2E tests pass! 🎉**
