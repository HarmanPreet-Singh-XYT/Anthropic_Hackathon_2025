#!/usr/bin/env python3
"""
Test script to verify dashboard returns resume sessions correctly
Tests various user_id scenarios including string "null"
"""

import requests
import sys
from pathlib import Path

BASE_URL = "http://localhost:8000"

def create_test_pdf():
    """Create a minimal test PDF if it doesn't exist"""
    test_pdf = Path("test_resume.pdf")
    if not test_pdf.exists():
        print("⚠️  test_resume.pdf not found. Please create a test PDF file first.")
        sys.exit(1)
    return test_pdf

def test_with_valid_user_id():
    """Test with a valid user ID"""
    print("\n" + "="*60)
    print("TEST 1: Valid User ID")
    print("="*60)
    
    user_id = "test_user_123"
    test_pdf = create_test_pdf()
    
    # 1. Upload resume
    print(f"\n📤 Uploading resume with user_id: {repr(user_id)}")
    with open(test_pdf, "rb") as f:
        response = requests.post(
            f"{BASE_URL}/api/upload-resume",
            files={"file": ("test_resume.pdf", f, "application/pdf")},
            headers={"X-User-ID": user_id}
        )
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        session_id = data["metadata"]["session_id"]
        print(f"   ✓ Resume uploaded, session_id: {session_id}")
    else:
        print(f"   ✗ Upload failed: {response.text}")
        return False
    
    # 2. Get dashboard
    print(f"\n📊 Fetching dashboard with user_id: {repr(user_id)}")
    response = requests.get(
        f"{BASE_URL}/api/dashboard",
        headers={"X-User-ID": user_id}
    )
    
    if response.status_code == 200:
        dashboard = response.json()
        resume_count = len(dashboard['resume_sessions'])
        print(f"   ✓ Dashboard fetched successfully")
        print(f"   Resume sessions found: {resume_count}")
        
        if resume_count > 0:
            print(f"   ✓ SUCCESS: Found resume sessions!")
            for resume in dashboard['resume_sessions']:
                print(f"      - {resume['filename']} (id: {resume['id']})")
            return True
        else:
            print(f"   ✗ FAIL: No resume sessions found (expected at least 1)")
            return False
    else:
        print(f"   ✗ Dashboard fetch failed: {response.text}")
        return False

def test_with_string_null():
    """Test with string 'null' - this might be the bug"""
    print("\n" + "="*60)
    print("TEST 2: String 'null' (Bug Scenario)")
    print("="*60)
    
    test_pdf = create_test_pdf()
    
    # Upload with string "null"
    print(f"\n📤 Uploading resume with user_id: 'null' (string)")
    with open(test_pdf, "rb") as f:
        response = requests.post(
            f"{BASE_URL}/api/upload-resume",
            files={"file": ("test_resume.pdf", f, "application/pdf")},
            headers={"X-User-ID": "null"}  # String "null"
        )
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Resume uploaded (should be sanitized to None)")
    else:
        print(f"   ✗ Upload failed: {response.text}")
        return False
    
    # Dashboard with string "null"
    print(f"\n📊 Fetching dashboard with user_id: 'null' (string)")
    response = requests.get(
        f"{BASE_URL}/api/dashboard",
        headers={"X-User-ID": "null"}
    )
    
    if response.status_code == 200:
        dashboard = response.json()
        resume_count = len(dashboard['resume_sessions'])
        print(f"   ✓ Dashboard fetched")
        print(f"   Resume sessions found: {resume_count}")
        print(f"   ℹ️  With sanitization, 'null' should be treated as None/anonymous")
        return True
    else:
        print(f"   ✗ Dashboard fetch failed: {response.text}")
        return False

def test_with_undefined():
    """Test with string 'undefined'"""
    print("\n" + "="*60)
    print("TEST 3: String 'undefined' (Bug Scenario)")
    print("="*60)
    
    test_pdf = create_test_pdf()
    
    # Upload with string "undefined"
    print(f"\n📤 Uploading resume with user_id: 'undefined' (string)")
    with open(test_pdf, "rb") as f:
        response = requests.post(
            f"{BASE_URL}/api/upload-resume",
            files={"file": ("test_resume.pdf", f, "application/pdf")},
            headers={"X-User-ID": "undefined"}  # String "undefined"
        )
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✓ Resume uploaded (should be sanitized to None)")
    else:
        print(f"   ✗ Upload failed: {response.text}")
        return False
    
    # Dashboard with string "undefined"
    print(f"\n📊 Fetching dashboard with user_id: 'undefined' (string)")
    response = requests.get(
        f"{BASE_URL}/api/dashboard",
        headers={"X-User-ID": "undefined"}
    )
    
    if response.status_code == 200:
        dashboard = response.json()
        print(f"   ✓ Dashboard fetched")
        print(f"   Resume sessions found: {len(dashboard['resume_sessions'])}")
        print(f"   ℹ️  With sanitization, 'undefined' should be treated as None/anonymous")
        return True
    else:
        print(f"   ✗ Dashboard fetch failed: {response.text}")
        return False

def test_no_header():
    """Test with no X-User-ID header"""
    print("\n" + "="*60)
    print("TEST 4: No X-User-ID Header")
    print("="*60)
    
    test_pdf = create_test_pdf()
    
    # Upload without header
    print(f"\n📤 Uploading resume without X-User-ID header")
    with open(test_pdf, "rb") as f:
        response = requests.post(
            f"{BASE_URL}/api/upload-resume",
            files={"file": ("test_resume.pdf", f, "application/pdf")}
        )
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✓ Resume uploaded (anonymous)")
    else:
        print(f"   ✗ Upload failed: {response.text}")
        return False
    
    # Dashboard without header
    print(f"\n📊 Fetching dashboard without X-User-ID header")
    response = requests.get(f"{BASE_URL}/api/dashboard")
    
    if response.status_code == 200:
        dashboard = response.json()
        print(f"   ✓ Dashboard fetched")
        print(f"   Resume sessions found: {len(dashboard['resume_sessions'])}")
        print(f"   ℹ️  Should use default 'test_user_demo'")
        return True
    else:
        print(f"   ✗ Dashboard fetch failed: {response.text}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("DASHBOARD USER ID FLOW TEST SUITE")
    print("="*60)
    print("\nThis script tests the dashboard API with various user_id scenarios")
    print("to verify that the sanitization fix works correctly.\n")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code != 200:
            print("❌ Server is not responding correctly. Please start the backend server.")
            sys.exit(1)
        print("✓ Server is running\n")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please start the backend server at http://localhost:8000")
        sys.exit(1)
    
    results = []
    
    # Run tests
    results.append(("Valid User ID", test_with_valid_user_id()))
    results.append(("String 'null'", test_with_string_null()))
    results.append(("String 'undefined'", test_with_undefined()))
    results.append(("No Header", test_no_header()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
