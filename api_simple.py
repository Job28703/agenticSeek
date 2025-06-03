#!/usr/bin/env python3
"""
Simplified AgenticSeek API for testing improvements
Temporarily disables browser functionality to focus on API improvements
"""

import os
import sys
import uvicorn
import time
from typing import List
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config_validator import validate_startup_config
from sources.logger import Logger

# Validate configuration before starting
print("🚀 Starting AgenticSeek (Simplified Mode)...")
if not validate_startup_config():
    print("❌ Configuration validation failed. Exiting.")
    sys.exit(1)

# Initialize system and global variables
start_time = time.time()  # Track startup time for health check
print("✅ Configuration validated. Initializing simplified system...")

api = FastAPI(title="AgenticSeek API (Simplified)", version="0.1.0")
logger = Logger("backend.log")

api.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not os.path.exists(".screenshots"):
    os.makedirs(".screenshots")
api.mount("/screenshots", StaticFiles(directory=".screenshots"), name="screenshots")

# Global variables
is_generating = False
query_resp_history = []

# Note: Removed custom signal handlers to allow Uvicorn to handle graceful shutdown
# Uvicorn has built-in signal handling that works better with FastAPI applications

@api.get("/screenshot")
async def get_screenshot():
    logger.info("Screenshot endpoint called")
    screenshot_path = ".screenshots/updated_screen.png"
    if os.path.exists(screenshot_path):
        return FileResponse(screenshot_path)
    logger.error("No screenshot available")
    return JSONResponse(
        status_code=404,
        content={"error": "No screenshot available"}
    )

@api.get("/health")
async def health_check():
    """Enhanced health check with detailed system status"""
    try:
        logger.info("Health check endpoint called")
        
        # Check system components
        system_status = {
            "status": "healthy",
            "version": "0.1.0",
            "mode": "simplified",
            "timestamp": time.time(),
            "components": {
                "api": True,
                "logger": logger is not None,
                "query_history_count": len(query_resp_history),
                "is_generating": is_generating,
                "screenshots_dir": os.path.exists(".screenshots")
            },
            "uptime_seconds": time.time() - start_time
        }
        
        return JSONResponse(status_code=200, content=system_status)
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(status_code=503, content={
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        })

@api.get("/is_active")
async def is_active():
    logger.info("Is active endpoint called")
    return {"is_active": not is_generating}

@api.get("/stop")
async def stop():
    logger.info("Stop endpoint called")
    global is_generating
    is_generating = False
    return JSONResponse(status_code=200, content={"status": "stopped"})

@api.get("/latest_answer")
async def get_latest_answer():
    """Get the latest answer from query history with enhanced error handling"""
    try:
        logger.info("Fetching latest answer from history")
        if query_resp_history and len(query_resp_history) > 0:
            latest = query_resp_history[-1]
            logger.info(f"Returning latest answer with UID: {latest.get('uid', 'unknown')}")
            return JSONResponse(status_code=200, content=latest)
        else:
            logger.warning("No answers available in query history")
            return JSONResponse(status_code=404, content={
                "error": "No answers available",
                "message": "Query history is empty. Please submit a query first.",
                "timestamp": time.time()
            })
    except Exception as e:
        logger.error(f"Error fetching latest answer: {str(e)}")
        return JSONResponse(status_code=500, content={
            "error": "Internal server error",
            "message": "Failed to fetch latest answer",
            "timestamp": time.time()
        })

@api.post("/query")
async def process_query(request: dict):
    """Simplified query processing for testing"""
    try:
        logger.info(f"Query endpoint called with: {request}")
        global is_generating, query_resp_history
        
        is_generating = True
        
        # Simulate processing
        import uuid
        response_data = {
            "answer": f"This is a test response to: {request.get('query', 'unknown query')}",
            "reasoning": "This is a simplified test response from the improved API.",
            "agent_name": "TestAgent",
            "status": "completed",
            "uid": str(uuid.uuid4()),
            "timestamp": time.time()
        }
        
        query_resp_history.append(response_data)
        is_generating = False
        
        logger.info(f"Query processed successfully with UID: {response_data['uid']}")
        return JSONResponse(status_code=200, content=response_data)
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        is_generating = False
        return JSONResponse(status_code=500, content={
            "error": "Internal server error",
            "message": "Failed to process query",
            "timestamp": time.time()
        })

print("✅ AgenticSeek (Simplified Mode) is ready!")

if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=8000, reload=False)