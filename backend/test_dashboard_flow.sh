#!/bin/bash
# Test script to verify dashboard returns resume sessions correctly
# Tests various user_id scenarios including string "null"

set -e

BASE_URL="http://localhost:8000"
TEST_PDF="test_resume.pdf"

echo "============================================================"
echo "DASHBOARD USER ID FLOW TEST SUITE"
echo "============================================================"
echo ""

# Check if server is running
echo "Checking if server is running..."
if ! curl -s "${BASE_URL}/api/health" > /dev/null; then
    echo "❌ Server is not running. Please start the backend server."
    exit 1
fi
echo "✓ Server is running"
echo ""

# Test 1: Valid User ID
echo "============================================================"
echo "TEST 1: Valid User ID"
echo "============================================================"
USER_ID="test_user_123"

echo ""
echo "📤 Uploading resume with user_id: '${USER_ID}'"
UPLOAD_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/upload-resume" \
    -H "X-User-ID: ${USER_ID}" \
    -F "file=@${TEST_PDF}")

echo "Upload response:"
echo "$UPLOAD_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$UPLOAD_RESPONSE"

echo ""
echo "📊 Fetching dashboard with user_id: '${USER_ID}'"
DASHBOARD_RESPONSE=$(curl -s -X GET "${BASE_URL}/api/dashboard" \
    -H "X-User-ID: ${USER_ID}")

RESUME_COUNT=$(echo "$DASHBOARD_RESPONSE" | python3 -c "import sys, json; print(len(json.load(sys.stdin)['resume_sessions']))" 2>/dev/null || echo "0")

echo "Resume sessions found: ${RESUME_COUNT}"
if [ "$RESUME_COUNT" -gt 0 ]; then
    echo "✓ SUCCESS: Found resume sessions!"
else
    echo "✗ FAIL: No resume sessions found (expected at least 1)"
fi

# Test 2: String "null"
echo ""
echo "============================================================"
echo "TEST 2: String 'null' (Bug Scenario)"
echo "============================================================"

echo ""
echo "📤 Uploading resume with user_id: 'null' (string)"
curl -s -X POST "${BASE_URL}/api/upload-resume" \
    -H "X-User-ID: null" \
    -F "file=@${TEST_PDF}" > /dev/null

echo "✓ Upload completed"

echo ""
echo "📊 Fetching dashboard with user_id: 'null' (string)"
DASHBOARD_RESPONSE=$(curl -s -X GET "${BASE_URL}/api/dashboard" \
    -H "X-User-ID: null")

RESUME_COUNT=$(echo "$DASHBOARD_RESPONSE" | python3 -c "import sys, json; print(len(json.load(sys.stdin)['resume_sessions']))" 2>/dev/null || echo "0")

echo "Resume sessions found: ${RESUME_COUNT}"
echo "ℹ️  With sanitization, 'null' should be treated as None/anonymous"

# Test 3: String "undefined"
echo ""
echo "============================================================"
echo "TEST 3: String 'undefined' (Bug Scenario)"
echo "============================================================"

echo ""
echo "📤 Uploading resume with user_id: 'undefined' (string)"
curl -s -X POST "${BASE_URL}/api/upload-resume" \
    -H "X-User-ID: undefined" \
    -F "file=@${TEST_PDF}" > /dev/null

echo "✓ Upload completed"

echo ""
echo "📊 Fetching dashboard with user_id: 'undefined' (string)"
DASHBOARD_RESPONSE=$(curl -s -X GET "${BASE_URL}/api/dashboard" \
    -H "X-User-ID: undefined")

RESUME_COUNT=$(echo "$DASHBOARD_RESPONSE" | python3 -c "import sys, json; print(len(json.load(sys.stdin)['resume_sessions']))" 2>/dev/null || echo "0")

echo "Resume sessions found: ${RESUME_COUNT}"
echo "ℹ️  With sanitization, 'undefined' should be treated as None/anonymous"

# Test 4: No header
echo ""
echo "============================================================"
echo "TEST 4: No X-User-ID Header"
echo "============================================================"

echo ""
echo "📤 Uploading resume without X-User-ID header"
curl -s -X POST "${BASE_URL}/api/upload-resume" \
    -F "file=@${TEST_PDF}" > /dev/null

echo "✓ Upload completed"

echo ""
echo "📊 Fetching dashboard without X-User-ID header"
DASHBOARD_RESPONSE=$(curl -s -X GET "${BASE_URL}/api/dashboard")

RESUME_COUNT=$(echo "$DASHBOARD_RESPONSE" | python3 -c "import sys, json; print(len(json.load(sys.stdin)['resume_sessions']))" 2>/dev/null || echo "0")

echo "Resume sessions found: ${RESUME_COUNT}"
echo "ℹ️  Should use default 'test_user_demo'"

echo ""
echo "============================================================"
echo "✅ All tests completed!"
echo "============================================================"
echo ""
echo "Check the backend server logs to see the detailed sanitization output."
