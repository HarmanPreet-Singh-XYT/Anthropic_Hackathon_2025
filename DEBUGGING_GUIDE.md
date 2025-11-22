# Debugging Guide - Application Page Stuck Loading

## Issue Summary
The application page gets stuck on "Generating your application..." when the workflow is in `"waiting_for_input"` status.

## Root Cause
The application page only handled two statuses:
- `"complete"` → Show data
- `"processing"` → Poll again

But didn't handle:
- `"waiting_for_input"` → Interview required
- `"processing_resume"` → Optimizer/Ghostwriter running

## Fix Applied
Added redirect logic in `frontend/app/application/page.tsx` (lines 49-54):

```typescript
} else if (data.status === "waiting_for_input") {
    // Interview required - redirect to AI-Help page
    router.push(`/ai-help?session=${session_id}`);
} else if (data.status === "processing" || data.status === "processing_resume") {
    // Still processing, poll again
    setTimeout(fetchData, 2000);
}
```

## How to Debug in the Future

### 1. Check Session Status
```bash
curl http://localhost:8000/api/workflow/status/<SESSION_ID> | python3 -m json.tool
```

### 2. Workflow Status Flow
```
"processing" → Initial workflow running (Scout, Profiler, Decoder, Matchmaker)
    ↓
"waiting_for_input" → Interview required (match_score < 0.8)
    ↓
User completes interview
    ↓
"processing_resume" → Optimizer + Ghostwriter running
    ↓
"complete" → Ready to display on application page
```

### 3. Common Issues

#### Issue: Stuck at "waiting_for_input"
**Solution:** Complete the interview at `/ai-help?session=<ID>`

#### Issue: Stuck at "processing"
**Possible causes:**
- Backend crashed
- Agent error
- ChromaDB not running

**Check backend logs:**
```bash
# Look for errors in the terminal running uvicorn
```

#### Issue: Stuck at "processing_resume"
**Possible causes:**
- Optimizer agent error
- Ghostwriter agent error
- LLM API timeout

**Check:**
```bash
# Check if LLM client is working
# Check API keys in .env
```

### 4. Force Complete Interview (Testing Only)

If you want to bypass the interview for testing:

```bash
curl -X POST http://localhost:8000/api/workflow/resume \
  -F "session_id=<SESSION_ID>" \
  -F "bridge_story=Test story for debugging"
```

### 5. Restart Workflow

If a session is stuck, start a new one:
1. Go to http://localhost:3000/start
2. Upload resume and scholarship URL again
3. You'll get a new session ID

## Verification Checklist

After the fix:
- [ ] Application page redirects to AI-Help if interview needed
- [ ] Application page polls while processing_resume
- [ ] Application page shows data when complete
- [ ] Matchmaker page loads correctly
- [ ] AI-Help page works correctly

## Testing the Full Flow

1. **Start:** Upload resume + URL
2. **Matchmaker:** See match score, click "Continue to AI Help"
3. **AI-Help:** Answer interview questions
4. **Processing:** Wait for optimizer/ghostwriter (will show loading)
5. **Application:** See essay + resume optimizations

Estimated time: 30-60 seconds for full workflow.
