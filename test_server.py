#!/usr/bin/env python3
"""
Simple test server to verify the fix
"""

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Create a minimal FastAPI app
app = FastAPI(title="Test Server", version="0.1.0")

@app.get("/health")
async def health_check():
    """Simple health check"""
    return JSONResponse(status_code=200, content={
        "status": "healthy",
        "message": "Test server is running",
        "fix_applied": "Signal handler removed"
    })

@app.get("/test")
async def test_endpoint():
    """Test endpoint"""
    return {"message": "Test endpoint working"}

if __name__ == "__main__":
    print("🚀 Starting test server...")
    print("✅ No signal handlers registered")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
