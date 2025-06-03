#!/usr/bin/env python3
"""
Verification script to test the signal handler fix
"""

import os
import sys
import time
import threading
import requests
from contextlib import contextmanager

# Add current directory to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

@contextmanager
def temporary_server():
    """Context manager to start and stop the server for testing"""
    server_thread = None
    try:
        print("🚀 Starting temporary server for testing...")
        
        # Import uvicorn and the API
        import uvicorn
        import api_simple
        
        # Create a thread to run the server
        def run_server():
            uvicorn.run(api_simple.api, host="127.0.0.1", port=8000, log_level="error")
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        time.sleep(3)
        
        # Check if server is responding
        for attempt in range(5):
            try:
                response = requests.get("http://127.0.0.1:8000/health", timeout=2)
                if response.status_code == 200:
                    print("✅ Server is responding!")
                    yield True
                    return
            except requests.exceptions.RequestException:
                if attempt < 4:
                    print(f"⏳ Attempt {attempt + 1}/5 - waiting for server...")
                    time.sleep(2)
                else:
                    print("❌ Server failed to respond")
                    yield False
                    return
        
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        yield False
    finally:
        print("🛑 Stopping test server...")

def test_signal_handler_fix():
    """Test that the signal handler fix is working"""
    print("\n🧪 Testing Signal Handler Fix")
    print("-" * 30)
    
    # Test 1: Check that signal module is not imported
    try:
        with open('api_simple.py', 'r') as f:
            content = f.read()
        
        if 'import signal' in content:
            print("❌ FAIL: signal module is still imported")
            return False
        else:
            print("✅ PASS: signal module not imported")
    except Exception as e:
        print(f"❌ FAIL: Could not read api_simple.py: {e}")
        return False
    
    # Test 2: Check that signal handler function is removed
    if 'def signal_handler' in content:
        print("❌ FAIL: signal_handler function still exists")
        return False
    else:
        print("✅ PASS: signal_handler function removed")
    
    # Test 3: Check that signal registration is removed
    if 'signal.signal(' in content:
        print("❌ FAIL: signal.signal() calls still exist")
        return False
    else:
        print("✅ PASS: signal.signal() calls removed")
    
    return True

def test_server_connectivity():
    """Test that the server can accept connections"""
    print("\n🧪 Testing Server Connectivity")
    print("-" * 30)
    
    with temporary_server() as server_started:
        if not server_started:
            print("❌ FAIL: Server failed to start")
            return False
        
        # Test health endpoint
        try:
            response = requests.get("http://127.0.0.1:8000/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print("✅ PASS: Health endpoint responding")
                print(f"   Status: {data.get('status', 'unknown')}")
                print(f"   Mode: {data.get('mode', 'unknown')}")
                return True
            else:
                print(f"❌ FAIL: Health endpoint returned status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ FAIL: Could not connect to health endpoint: {e}")
            return False

def test_multiple_requests():
    """Test that the server can handle multiple requests"""
    print("\n🧪 Testing Multiple Requests")
    print("-" * 30)
    
    with temporary_server() as server_started:
        if not server_started:
            print("❌ FAIL: Server failed to start")
            return False
        
        # Send multiple requests
        success_count = 0
        total_requests = 5
        
        for i in range(total_requests):
            try:
                response = requests.get("http://127.0.0.1:8000/health", timeout=2)
                if response.status_code == 200:
                    success_count += 1
                    print(f"✅ Request {i+1}/{total_requests}: Success")
                else:
                    print(f"❌ Request {i+1}/{total_requests}: Failed with status {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"❌ Request {i+1}/{total_requests}: Exception - {e}")
            
            time.sleep(0.5)  # Small delay between requests
        
        if success_count == total_requests:
            print(f"✅ PASS: All {total_requests} requests successful")
            return True
        else:
            print(f"❌ FAIL: Only {success_count}/{total_requests} requests successful")
            return False

def main():
    """Run all verification tests"""
    print("🔍 AgenticSeek Signal Handler Fix Verification")
    print("=" * 50)
    
    tests = [
        ("Signal Handler Fix", test_signal_handler_fix),
        ("Server Connectivity", test_server_connectivity),
        ("Multiple Requests", test_multiple_requests)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} Test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ FAIL: Test crashed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Verification Results Summary")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ The signal handler fix is working correctly")
        print("🚀 Your server should now accept connections properly")
        print("\n💡 To start the server manually:")
        print("   python3 api_simple.py")
        print("\n🔗 Then test with:")
        print("   curl http://localhost:8000/health")
    else:
        print("❌ SOME TESTS FAILED")
        print("🔧 Please check the issues above and fix them")
    
    return all_passed

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Verification cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Verification crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
