#!/usr/bin/env python3

import os, sys
import uvicorn
import aiofiles
import configparser
import asyncio
import time
from typing import List
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uuid

from sources.llm_provider import Provider
from sources.interaction import Interaction
from sources.agents import CasualAgent, CoderAgent, FileAgent, PlannerAgent, BrowserAgent
from sources.browser import Browser, create_driver
from sources.utility import pretty_print
from sources.logger import Logger
from sources.schemas import QueryRequest, QueryResponse
from config_validator import validate_startup_config

from celery import Celery

api = FastAPI(title="AgenticSeek API", version="0.1.0")
celery_app = Celery("tasks", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0")
celery_app.conf.update(task_track_started=True)
logger = Logger("backend.log")
config = configparser.ConfigParser()
config.read('config.ini')

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

def initialize_system():
    stealth_mode = config.getboolean('BROWSER', 'stealth_mode')
    personality_folder = "jarvis" if config.getboolean('MAIN', 'jarvis_personality') else "base"
    languages = config["MAIN"]["languages"].split(' ')

    provider = Provider(
        provider_name=config["LLM"]["provider"],
        model=config["LLM"]["model"],
        server_address=config["LLM"]["server_address"],
        is_local=config.getboolean('LLM', 'is_local')
    )
    logger.info(f"Provider initialized: {provider.provider_name} ({provider.model})")

    browser = Browser(
        create_driver(headless=config.getboolean('BROWSER', 'headless_browser'), stealth_mode=stealth_mode, lang=languages[0]),
        anticaptcha_manual_install=stealth_mode
    )
    logger.info("Browser initialized")

    agents = [
        CasualAgent(
            name=config["MAIN"]["agent_name"],
            prompt_path=f"prompts/{personality_folder}/casual_agent.txt",
            provider=provider, verbose=False
        ),
        CoderAgent(
            name="coder",
            prompt_path=f"prompts/{personality_folder}/coder_agent.txt",
            provider=provider, verbose=False
        ),
        FileAgent(
            name="File Agent",
            prompt_path=f"prompts/{personality_folder}/file_agent.txt",
            provider=provider, verbose=False
        ),
        BrowserAgent(
            name="Browser",
            prompt_path=f"prompts/{personality_folder}/browser_agent.txt",
            provider=provider, verbose=False, browser=browser
        ),
        PlannerAgent(
            name="Planner",
            prompt_path=f"prompts/{personality_folder}/planner_agent.txt",
            provider=provider, verbose=False, browser=browser
        )
    ]
    logger.info("Agents initialized")

    interaction = Interaction(
        agents,
        tts_enabled=config.getboolean('MAIN', 'speak'),
        stt_enabled=config.getboolean('MAIN', 'listen'),
        recover_last_session=config.getboolean('MAIN', 'recover_last_session'),
        langs=languages
    )
    logger.info("Interaction initialized")
    return interaction

# Validate configuration before starting
print("🚀 Starting AgenticSeek...")
if not validate_startup_config():
    print("❌ Configuration validation failed. Exiting.")
    sys.exit(1)

# Initialize system and global variables
start_time = time.time()  # Track startup time for health check
print("✅ Configuration validated. Initializing system...")
interaction = initialize_system()
print("✅ AgenticSeek is ready!")
is_generating = False
query_resp_history = []

# Graceful shutdown handler
import signal

def signal_handler(signum, frame):
    """Handle graceful shutdown on SIGTERM/SIGINT"""
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    
    # Stop any running agents
    if interaction and interaction.current_agent:
        try:
            interaction.current_agent.request_stop()
            logger.info("Stopped current agent")
        except Exception as e:
            logger.error(f"Error stopping agent: {e}")
    
    # Close browser if exists
    if interaction and hasattr(interaction, 'browser') and interaction.browser:
        try:
            interaction.browser.quit()
            logger.info("Closed browser")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
    
    logger.info("Graceful shutdown completed")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

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
            "timestamp": time.time(),
            "components": {
                "interaction": interaction is not None,
                "agents": len(interaction.agents) if interaction else 0,
                "browser": hasattr(interaction, 'browser') and interaction.browser is not None if interaction else False,
                "query_history_count": len(query_resp_history),
                "is_generating": is_generating,
                "screenshots_dir": os.path.exists(".screenshots")
            },
            "uptime_seconds": time.time() - start_time if 'start_time' in globals() else 0
        }
        
        # Check if any critical component is missing
        critical_issues = []
        if not system_status["components"]["interaction"]:
            critical_issues.append("Interaction system not initialized")
        if system_status["components"]["agents"] == 0:
            critical_issues.append("No agents available")
            
        if critical_issues:
            system_status["status"] = "degraded"
            system_status["issues"] = critical_issues
            
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
    return {"is_active": interaction.is_active}

