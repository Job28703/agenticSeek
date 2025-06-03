#!/usr/bin/env python3
"""
AgenticSeek Server Startup Script
Provides a convenient way to start the AgenticSeek API server with proper error handling
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import uvicorn
        import fastapi
        import aiofiles
        print("✅ Core dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return False

def check_redis():
    """Check if Redis is running (for Celery)"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis connection successful")
        return True
    except Exception as e:
        print(f"⚠️  Redis not available: {e}")
        print("Some features may not work without Redis")
        return False

def start_server(host="0.0.0.0", port=8000, reload=False):
    """Start the AgenticSeek API server"""
    print("\n" + "="*50)
    print("🚀 AgenticSeek Server Startup")
    print("="*50)
    
    # Check current directory
    if not os.path.exists("api.py"):
        print("❌ api.py not found. Please run this script from the AgenticSeek directory.")
        return False
        
    # Check dependencies
    if not check_dependencies():
        return False
        
    # Check Redis (optional)
    check_redis()
    
    print(f"\n🌐 Starting server on http://{host}:{port}")
    print("Press Ctrl+C to stop the server\n")
    
    try:
        # Import and run the API
        import uvicorn
        uvicorn.run(
            "api:api",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        return False
        
    return True

def main():
    """Main function with command line argument parsing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Start AgenticSeek API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    parser.add_argument("--dev", action="store_true", help="Development mode (enables reload and localhost only)")
    
    args = parser.parse_args()
    
    # Development mode adjustments
    if args.dev:
        args.reload = True
        args.host = "127.0.0.1"
        print("🔧 Development mode enabled")
    
    # Start the server
    success = start_server(args.host, args.port, args.reload)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()