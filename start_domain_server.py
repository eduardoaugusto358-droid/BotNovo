#!/usr/bin/env python3
"""
Start WhatsApp Bot on port 8000 for domain access
"""
import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.append(str(Path(__file__).parent))

# Import the FastAPI app from backend
from backend.server import app

if __name__ == "__main__":
    import uvicorn
    print("🌐 Iniciando WhatsApp Bot Management System em http://78.46.250.112:8000")
    print("🚀 Sistema pronto para acesso pelo domínio!")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")