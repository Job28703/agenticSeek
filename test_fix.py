#!/usr/bin/env python3
"""
Test script to verify the signal handler fix
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all imports work correctly"""
    try:
        print("🧪 Testing imports...")
        
        # Test basic imports
        import uvicorn
        print("✅ uvicorn imported successfully")
        
        from fastapi import FastAPI
        print("✅ FastAPI imported successfully")
        
        from config_validator import validate_startup_config
        print("✅ config_validator imported successfully")
        
        from sources.logger import Logger
        print("✅ Logger imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_config_validation():
    """Test configuration validation"""
    try:
        print("\n🧪 Testing configuration validation...")
        from config_validator import validate_startup_config
        result = validate_startup_config()
        print(f"✅ Config validation result: {result}")
        return result
    except Exception as e:
        print(f"❌ Config validation error: {e}")
        return False

def test_signal_handler_fix():
    """Test that signal handlers are not interfering"""
    try:
        print("\n🧪 Testing signal handler fix...")
        
        # Check if signal module is imported in api_simple.py
        with open('api_simple.py', 'r') as f:
            content = f.read()
            
        if 'import signal' in content:
            print("❌ signal module is still imported")
            return False
        
        if 'signal_handler' in content and 'def signal_handler' in content:
            print("❌ signal_handler function still exists")
            return False
            
        if 'signal.signal(' in content:
            print("❌ signal.signal() calls still exist")
            return False
            
        print("✅ Signal handler fix verified - no signal handling code found")
        return True
        
    except Exception as e:
        print(f"❌ Signal handler test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting AgenticSeek Fix Verification Tests")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Config Validation Test", test_config_validation),
        ("Signal Handler Fix Test", test_signal_handler_fix)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        result = test_func()
        results.append((test_name, result))
        
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
            
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests PASSED! The fix is working correctly.")
        print("🚀 You can now start the server with: python3 api_simple.py")
    else:
        print("❌ Some tests FAILED. Please check the issues above.")
        
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
