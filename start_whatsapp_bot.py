#!/usr/bin/env python3
import subprocess
import sys
import os
import time
from pathlib import Path

def log(message, level="INFO"):
    levels = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
    print(f"{levels.get(level, 'ℹ️')} {message}")

def main():
    log("🚀 Iniciando WhatsApp Bot Management System...")
    
    base_dir = Path(__file__).parent
    os.chdir(base_dir)
    
    # Use virtual environment
    venv_python = base_dir / "venv" / "bin" / "python"
    if not venv_python.exists():
        log("❌ Ambiente virtual não encontrado. Execute: python3 deploy_whatsapp_bot.py", "ERROR")
        sys.exit(1)
    
    try:
        # Start Baileys service in background
        baileys_dir = base_dir / "baileys_service"
        if baileys_dir.exists():
            log("🤖 Iniciando Baileys service...")
            baileys_process = subprocess.Popen(
                ["node", "server.js"], 
                cwd=baileys_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            log("✅ Baileys service iniciado")
            
        # Start FastAPI backend (this will replace the current backend)
        log("🌐 Iniciando WhatsApp Bot backend...")
        
        # The supervisor will restart the backend automatically
        # We just need to ensure our new server.py is in place
        log("✅ Backend configurado (será reiniciado pelo supervisor)")
        
        log("🎉 WhatsApp Bot Management System está pronto!")
        log("🌐 Acesse: http://localhost:3000 (frontend)")
        log("📚 API: http://localhost:8001/api/docs (backend)")
        
    except Exception as e:
        log(f"❌ Erro ao iniciar sistema: {e}", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()
