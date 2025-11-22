# Backend API Testing Guide

## Quick Start - Verify Agents & Workflow

### 1. Run End-to-End Workflow Test
This tests the full chain: Scout -> Profiler -> Matchmaker -> Interviewer -> Optimizer.

```bash
# From the project root
python3 backend/test_e2e.py
```

**Success Criteria:**
- Match Score should be > 40% (e.g., ~59%).
- Workflow should proceed to `optimizer` phase.
- No critical errors in logs.

### 2. Verify Scout Agent (Search)
This tests if the Scout can find real data from the web.

```bash
# From the project root
python3 backend/verify_scout.py
```

**Success Criteria:**
- Should find > 0 "validated winner items".
- Should find > 0 "insights".

---

## API Testing - Test the Server

### 1. Start the Backend Server

Open a **new terminal** and run:

```bash
cd /Users/elliot18/Desktop/Home/Projects/Anthropic_Hack/backend
python3 -m uvicorn api:app --reload --port 8000
```

You should see:
```
✓ Vector store initialized: /Users/elliot18/Desktop/Home/Projects/Anthropic_Hack/backend/data/chroma_db
✓ Collection stats: 0 documents
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

### 2. Test Health Endpoint

In another terminal:

```bash
curl http://localhost:8000/api/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "vector_store_ready": true,
  "collection_stats": {
    "count": 0,
    "collection_name": "resumes",
    "persist_directory": "..."
  }
}
```

---

### 3. Test Resume Upload

**You need a test PDF file.**  Where is your test resume PDF located?

Once you have it, upload with:

```bash
curl -X POST http://localhost:8000/api/upload-resume \
  -F "file=@/path/to/your/test-resume.pdf"
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Resume processed successfully",
  "chunks_stored": 15,
  "metadata": {
    "filename": "test-resume.pdf",
    "file_size_bytes": 45678,
    "file_size_mb": 0.04,
    "text_preview": "..."
  }
}
```

---

### 4. Verify Data Was Stored

```bash
curl http://localhost:8000/api/resume-stats
```

**Expected Response:**
```json
{
  "success": true,
  "count": 15,
  "collection_name": "resumes",
  "persist_directory": "..."
}
```

The `count` should match `chunks_stored` from upload response.

---

### 5. Test Error Handling

**Invalid file type:**
```bash
echo "not a pdf" > test.txt
curl -X POST http://localhost:8000/api/upload-resume \
  -F "file=@test.txt"
```

Expected: 400 error about file type

**Empty file:**
```bash
touch empty.pdf
curl -X POST http://localhost:8000/api/upload-resume \
  -F "file=@empty.pdf"
```

Expected: 400 error about empty file

---

### 6. Clear Resume Data (Optional)

```bash
curl -X DELETE http://localhost:8000/api/resume
```

---

## Troubleshooting

### Server won't start?
- Check if port 8000 is already in use: `lsof -i :8000`
- Check ANTHROPIC_API_KEY is set in `.env` file

### ChromaDB errors?
- Directory permissions: `ls -la backend/data/`
- ChromaDB should auto-create directory

### PDF processing errors?
- Make sure file is a valid PDF
- Check file isn't encrypted or image-only
- Max file size: 5MB
