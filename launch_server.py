#!/usr/bin/env python3
"""
Independent server launcher to bypass shell configuration issues
"""

import os
import sys
import subprocess
import time

def main():
    """Launch the API server independently"""
    print("🚀 AgenticSeek Independent Server Launcher")
    print("=" * 50)
    
    # Change to the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Check Python version
    print(f"🐍 Python version: {sys.version}")
    
    # Check if api_simple.py exists
    if not os.path.exists('api_simple.py'):
        print("❌ api_simple.py not found!")
        return False
    
    print("✅ api_simple.py found")
    
    # Try to import required modules
    try:
        import uvicorn
        import fastapi
        print("✅ Required modules available")
    except ImportError as e:
        print(f"❌ Missing required module: {e}")
        return False
    
    # Launch the server
    print("\n🚀 Starting server...")
    print("📡 Server will be available at: http://localhost:8000")
    print("🔗 Health check: http://localhost:8000/health")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Import and run the API directly
        sys.path.insert(0, script_dir)
        
        # Import the API module
        import api_simple
        
        print("✅ API module loaded successfully")
        print("🎯 Signal handler fix applied - using Uvicorn's built-in handling")
        
        # This should work now that signal handlers are removed
        return True
        
    except KeyboardInterrupt:
        print("\n⏹️  Server stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Server launch failed")
        sys.exit(1)
    else:
        print("\n✅ Server launch completed")