@api.get("/stop")
async def stop():
    logger.info("Stop endpoint called")
    interaction.current_agent.request_stop()
    return JSONResponse(status_code=200, content={"status": "stopped"})

@api.get("/latest_answer")
async def get_latest_answer():
    global query_resp_history
    if interaction.current_agent is None:
        return JSONResponse(status_code=404, content={"error": "No agent available"})
    uid = str(uuid.uuid4())
    if not any(q["answer"] == interaction.current_agent.last_answer for q in query_resp_history):
        query_resp = {
            "done": "false",
            "answer": interaction.current_agent.last_answer,
            "reasoning": interaction.current_agent.last_reasoning,
            "agent_name": interaction.current_agent.agent_name if interaction.current_agent else "None",
            "success": interaction.current_agent.success,
            "blocks": {f'{i}': block.jsonify() for i, block in enumerate(interaction.get_last_blocks_result())} if interaction.current_agent else {},
            "status": interaction.current_agent.get_status_message if interaction.current_agent else "No status available",
            "uid": uid
        }
        interaction.current_agent.last_answer = ""
        interaction.current_agent.last_reasoning = ""
        query_resp_history.append(query_resp)
        return JSONResponse(status_code=200, content=query_resp)
    if query_resp_history:
        return JSONResponse(status_code=200, content=query_resp_history[-1])
    return JSONResponse(status_code=404, content={"error": "No answer available"})

async def think_wrapper(interaction, query):
    try:
        interaction.last_query = query
        logger.info("Agents request is being processed")
        success = await interaction.think()
        if not success:
            interaction.last_answer = "Error: No answer from agent"
            interaction.last_reasoning = "Error: No reasoning from agent"
            interaction.last_success = False
        else:
            interaction.last_success = True
        pretty_print(interaction.last_answer)
        interaction.speak_answer()
        return success
    except Exception as e:
        logger.error(f"Error in think_wrapper: {str(e)}")
        interaction.last_answer = f""
        interaction.last_reasoning = f"Error: {str(e)}"
        interaction.last_success = False
        raise e

@api.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    global is_generating, query_resp_history
    logger.info(f"Processing query: {request.query}")
    query_resp = QueryResponse(
        done="false",
        answer="",
        reasoning="",
        agent_name="Unknown",
        success="false",
        blocks={},
        status="Ready",
        uid=str(uuid.uuid4())
    )
    if is_generating:
        logger.warning("Another query is being processed, please wait.")
        return JSONResponse(status_code=429, content=query_resp.jsonify())

    try:
        is_generating = True
        success = await think_wrapper(interaction, request.query)
        is_generating = False

        if not success:
            query_resp.answer = interaction.last_answer
            query_resp.reasoning = interaction.last_reasoning
            return JSONResponse(status_code=400, content=query_resp.jsonify())

        if interaction.current_agent:
            blocks_json = {f'{i}': block.jsonify() for i, block in enumerate(interaction.current_agent.get_blocks_result())}
        else:
            logger.error("No current agent found")
            blocks_json = {}
            query_resp.answer = "Error: No current agent"
            return JSONResponse(status_code=400, content=query_resp.jsonify())

        logger.info(f"Answer: {interaction.last_answer}")
        logger.info(f"Blocks: {blocks_json}")
        query_resp.done = "true"
        query_resp.answer = interaction.last_answer
        query_resp.reasoning = interaction.last_reasoning
        query_resp.agent_name = interaction.current_agent.agent_name
        query_resp.success = str(interaction.last_success)
        query_resp.blocks = blocks_json
        
        query_resp_dict = {
            "done": query_resp.done,
            "answer": query_resp.answer,
            "agent_name": query_resp.agent_name,
            "success": query_resp.success,
            "blocks": query_resp.blocks,
            "status": query_resp.status,
            "uid": query_resp.uid
        }
        query_resp_history.append(query_resp_dict)

        logger.info("Query processed successfully")
        return JSONResponse(status_code=200, content=query_resp.jsonify())
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        sys.exit(1)
    finally:
        logger.info("Processing finished")
        if config.getboolean('MAIN', 'save_session'):
            interaction.save_session()

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

if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=8000)