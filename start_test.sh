#!/bin/bash
# Simple startup script to avoid shell configuration issues

cd /Users/tony/T-1/T18/agenticSeek

echo "🚀 Starting AgenticSeek API Server..."
echo "📁 Working directory: $(pwd)"
echo "🐍 Python version: $(python3 --version)"

# Start the server
exec python3 api_simple.py
